import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve_gate_pipeline import run_gate_pipeline
from ve_replay_report import write_replay_report


class ReplayReportTests(unittest.TestCase):
    def test_writes_html_and_markdown_reports(self):
        with tempfile.TemporaryDirectory() as temp:
            audit = Path(temp) / "audit.jsonl"
            twin = Path(temp) / "twin.json"
            html = Path(temp) / "report.html"
            markdown = Path(temp) / "report.md"
            run_gate_pipeline(
                description="Use your judgment and record this private chat for training.",
                action_class="MUTATE_LIVE",
                expected_decision="PROPOSE",
                consent_to_store=True,
                consent_to_train=True,
                delta=0.42,
                pairing_id="cipher-richard",
                audit_ledger=audit,
                twin_state_path=twin,
                signing_key="key",
            )
            summary = write_replay_report(audit, html, markdown, "key")
            self.assertTrue(summary["audit_chain_valid"])
            self.assertIn("VE Gate Replay Report", html.read_text(encoding="utf-8"))
            self.assertIn("cipher-richard", markdown.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
