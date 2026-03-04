# ve_handshake.py
# Purpose: CLI handshake sanity check for VE (supports --input-file; BOM-safe)

import argparse
import json
import sys
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser(description="VE handshake")
    ap.add_argument("--input", default=None, help="JSON payload as string (best-effort)")
    ap.add_argument("--input-file", default=None, help="Path to JSON payload file (recommended)")
    args = ap.parse_args()

    if args.input_file:
        p = Path(args.input_file)
        if not p.exists():
            print(f"[ENV] input-file not found: {p}", file=sys.stderr)
            return 10
        raw = p.read_text(encoding="utf-8-sig", errors="strict").strip()
    else:
        raw = (args.input or "").strip()
        raw = raw.lstrip("\ufeff")

    if not raw:
        print("[ENV] No input provided. Use --input-file (recommended).", file=sys.stderr)
        return 10

    try:
        data = json.loads(raw)
    except Exception as e:
        print("[ERROR] Handshake JSON parse failed.", file=sys.stderr)
        print(f"[ERROR] Raw received: {raw}", file=sys.stderr)
        print(f"[ERROR] {e}", file=sys.stderr)
        return 10

    print(json.dumps({"ok": True, "received": data}, separators=(",", ":"), ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())