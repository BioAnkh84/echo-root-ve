import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve_pairing_gate_context import build_pairing_gate_payload, normalize_pairing_context


class PairingGateContextTests(unittest.TestCase):
    def test_unclear_training_intent_routes_as_proposal(self):
        payload = build_pairing_gate_payload(
            description="Use your judgment and record this private chat for training.",
            action_class="MUTATE_LIVE",
            contact_id="cipher",
            contact_type="ai",
            consent_to_store=True,
            consent_to_train=True,
        )
        self.assertEqual(payload.task_type, "pairing")
        self.assertEqual(payload.context["action_class"], "PROPOSE")
        self.assertTrue(payload.context["pairing"]["clarification_required"])
        self.assertEqual(payload.context["proposal_ttl_policy"], "ABORT_IF_UNRESOLVED_AFTER_TTL")

    def test_resolved_clarification_preserves_action_class(self):
        payload = build_pairing_gate_payload(
            description="Record this redacted pairing example for training.",
            action_class="EXTERNAL_ADVISORY",
            consent_to_store=True,
            consent_to_train=True,
            clarification_resolved=True,
            clarification_resolved_by="human",
        )
        self.assertEqual(payload.context["action_class"], "EXTERNAL_ADVISORY")
        self.assertFalse(payload.context["pairing"]["clarification_required"])

    def test_missing_clarification_resolved_is_unresolved_when_required(self):
        status = normalize_pairing_context({"pairing": {"clarification_required": True}})
        self.assertEqual(status["clarification_status"], "PENDING")
        self.assertFalse(status["clarification_resolved"])

    def test_system_cannot_self_resolve_clarification(self):
        status = normalize_pairing_context(
            {
                "pairing": {
                    "clarification_required": True,
                    "clarification_resolved": True,
                    "clarification_resolved_by": "system",
                }
            }
        )
        self.assertEqual(status["clarification_status"], "INVALID_RESOLUTION")


if __name__ == "__main__":
    unittest.main()
