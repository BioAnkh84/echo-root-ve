import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve_audit_chain import append_audit_record, verify_audit_chain
from ve_deviation_classifier import classify_deviation
from ve_twin_state import load_twin, predicted_delta, update_twin


class MedicalGradeControlTests(unittest.TestCase):
    def test_audit_chain_verifies_and_detects_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "audit.jsonl"
            append_audit_record(path, "GATE_DECISION", "operator", {"decision": "PROPOSE"}, "key")
            append_audit_record(path, "TTL_EXPIRED", "operator", {"decision": "ABORT"}, "key")
            self.assertTrue(verify_audit_chain(path, "key"))
            rows = path.read_text(encoding="utf-8").splitlines()
            item = json.loads(rows[0])
            item["payload"]["decision"] = "PROCEED"
            rows[0] = json.dumps(item)
            path.write_text("\n".join(rows) + "\n", encoding="utf-8")
            self.assertFalse(verify_audit_chain(path, "key"))

    def test_audit_chain_lock_file_is_removed_after_append(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "audit.jsonl"
            append_audit_record(path, "GATE_DECISION", "operator", {"decision": "PROPOSE"}, "key")
            self.assertFalse(path.with_suffix(path.suffix + ".lock").exists())

    def test_ttl_expiry_is_adverse_event(self):
        result = classify_deviation("PROPOSE", "ABORT", ttl_expired=True)
        self.assertEqual(result.classification, "adverse_event")
        self.assertEqual(result.severity, "high")

    def test_propose_to_pause_is_advisory(self):
        result = classify_deviation("PROPOSE", "PAUSE")
        self.assertEqual(result.classification, "advisory")

    def test_twin_updates_baseline_and_reports_delta_gap(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "twin.json"
            update_twin(path, "pairing-1", "PROPOSE", "PAUSE", 0.8, 0.7, 0.2)
            twin = load_twin(path, "pairing-1")
            self.assertEqual(twin.observations, 1)
            self.assertEqual(predicted_delta(twin, 0.5), 0.3)


if __name__ == "__main__":
    unittest.main()
