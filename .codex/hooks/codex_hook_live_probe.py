#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = REPO_ROOT / "ve_data" / "codex_hooks" / "codex_hook_receipts.jsonl"


def read_receipts(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect live Codex Echo Root hook receipts")
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    parser.add_argument("--before-count", type=int, help="Previous receipt count to compare against")
    args = parser.parse_args()

    ledger = Path(args.ledger)
    receipts = read_receipts(ledger)
    latest = receipts[-1] if receipts else {}
    result = {
        "ledger": str(ledger),
        "receipt_count": len(receipts),
        "live_hook_append_detected": args.before_count is not None and len(receipts) > args.before_count,
        "latest": {
            "decision": latest.get("decision"),
            "reason": latest.get("reason"),
            "tool_name": latest.get("tool_name"),
            "route_id": latest.get("route_id"),
            "hook_metadata": latest.get("hook_metadata"),
            "calibration_reason": latest.get("calibration_reason"),
        },
        "how_to_use": [
            "Run this probe and note receipt_count.",
            "In a fresh trusted Codex session, run one harmless repo command.",
            "Run this probe again with --before-count set to the earlier count.",
            "live_hook_append_detected=true means repo hooks are active.",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
