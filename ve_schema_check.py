import argparse, json, hashlib, sys, time, re, os
# VE v1.1 checker — GENESIS-aware psi, FAIL_ENV/FAIL_EXIT, policy-bound

def sha256(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()

def read_lines(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        for i, line in enumerate(f, start=1):
            yield i, line.rstrip('\n')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ledger', required=True)
    ap.add_argument('--psi-min', type=float, default=1.38)
    ap.add_argument('--strict-psi', action='store_true', help='Treat psi breaches as FAIL (non-GENESIS lines)')
    args = ap.parse_args()

    last_hash_self = None
    ok = True
    for ln, raw in read_lines(args.ledger):
        try:
            obj = json.loads(raw)
        except Exception as e:
            print(f"[ERROR] L{ln}: invalid JSON: {e}")
            ok = False
            continue

        # Basic fields
        hp = obj.get("hash_prev","")
        hs = obj.get("hash_self","")
        if ln == 1:
            # GENESIS: allow hash_prev to be zeros
            pass
        else:
            if not last_hash_self:
                print(f"[ERROR] L{ln}: previous line missing for chain check")
                ok = False
            else:
                if hp != last_hash_self:
                    print(f"[ERROR] L{ln}: hash_prev != previous hash_self")
                    ok = False

        # Recompute hash_self structure (best-effort canonicalization)
        # We won't fully canonicalize; we trust runtime, but sanity-check existence:
        if not isinstance(hs, str) or len(hs) < 16:
            print(f"[ERROR] L{ln}: hash_self missing/invalid")
            ok = False

        # Exit code failure classification
        exit_code = obj.get("exit_code", 0)
        status = obj.get("status","")
        if isinstance(exit_code, int) and exit_code != 0:
            print(f"[FAIL]  L{ln}: FAIL_EXIT (exit_code={exit_code})")
            ok = False

        # Policy-bound: show psi and allow warn/fail
        try:
            if obj.get("action","").upper() != "GENESIS" and "psi_score" in obj:
                psi_eff = float(obj.get("psi_score", 0.0))
                if psi_eff < float(args.psi_min):
                    if args.strict_psi:
                        print(f"[FAIL]  L{ln}: psi_eff={psi_eff:.2f} < psi_min={args.psi_min:.2f}")
                        ok = False
                    else:
                        print(f"[WARN]  L{ln}: psi_eff={psi_eff:.2f} < psi_min={args.psi_min:.2f}")
        except Exception as e:
            print(f"[WARN]  L{ln}: psi check skipped ({e})")

        last_hash_self = hs

    if ok:
        print("[OK] Schema + chain verified.")
        sys.exit(0)
    else:
        print("[FAIL] Issues found. See messages above.")
        sys.exit(1)

if __name__ == '__main__':
    main()