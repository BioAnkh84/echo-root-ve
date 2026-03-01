#!/usr/bin/env python3
# ve_quickcheck_stub.py
# Minimal ledger checker:
#  - validates hash_prev continuity
#  - recomputes hash_self from stable JSON (excluding hash_self)
#  - optional ψ-eff warning (stub): rho+gamma, prefers *_bps fields when present
#
# Patch posture (v1.0.3): tolerate fixed-point basis points while remaining backwards compatible.

import argparse
import json
import hashlib
import sys


def sha256_utf8(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def as_float(obj, key):
    """Best-effort numeric conversion."""
    try:
        return float(obj[key])
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="ledger.jsonl")
    ap.add_argument("--psi-min", type=float, default=1.38, help="ψ minimum warning threshold (stub: rho+gamma)")
    args = ap.parse_args()

    ok = True
    prev_hash = None
    line_num = 0

    try:
        with open(args.ledger, "r", encoding="utf-8") as f:
            for raw_line in f:
                line_num += 1

                # Strip whitespace and BOM (handles UTF-8 BOM safely)
                line = raw_line.strip().lstrip("\ufeff")
                if not line:
                    continue

                # Parse JSON safely
                try:
                    obj = json.loads(line)
                except Exception as e:
                    print(f"[ERROR] Line {line_num}: invalid JSON: {e}")
                    ok = False
                    continue

                # 1) hash_prev continuity
                if prev_hash is not None and obj.get("hash_prev") != prev_hash:
                    print(f"[ERROR] Line {line_num}: hash_prev does not match previous hash_self")
                    ok = False

                # 2) recompute expected hash_self using stable JSON form (no hash_self)
                check_obj = {k: v for k, v in obj.items() if k != "hash_self"}
                stable = json.dumps(check_obj, separators=(",", ":"), ensure_ascii=False)
                recomputed = sha256_utf8(stable)

                if obj.get("hash_self") != recomputed:
                    print(f"[ERROR] Line {line_num}: hash_self mismatch (expected recomputed)")
                    ok = False

                prev_hash = obj.get("hash_self")

                # 3) optional ψ-eff warning (stub only)
                # Prefer fixed-point basis points if present; else use float fields.
                rho = None
                gamma = None

                if "rho_bps" in obj and "gamma_bps" in obj:
                    rb = as_float(obj, "rho_bps")
                    gb = as_float(obj, "gamma_bps")
                    if rb is not None and gb is not None:
                        rho = rb / 10000.0
                        gamma = gb / 10000.0
                elif "rho" in obj and "gamma" in obj:
                    rho = as_float(obj, "rho")
                    gamma = as_float(obj, "gamma")

                if rho is not None and gamma is not None:
                    psi_eff = rho + gamma
                    if psi_eff < args.psi_min:
                        print(f"[WARN] Line {line_num}: ψ_eff={psi_eff:.2f} < ψ_min {args.psi_min:.2f}")

    except FileNotFoundError:
        print(f"[ERROR] Ledger not found: {args.ledger}")
        return 2
    except Exception as e:
        print(f"[ERROR] Unexpected failure: {e}")
        return 2

    if ok:
        print("[OK] Ledger checks passed (hash continuity + hash_self recomputation).")
        return 0

    print("[FAIL] One or more checks failed.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
