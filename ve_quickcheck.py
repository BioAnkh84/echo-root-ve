# ve_quickcheck_stub.py
# Minimal ledger checker: validates hash chain continuity and psi floor (if provided)
import argparse, json, hashlib, sys

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="ledger.jsonl")
    ap.add_argument("--psi-min", type=float, default=1.38, help="ψ minimum (not enforced unless rho,gamma present)")
    args = ap.parse_args()

    ok = True
    prev_hash = None
    line_num = 0

    with open(args.ledger, "r", encoding="utf-8") as f:
        for line in f:
            line_num += 1
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                print(f"[ERROR] Line {line_num}: invalid JSON: {e}")
                ok = False
                continue

            # Link check
            if prev_hash is not None:
                if obj.get("hash_prev") != prev_hash:
                    print(f"[ERROR] Line {line_num}: hash_prev does not match previous hash_self")
                    ok = False

            # Recompute hash_self from the object without hash_self (use original compressed form if available)
            # For a simple check, hash the object without hash_self, then compare.
            check_obj = {k:v for k,v in obj.items() if k != "hash_self"}
            recomputed = sha256(json.dumps(check_obj, separators=(',',':'), ensure_ascii=False))
            if obj.get("hash_self") != recomputed:
                print(f"[ERROR] Line {line_num}: hash_self mismatch (expected recomputed)")
                ok = False

            prev_hash = obj.get("hash_self")

            # Optional ψ-floor heuristic: treat psi ~ (rho + gamma) for stub only
            if "rho" in obj and "gamma" in obj:
                psi_eff = obj["rho"] + obj["gamma"]
                if psi_eff < args.psi_min:
                    print(f"[WARN] Line {line_num}: ψ_eff (rho+gamma)={psi_eff:.2f} < ψ_min {args.psi_min:.2f}")

    if ok:
        print("[OK] Ledger checks passed (hash continuity + structural).")
        sys.exit(0)
    else:
        print("[FAIL] One or more checks failed.")
        sys.exit(2)

if __name__ == "__main__":
    main()
