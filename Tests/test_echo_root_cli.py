from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "echo_root_cli.py"


class EchoRootCliTests(unittest.TestCase):
    def run_cli(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=check,
        )

    def test_gate_outputs_decision_without_receipt(self) -> None:
        proc = self.run_cli(
            "gate",
            "--action",
            "read release evidence",
            "--scope",
            "true",
            "--rho",
            "0.82",
            "--delta",
            "0.12",
        )
        data = json.loads(proc.stdout)

        self.assertEqual(data["decision"], "PROCEED")
        self.assertFalse(data["receipt_written"])
        self.assertIn("not execution permission", data["claim_boundary"])

    def test_prove_runs_orientation_receipts_verify_and_replay(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = Path(temp) / "proof.jsonl"
            proc = self.run_cli("--ledger", str(ledger), "prove", "--root", str(REPO), "--depth", "2")
            data = json.loads(proc.stdout)

            self.assertTrue(data["ok"])
            self.assertEqual(data["mode"], "cli_fallback_adapter")
            self.assertEqual(data["decisions"], ["PROCEED", "PAUSE", "ABORT"])
            self.assertTrue(data["verify_chain"]["ok"])
            self.assertTrue(all(row["matches"] for row in data["replay"]))
            self.assertTrue(ledger.exists())
            self.assertIn("MCP is optional", data["mcp_boundary"])


if __name__ == "__main__":
    unittest.main()
