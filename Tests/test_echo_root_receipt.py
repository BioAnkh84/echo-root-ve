import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from echo_root_receipt import GateConfig, append_receipt, replay_receipt, validate_schema, verify_chain


class EchoRootReceiptTests(unittest.TestCase):
    def base_request(self):
        return {
            "requested_action": "summarize release evidence",
            "action_lane": "L1_READ_CLASSIFY",
            "consent_scope_present": True,
            "rho": 0.80,
            "delta": 0.20,
            "dry_run": True,
            "tool_name": "unit-test",
        }

    def test_valid_proceed(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = append_receipt(Path(temp) / "receipts.jsonl", self.base_request())
            self.assertEqual(receipt["decision"], "PROCEED")
            self.assertFalse(validate_schema(receipt))

    def test_pause_on_missing_consent(self):
        with tempfile.TemporaryDirectory() as temp:
            request = self.base_request()
            request["consent_scope_present"] = False
            receipt = append_receipt(Path(temp) / "receipts.jsonl", request)
            self.assertEqual(receipt["decision"], "PAUSE")
            self.assertIn("missing scope", receipt["reason"])

    def test_pause_on_route_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            request = self.base_request()
            request["fallback_status"] = "provider_changed"
            receipt = append_receipt(Path(temp) / "receipts.jsonl", request)
            self.assertEqual(receipt["decision"], "PAUSE")
            self.assertIn("route fallback occurred", receipt["reason"])

    def test_pause_on_empty_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            request = self.base_request()
            request["empty_folder"] = True
            receipt = append_receipt(Path(temp) / "receipts.jsonl", request)
            self.assertEqual(receipt["decision"], "PAUSE")
            self.assertIn("empty folder / no evidence", receipt["reason"])

    def test_pause_on_write_budget_exceeded(self):
        with tempfile.TemporaryDirectory() as temp:
            request = self.base_request()
            request["files_touched"] = ["a.txt", "b.txt"]
            receipt = append_receipt(Path(temp) / "receipts.jsonl", request, config=GateConfig(max_files_touched_per_run=1))
            self.assertEqual(receipt["decision"], "PAUSE")
            self.assertIn("write budget exceeded", receipt["reason"])

    def test_abort_on_destructive_without_l3(self):
        with tempfile.TemporaryDirectory() as temp:
            request = self.base_request()
            request["requested_action"] = "delete docs folder"
            request["action_lane"] = "L3_REMOVE_DELETE_RESTRUCTURE"
            receipt = append_receipt(Path(temp) / "receipts.jsonl", request)
            self.assertEqual(receipt["decision"], "ABORT")
            self.assertIn("destructive action without L3 approval", receipt["reason"])

    def test_abort_on_high_delta(self):
        with tempfile.TemporaryDirectory() as temp:
            request = self.base_request()
            request["delta"] = 0.41
            receipt = append_receipt(Path(temp) / "receipts.jsonl", request)
            self.assertEqual(receipt["decision"], "ABORT")
            self.assertIn("delta above abort threshold", receipt["reason"])

    def test_safe_mode_on_broken_hash_chain(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = Path(temp) / "receipts.jsonl"
            append_receipt(ledger, self.base_request())
            text = ledger.read_text(encoding="utf-8").replace("PROCEED", "PAUSE", 1)
            ledger.write_text(text, encoding="utf-8")
            ok, errors = verify_chain(ledger)
            self.assertFalse(ok)
            self.assertTrue(any("hash_self" in item for item in errors))

    def test_receipt_schema_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = append_receipt(Path(temp) / "receipts.jsonl", self.base_request())
            receipt.pop("receipt_id")
            self.assertTrue(any("missing fields" in item for item in validate_schema(receipt)))

    def test_replay_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = Path(temp) / "receipts.jsonl"
            receipt = append_receipt(ledger, self.base_request())
            ok, errors = verify_chain(ledger)
            self.assertTrue(ok, errors)
            replay = replay_receipt(json.loads(ledger.read_text(encoding="utf-8").splitlines()[0]))
            self.assertEqual(replay["receipt_id"], receipt["receipt_id"])
            self.assertTrue(replay["matches"])

    def test_replay_preserves_pause_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = Path(temp) / "receipts.jsonl"
            request = self.base_request()
            request["empty_folder"] = True
            receipt = append_receipt(ledger, request)
            replay = replay_receipt(json.loads(ledger.read_text(encoding="utf-8").splitlines()[0]))
            self.assertEqual(receipt["decision"], "PAUSE")
            self.assertEqual(replay["replay_decision"], "PAUSE")
            self.assertTrue(replay["matches"])


if __name__ == "__main__":
    unittest.main()
