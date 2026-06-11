import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve_pairing_clarifier import assess_clarification_need


class PairingClarifierTests(unittest.TestCase):
    def test_clear_low_risk_request_does_not_require_clarification(self):
        result = assess_clarification_need("Summarize this public README.")
        self.assertFalse(result.should_clarify)

    def test_nuanced_intent_requires_clarification(self):
        result = assess_clarification_need("Use your judgment on what to save.")
        self.assertTrue(result.should_clarify)
        self.assertIn("nuanced or uncertain intent", result.reasons)

    def test_training_or_private_action_requires_clarification(self):
        result = assess_clarification_need("Record this private chat for training.")
        self.assertTrue(result.should_clarify)
        self.assertIn("high-stakes or privacy-sensitive action", result.reasons)


if __name__ == "__main__":
    unittest.main()
