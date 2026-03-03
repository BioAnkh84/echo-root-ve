# ve_quickcheck.py
# Minimal ledger checker: validates hash chain continuity and psi floor (soft-fail if breached)
import argparse
import json
import hashlib
import sys
from pathlib import Path

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="ledger.jsonl", help="Path to ledger JSONL")
    ap.add_argument("--psi-min", type=float, default=1.38, help="ψ minimum (soft-warn if rho,gamma present)")
    ap.add_argument(
        "--psi-warn-is-softfail",
        action="store_true",
        help="If set, ψ warnings trigger exit code 20 (soft-fail)."
    )
    args = ap.parse_args()

    ledger_path = Path(args.ledger)

    # Exit 10 = environment/missing file
    if not ledger_path.exists():
        print(f"[ENV] Ledger not found: {ledger_path}", file=sys.stderr)
        return 10

    hard_ok = True
    saw_soft_warning = False

    prev_hash = None
    line_num = 0

    try:
        with ledger_path.open("r", encoding="utf-8") as f:
            for line in f:
                line_num += 1
                line = line.strip()
                if not line:
                    continue

                try:
                    obj = json.loads(line)
                except Exception as e:
                    print(f"[ERROR] Line {line_num}: invalid JSON: {e}")
                    hard_ok = False
                    continue

                # Link check
                if prev_hash is not None:
                    if obj.get("hash_prev") != prev_hash:
                        print(f"[ERROR] Line {line_num}: hash_prev does not match previous hash_self")
                        hard_ok = False

                # Recompute hash_self from object excluding hash_self
                check_obj = {k: v for k, v in obj.items() if k != "hash_self"}
                recomputed = sha256(json.dumps(check_obj, separators=(",", ":"), ensure_ascii=False))
                if obj.get("hash_self") != recomputed:
                    print(f"[ERROR] Line {line_num}: hash_self mismatch (expected recomputed)")
                    hard_ok = False

                prev_hash = obj.get("hash_self")

                # Optional ψ-floor heuristic (stub)
                if "rho" in obj and "gamma" in obj:
                    try:
                        psi_eff = float(obj["rho"]) + float(obj["gamma"])
                        if psi_eff < args.psi_min:
                            print(f"[WARN] Line {line_num}: ψ_eff (rho+gamma)={psi_eff:.2f} < ψ_min {args.psi_min:.2f}")
                            saw_soft_warning = True
                    except Exception as e:
                        print(f"[ERROR] Line {line_num}: rho/gamma not numeric: {e}")
                        hard_ok = False

    except Exception as e:
        print(f"[ENV] Failed reading ledger: {e}", file=sys.stderr)
        return 10

    if hard_ok:
        print("[OK] Ledger checks passed (hash continuity + structural).")
        # Exit 20 only if user asked warnings to be soft-fail AND we saw any
        if args.psi_warn_is_softfail and saw_soft_warning:
            print("[SOFT_FAIL] ψ warnings present.")
            return 20
        return 0

    print("[HARD_FAIL] One or more integrity checks failed.")
    return 30

if __name__ == "__main__":
    sys.exit(main())