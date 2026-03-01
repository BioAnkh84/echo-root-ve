#!/usr/bin/env python3
# ve_quickcheck_stub.py
# Minimal ledger checker:
#  - validates hash_prev continuity
#  - recomputes hash_self from stable JSON (excluding hash_self)
#  - Patch posture: tolerates *_bps fields
#  - Compatibility: optional legacy hash fallback (for older ledgers)

import argparse
import json
import hashlib
import sys


def sha256_utf8(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def stable_json(obj) -> str:
    # Patch canonical: UTF-8, compact, no ASCII-forcing
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def legacy_json(obj) -> str:
    # Legacy fallback: compact but ASCII-escaped (common historical default)
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


def as_float(obj, key):
    try:
        return float(obj[key])
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="ledger.jsonl")
    ap.add_argument("--psi-min", type=float, default=1.38, help="ψ minimum warning threshold (stub: rho+gamma)")
    ap.add_argument("--allow-legacy-hash", action="store_true",
                    help="If set, accept legacy hash_self computed with ensure_ascii=True")
    args = ap.parse_args()

    ok = True
    prev_hash = None
    line_num = 0

    try:
        with open(args.ledger, "r", encoding="utf-8") as f:
            for raw_line in f:
                line_num += 1

                line = raw_line.strip().lstrip("\ufeff")
                if not line:
                    continue

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

                # 2) recompute expected hash_self (canonical)
                check_obj = {k: v for k, v in obj.items() if k != "hash_self"}
                canon = stable_json(check_obj)
                recomputed = sha256_utf8(canon)

                if obj.get("hash_self") != recomputed:
                    # Optional legacy fallback
                    if args.allow_legacy_hash:
                        leg = legacy_json(check_obj)
                        recomputed_legacy = sha256_utf8(leg)
                        if obj.get("hash_self") != recomputed_legacy:
                            print(f"[ERROR] Line {line_num}: hash_self mismatch (canonical+legacy)")
                            ok = False
                        else:
                            print(f"[WARN] Line {line_num}: hash_self matches legacy serializer (accepted).")
                    else:
                        print(f"[ERROR] Line {line_num}: hash_self mismatch (canonical). Use --allow-legacy-hash if needed.")
                        ok = False

                prev_hash = obj.get("hash_self")

                # 3) optional ψ-eff warning (stub only)
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
