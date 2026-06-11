from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
HOOK = REPO / ".codex" / "hooks" / "codex_echo_root_hook.py"
BASELINE = REPO / ".codex" / "echo_root_score_baseline.json"


class CodexEchoRootHookTests(unittest.TestCase):
    def run_hook(self, event: str, runtime_dir: Path) -> list[dict]:
        env = dict(os.environ)
        env["ECHO_ROOT_CODEX_HOOK_DIR"] = str(runtime_dir)
        proc = subprocess.run(
            [sys.executable, str(HOOK), event],
            cwd=REPO,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )
        return [json.loads(line) for line in proc.stdout.splitlines() if line.strip().startswith("{")]

    def read_ledger(self, runtime_dir: Path) -> list[dict]:
        ledger = runtime_dir / "codex_hook_receipts.jsonl"
        return [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_session_start_writes_orientation_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            runtime_dir = Path(temp)
            rows = self.run_hook("SessionStart", runtime_dir)

            self.assertTrue((runtime_dir / "codex_hook_receipts.jsonl").exists())
            self.assertTrue((runtime_dir / "repo_map_latest.json").exists())
            self.assertEqual(rows[-1]["event"], "SessionStart")
            self.assertEqual(rows[-1]["boundary"], "Repo map is orientation, not proof.")

    def test_pre_tool_use_defaults_to_pause_posture(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            runtime_dir = Path(temp)
            rows = self.run_hook("PreToolUse", runtime_dir)
            receipts = self.read_ledger(runtime_dir)

            self.assertEqual(rows[-1]["event"], "PreToolUse")
            self.assertEqual(rows[-1]["decision"], "PAUSE")
            self.assertIn("confidence medium/unclear", rows[-1]["reason"])
            calibration = receipts[-1]["calibration_reason"]
            self.assertIn("rho=0.72", calibration["rho"])
            self.assertIn("delta=", calibration["delta"])

    def test_score_baseline_records_lessons_learned(self) -> None:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))

        self.assertIn("Presence is not proof.", baseline["doctrine"])
        self.assertEqual(baseline["event_defaults"]["PermissionRequest"]["delta"], 0.25)
        self.assertIn("Was the action expected?", baseline["feedback_questions"])


if __name__ == "__main__":
    unittest.main()
