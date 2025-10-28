#!/usr/bin/env python3
# Minimal VE ledger schema & chain checker
# Usage: python ve_schema_check.py --ledger ve_ledger.jsonl --psi-min 1.38

import argparse, json, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--psi-min", type=float, required=True, dest="psi_min_req")
    args = ap.parse_args()

    required = ["timestamp","event","psi_min","hash_prev","hash_self"]
    zeros64  = "0"*64

    ok = True
    line_num = 0
    prev_hash_self = None

    try:
        with open(args.ledger, "r", encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    # skip blank lines
                    continue
                line_num += 1
                try:
                    obj = json.loads(raw)
                except Exception as e:
                    print(f"ERR line {line_num}: invalid JSON ({e})")
                    ok = False
                    continue

                # required fields
                missing = [k for k in required if k not in obj]
                if missing:
                    print(f"ERR line {line_num}: missing fields {missing}")
                    ok = False
                    continue

                # psi_min gate
                try:
                    psi = float(obj["psi_min"])
                    if psi < args.psi_min_req:
                        print(f"ERR line {line_num}: psi_min {psi} < required {args.psi_min_req}")
                        ok = False
                except Exception:
                    print(f"ERR line {line_num}: psi_min not numeric")
                    ok = False

                # chain linkage
                hp = str(obj["hash_prev"])
                hs = str(obj["hash_self"])
                if len(hp) != 64 or len(hs) != 64:
                    print(f"ERR line {line_num}: hash length must be 64 hex chars")
                    ok = False

                if line_num == 1:
                    if hp != zeros64:
                        print(f"ERR line 1: hash_prev must be {zeros64}")
                        ok = False
                else:
                    if hp != prev_hash_self:
                        print(f"ERR line {line_num}: hash_prev != previous hash_self")
                        ok = False

                prev_hash_self = hs

        if line_num == 0:
            print("ERR: ledger is empty")
            return 2

        if ok:
            print(f"OK: {line_num} valid line(s), psi_min >= requirement, chain linked")
            return 0
        else:
            return 2

    except FileNotFoundError:
        print(f"ERR: ledger not found: {args.ledger}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
