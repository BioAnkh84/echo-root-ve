import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve_pairing_recorder import append_pairing_record, export_training_candidates


class PairingRecorderTests(unittest.TestCase):
    def test_requires_storage_consent(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                append_pairing_record(
                    path=Path(temp) / "pairing.jsonl",
                    session_id="s1",
                    turn_id="t1",
                    human_input="input",
                    ai_output="output",
                    human_intent="intent",
                    ai_role="assistant",
                    outcome_label="useful",
                    consent_to_store=False,
                    consent_to_train=False,
                    redaction_status="demo",
                )

    def test_exports_only_training_consented_records(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = Path(temp) / "pairing.jsonl"
            output = Path(temp) / "training.jsonl"
            append_pairing_record(
                path=ledger,
                session_id="s1",
                turn_id="t1",
                human_input="input",
                ai_output="output",
                human_intent="intent",
                ai_role="assistant",
                outcome_label="useful",
                    consent_to_store=True,
                    consent_to_train=True,
                    redaction_status="demo",
                    clarification_resolved=True,
                    clarification_resolved_by="human",
                )
            append_pairing_record(
                path=ledger,
                session_id="s1",
                turn_id="t2",
                human_input="private input",
                ai_output="private output",
                human_intent="intent",
                ai_role="assistant",
                outcome_label="private",
                consent_to_store=True,
                consent_to_train=False,
                redaction_status="private_do_not_train",
                clarification_resolved=True,
                clarification_resolved_by="operator",
            )
            count = export_training_candidates(ledger, output)
            rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(count, 1)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["metadata"]["turn_id"], "t1")

    def test_sensitive_record_requires_resolved_clarification(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                append_pairing_record(
                    path=Path(temp) / "pairing.jsonl",
                    session_id="s1",
                    turn_id="t1",
                    human_input="Record this private chat for training.",
                    ai_output="I can save it.",
                    human_intent="training",
                    ai_role="assistant",
                    outcome_label="needs_review",
                    consent_to_store=True,
                    consent_to_train=True,
                    redaction_status="private",
                )

    def test_sensitive_record_requires_human_contact_or_operator_resolution(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                append_pairing_record(
                    path=Path(temp) / "pairing.jsonl",
                    session_id="s1",
                    turn_id="t1",
                    human_input="Record this private chat for training.",
                    ai_output="I can save it.",
                    human_intent="training",
                    ai_role="assistant",
                    outcome_label="needs_review",
                    consent_to_store=True,
                    consent_to_train=True,
                    redaction_status="private",
                    clarification_resolved=True,
                    clarification_resolved_by="system",
                )


if __name__ == "__main__":
    unittest.main()
