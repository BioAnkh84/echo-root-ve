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
            rows = self.run_hook("PreToolUse", Path(temp))

            self.assertEqual(rows[-1]["event"], "PreToolUse")
            self.assertEqual(rows[-1]["decision"], "PAUSE")
            self.assertIn("confidence medium/unclear", rows[-1]["reason"])


if __name__ == "__main__":
    unittest.main()
