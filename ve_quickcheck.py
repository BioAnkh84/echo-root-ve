import argparse
import json
import hashlib
import sys
from pathlib import Path

def sha256_hex(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def compute_hash(obj):
    payload = {k: v for k, v in obj.items() if k != "hash_self"}
    text = json.dumps(payload, separators=(",", ":"))
    return sha256_hex(text)

def is_genesis(obj):
    return str(obj.get("type","")).upper() == "GENESIS"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--psi-min", type=float, default=1.38)
    ap.add_argument("--psi-warn-is-softfail", action="store_true")
    ap.add_argument("--max-errors", type=int, default=10)
    args = ap.parse_args()

    path = Path(args.ledger)
    if not path.exists():
        print("[ENV] Ledger missing")
        return 10

    prev_hash = None
    psi_warn = False
    errors = 0

    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f,1):
            line=line.strip()
            if not line:
                continue

            try:
                obj=json.loads(line)
            except Exception as e:
                print(f"[ERROR] Line {line_num} invalid JSON")
                errors+=1
                continue

            if prev_hash and obj.get("hash_prev")!=prev_hash:
                print(f"[ERROR] Line {line_num} hash_prev mismatch")
                errors+=1

            if "hash_self" in obj:
                recompute=compute_hash(obj)
                if recompute!=obj["hash_self"]:
                    print(f"[ERROR] Line {line_num} hash_self mismatch")
                    errors+=1

            prev_hash=obj.get("hash_self")

            if not is_genesis(obj):
                if "rho" in obj and "gamma" in obj:
                    psi=float(obj["rho"])+float(obj["gamma"])
                    if psi<args.psi_min:
                        print(f"[WARN] Line {line_num} ψ={psi:.2f} < {args.psi_min}")
                        psi_warn=True

    if errors>0:
        print("[HARD_FAIL] Ledger integrity failure")
        return 30

    print("[OK] Ledger integrity verified")

    if psi_warn and args.psi_warn_is_softfail:
        print("[SOFT_FAIL] ψ warnings present")
        return 20

    return 0

if __name__=="__main__":
    sys.exit(main())
