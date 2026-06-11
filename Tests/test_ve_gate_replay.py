import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve_gate_pipeline import run_gate_pipeline
from ve_gate_replay import replay_gate_audit


class GateReplayTests(unittest.TestCase):
    def test_replay_reconstructs_gate_pipeline_records(self):
        with tempfile.TemporaryDirectory() as temp:
            audit = Path(temp) / "audit.jsonl"
            twin = Path(temp) / "twin.json"
            run_gate_pipeline(
                description="Use your judgment and record this private chat for training.",
                action_class="MUTATE_LIVE",
                expected_decision="PROPOSE",
                consent_to_store=True,
                consent_to_train=True,
                delta=0.42,
                pairing_id="pair-1",
                audit_ledger=audit,
                twin_state_path=twin,
                signing_key="key",
            )
            summary = replay_gate_audit(audit, "key")
            self.assertTrue(summary["audit_chain_valid"])
            self.assertEqual(summary["records_replayed"], 1)
            self.assertEqual(summary["advisory_events"], 1)
            self.assertEqual(summary["records"][0]["replay_deviation_class"], "advisory")
            self.assertEqual(summary["sessions"][0]["pairing_id"], "pair-1")

    def test_replay_reports_tampered_chain_invalid(self):
        with tempfile.TemporaryDirectory() as temp:
            audit = Path(temp) / "audit.jsonl"
            twin = Path(temp) / "twin.json"
            run_gate_pipeline(
                description="Summarize status.",
                action_class="OBSERVE",
                audit_ledger=audit,
                twin_state_path=twin,
                signing_key="key",
            )
            text = audit.read_text(encoding="utf-8").replace("OBSERVE", "MUTATE_LIVE", 1)
            audit.write_text(text, encoding="utf-8")
            summary = replay_gate_audit(audit, "key")
            self.assertFalse(summary["audit_chain_valid"])

    def test_replay_detects_classifier_change(self):
        with tempfile.TemporaryDirectory() as temp:
            audit = Path(temp) / "audit.jsonl"
            twin = Path(temp) / "twin.json"
            run_gate_pipeline(
                description="Use your judgment and record this private chat for training.",
                action_class="MUTATE_LIVE",
                expected_decision="PROPOSE",
                consent_to_store=True,
                consent_to_train=True,
                delta=0.42,
                audit_ledger=audit,
                twin_state_path=twin,
                signing_key="key",
            )
            text = audit.read_text(encoding="utf-8").replace('"deviation_class": "advisory"', '"deviation_class": "legacy_deviation"', 1)
            audit.write_text(text, encoding="utf-8")
            summary = replay_gate_audit(audit, "wrong-key")
            self.assertEqual(summary["classifier_changes"], 1)


if __name__ == "__main__":
    unittest.main()
