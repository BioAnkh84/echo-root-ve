import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve_gate_pipeline import run_gate_pipeline


class GatePipelineTests(unittest.TestCase):
    def test_pipeline_returns_unified_signed_envelope(self):
        with tempfile.TemporaryDirectory() as temp:
            response = run_gate_pipeline(
                description="Use your judgment and record this private chat for training.",
                action_class="MUTATE_LIVE",
                expected_decision="PROPOSE",
                contact_id="cipher",
                contact_type="ai",
                consent_to_store=True,
                consent_to_train=True,
                delta=0.42,
                pairing_id="pair-1",
                audit_ledger=Path(temp) / "audit.jsonl",
                twin_state_path=Path(temp) / "twin.json",
                signing_key="key",
            )
            self.assertEqual(response["action_class"], "PROPOSE")
            self.assertEqual(response["deviation_class"], "advisory")
            self.assertTrue(response["audit_chain_valid"])
            self.assertIn("audit_record_id", response)
            self.assertIn("twin_delta", response)
            self.assertTrue(response["clarification_required"])

    def test_audit_failure_aborts(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch("ve_gate_pipeline.append_audit_record", side_effect=OSError("disk full")):
                response = run_gate_pipeline(
                    description="Summarize status.",
                    action_class="OBSERVE",
                    audit_ledger=Path(temp) / "audit.jsonl",
                    twin_state_path=Path(temp) / "twin.json",
                    signing_key="key",
                )
            self.assertEqual(response["actual_decision"], "ABORT")
            self.assertTrue(response["audit_fail_closed"])
            self.assertFalse(response["audit_chain_valid"])


if __name__ == "__main__":
    unittest.main()
