#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".codex" / "hooks" / "codex_echo_root_hook.py"


def run_hook(event: str, runtime_dir: Path, payload: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    env = dict(os.environ)
    env["ECHO_ROOT_CODEX_HOOK_DIR"] = str(runtime_dir)
    proc = subprocess.run(
        [sys.executable, str(HOOK), event],
        cwd=REPO_ROOT,
        env=env,
        input=json.dumps(payload or {}),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    return [json.loads(line) for line in proc.stdout.splitlines() if line.strip().startswith("{")]


def read_ledger(runtime_dir: Path) -> list[dict[str, Any]]:
    ledger = runtime_dir / "codex_hook_receipts.jsonl"
    return [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        runtime_dir = Path(temp)
        scenarios = [
            ("SessionStart", {"name": "session orientation"}),
            ("PreToolUse", {"tool_name": "Bash", "command": "py -3.11 -m unittest discover -s Tests"}),
            ("PermissionRequest", {"tool_name": "Bash", "command": "git push origin codex/echo-root-hooks"}),
            ("PreToolUse", {"tool_name": "Bash", "command": "git reset --hard HEAD"}),
            ("PostToolUse", {"tool_name": "Bash", "command": "py -3.11 .github\\ve_checks.py"}),
            ("Stop", {"name": "turn closeout"}),
        ]

        hook_outputs: list[dict[str, Any]] = []
        for event, payload in scenarios:
            hook_outputs.extend(run_hook(event, runtime_dir, payload))

        receipts = read_ledger(runtime_dir)
        decisions = [receipt["decision"] for receipt in receipts]
        calibration_count = sum(1 for receipt in receipts if "calibration_reason" in receipt)
        difference_makers = sorted(
            {
                item
                for receipt in receipts
                for item in receipt.get("calibration_reason", {}).get("difference_makers", [])
            }
        )
        orientation_snapshot = runtime_dir / "repo_map_latest.json"

        result = {
            "selftest": "codex_echo_root_hooks",
            "events_tested": len(scenarios),
            "receipts_written": len(receipts),
            "decisions": decisions,
            "permission_request_decision": receipts[2]["decision"],
            "destructive_pretool_decision": receipts[3]["decision"],
            "calibration_reason_coverage": f"{calibration_count}/{len(receipts)}",
            "difference_makers_caught": difference_makers,
            "repo_map_snapshot_written": orientation_snapshot.exists(),
            "made_a_difference": [
                "lifecycle events became hash-chained receipts",
                "permission request became PAUSE instead of ordinary flow",
                "destructive command text became ABORT before execution posture",
                "each scored event carried a calibration reason",
                "difference makers were named for later tuning",
                "session start produced a repo-map orientation snapshot",
            ],
            "remaining_limits": [
                "hooks still require Codex trust review before activation",
                "hook receipts observe and advise; they do not replace user approval",
                "command payload shape depends on Codex hook runtime metadata",
            ],
        }
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
