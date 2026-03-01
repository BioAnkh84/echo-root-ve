#!/usr/bin/env python3
# ve_quickcheck_stub.py
# Minimal ledger checker:
#  - validates hash_prev continuity
#  - recomputes hash_self from stable JSON (excluding hash_self)
#  - Patch posture: tolerates *_bps fields
#  - Compatibility: optional legacy hash fallback + chain-only verification
#  - Derived phase (read-only): no progression mechanics, purely derived from (rho,gamma,delta)

import argparse
import json
import hashlib


def sha256_utf8(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def stable_json(obj) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def legacy_json(obj) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


def as_float(obj, key):
    try:
        return float(obj[key])
    except Exception:
        return None


def get_rgdelta(obj):
    """Return (rho,gamma,delta) as floats if available, preferring *_bps."""
    rho = gamma = delta = None

    if "rho_bps" in obj and "gamma_bps" in obj:
        rb = as_float(obj, "rho_bps")
        gb = as_float(obj, "gamma_bps")
        if rb is not None and gb is not None:
            rho = rb / 10000.0
            gamma = gb / 10000.0

    if "delta_bps" in obj:
        db = as_float(obj, "delta_bps")
        if db is not None:
            delta = db / 10000.0

    if rho is None and "rho" in obj:
        rho = as_float(obj, "rho")
    if gamma is None and "gamma" in obj:
        gamma = as_float(obj, "gamma")
    if delta is None and "delta" in obj:
        delta = as_float(obj, "delta")

    return rho, gamma, delta


def derive_phase(line_num, obj, rho, gamma, delta):
    """Patch v1.0.3 posture: derived state only (no progression)."""
    if obj.get("type") == "GENESIS":
        return "GENESIS" if line_num == 1 else "ANCHOR"

    if rho is None or gamma is None or delta is None:
        return "RED"

    if delta > 0.40:
        return "RED"

    if delta > 0.30:
        return "AMBER"

    if rho < 0.70 or gamma < 0.70:
        if rho >= 0.65 and gamma >= 0.65:
            return "AMBER"
        return "RED"

    return "CLEAR"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="ledger.jsonl")
    ap.add_argument("--psi-min", type=float, default=1.38, help="ψ minimum warning threshold (stub: rho+gamma)")
    ap.add_argument("--allow-legacy-hash", action="store_true",
                    help="If set, accept legacy hash_self computed with ensure_ascii=True")
    ap.add_argument("--chain-only", action="store_true",
                    help="Only validate hash_prev continuity; do not recompute hash_self (compat for non-canonical legacy ledgers)")
    ap.add_argument("--show-phase", action="store_true",
                    help="Print derived phase per line (read-only; no progression mechanics).")
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

                if prev_hash is not None and obj.get("hash_prev") != prev_hash:
                    print(f"[ERROR] Line {line_num}: hash_prev does not match previous hash_self")
                    ok = False

                if args.chain_only:
                    prev_hash = obj.get("hash_self")
                    continue

                check_obj = {k: v for k, v in obj.items() if k != "hash_self"}
                recomputed = sha256_utf8(stable_json(check_obj))

                if obj.get("hash_self") != recomputed:
                    if args.allow_legacy_hash:
                        recomputed_legacy = sha256_utf8(legacy_json(check_obj))
                        if obj.get("hash_self") != recomputed_legacy:
                            print(f"[ERROR] Line {line_num}: hash_self mismatch (canonical+legacy)")
                            ok = False
                        else:
                            print(f"[WARN] Line {line_num}: hash_self matches legacy serializer (accepted).")
                    else:
                        print(f"[ERROR] Line {line_num}: hash_self mismatch (canonical). Use --allow-legacy-hash if needed.")
                        ok = False

                prev_hash = obj.get("hash_self")

                rho, gamma, delta = get_rgdelta(obj)
                if args.show_phase:
                    phase = derive_phase(line_num, obj, rho, gamma, delta)
                    print(f"[PHASE] Line {line_num}: {phase}")

                if obj.get("type") == "GENESIS":
                    continue

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
