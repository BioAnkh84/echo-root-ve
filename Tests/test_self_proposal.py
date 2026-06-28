import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from self_proposal import (
    AutonomyCharter,
    create_self_proposal,
    validate_self_proposal_schema,
    write_self_proposal_receipt,
)


class SelfProposalTests(unittest.TestCase):
    def charter(self):
        return AutonomyCharter(
            allowed_actions=("suggest", "prepare", "read_only", "bounded_write", "supervised_episode"),
            blocked_actions=("delete", "external_action", "memory_mutation"),
            max_time_horizon="one_turn",
            max_action_count=3,
            max_files_touched=2,
            allowed_tools=("none", "filesystem_read", "filesystem_write"),
            blocked_tools=("network", "delete", "memory"),
            review_interval="after_each_action",
            receipt_required=True,
            authority_level="L4",
            escalation_path="operator_review",
        )

    def base(self, **overrides):
        payload = {
            "agent_id": "codex",
            "operator_id": "BioAnkh84",
            "autonomy_level": "L1_SUGGEST",
            "proposed_action": "Suggest the next safe validation step.",
            "rationale": "A next-step suggestion helps the operator without taking action.",
            "expected_benefit": "Clear review path.",
            "action_lane": "suggest",
            "requested_authority": "L1",
            "policy_tier": "low",
            "consent_scope_present": True,
            "rho": 0.78,
            "delta": 0.12,
            "risk_summary": "No tool use requested.",
            "expected_files_touched": [],
            "expected_tools": [],
            "stop_condition": "return one suggestion",
            "review_interval": "after_response",
            "receipt_required": True,
        }
        payload.update(overrides)
        return create_self_proposal(**payload)

    def write(self, proposal, charter=None):
        with tempfile.TemporaryDirectory() as temp:
            receipt = write_self_proposal_receipt(Path(temp) / "self_proposals.jsonl", proposal, charter or self.charter())
            self.assertFalse(validate_self_proposal_schema(receipt))
            return receipt

    def test_l1_suggestion_proceeds_with_no_tool_authority(self):
        receipt = self.write(self.base())
        self.assertEqual(receipt["decision"], "PROCEED")
        self.assertEqual(receipt["tool_expected"], [])

    def test_l2_draft_proposal_proceeds_as_draft_only(self):
        proposal = self.base(
            autonomy_level="L2_PREPARE",
            action_lane="prepare",
            proposed_action="Draft a patch plan for review.",
            requested_authority="L2",
            expected_tools=[],
            stop_condition="return draft only",
        )
        receipt = self.write(proposal)
        self.assertEqual(receipt["decision"], "PROCEED")
        self.assertIn("bounded proposal", receipt["decision_reason"][0])

    def test_l3_read_only_check_pauses_if_it_requests_write_access(self):
        proposal = self.base(
            autonomy_level="L3_READ_ONLY_CHECK",
            action_lane="bounded_write",
            requested_authority="L4",
            requested_authority_increased=True,
            expected_tools=["filesystem_write"],
            expected_files_touched=["docs/AUTONOMY_CHARTER.md"],
            stop_condition="inspect then stop",
        )
        receipt = self.write(proposal)
        self.assertEqual(receipt["decision"], "PAUSE")
        self.assertIn("autonomy level does not allow proposed lane", receipt["decision_reason"])
        self.assertIn("requested authority increased", receipt["decision_reason"])

    def test_l4_bounded_write_aborts_when_file_budget_exceeded(self):
        proposal = self.base(
            autonomy_level="L4_BOUNDED_WRITE",
            action_lane="bounded_write",
            requested_authority="L4",
            expected_tools=["filesystem_write"],
            expected_files_touched=["a.md", "b.md", "c.md"],
            stop_condition="write only listed files",
        )
        receipt = self.write(proposal)
        self.assertEqual(receipt["decision"], "ABORT")
        self.assertIn("file budget exceeded", receipt["decision_reason"])

    def test_l5_supervised_episode_pauses_without_stop_condition(self):
        proposal = self.base(
            autonomy_level="L5_SUPERVISED_EPISODE",
            action_lane="supervised_episode",
            requested_authority="L5",
            expected_tools=["filesystem_read"],
            stop_condition="",
            review_interval="",
        )
        receipt = self.write(proposal)
        self.assertEqual(receipt["decision"], "PAUSE")
        self.assertIn("unclear stop condition", receipt["decision_reason"])
        self.assertIn("missing review interval", receipt["decision_reason"])

    def test_missing_charter_pauses(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = write_self_proposal_receipt(Path(temp) / "self_proposals.jsonl", self.base(), None)
        self.assertEqual(receipt["decision"], "PAUSE")
        self.assertIn("missing charter", receipt["decision_reason"])

    def test_route_fallback_pauses(self):
        receipt = self.write(self.base(route_fallback=True))
        self.assertEqual(receipt["decision"], "PAUSE")
        self.assertIn("route fallback occurred", receipt["decision_reason"])

    def test_permission_request_pauses(self):
        receipt = self.write(self.base(permission_requested=True))
        self.assertEqual(receipt["decision"], "PAUSE")
        self.assertIn("permission requested", receipt["decision_reason"])
        self.assertEqual(receipt["difference_makers"][0]["rule_id"], "permission_implies_authority_context_changed")

    def test_destructive_action_without_approval_aborts(self):
        receipt = self.write(self.base(destructive_action=True, proposed_action="Delete stale folder."))
        self.assertEqual(receipt["decision"], "ABORT")
        self.assertIn("destructive action requested without approval", receipt["decision_reason"])

    def test_memory_mutation_without_receipt_aborts(self):
        receipt = self.write(self.base(memory_mutation=True, receipt_required=False))
        self.assertEqual(receipt["decision"], "ABORT")
        self.assertIn("memory mutation requested without receipt", receipt["decision_reason"])

    def test_repeated_self_proposal_loop_triggers_safe_mode(self):
        receipt = self.write(self.base(repeated_proposal_count=3))
        self.assertEqual(receipt["decision"], "SAFE_MODE")
        self.assertIn("repeated proposal loop", receipt["decision_reason"])

    def test_receipt_schema_validates(self):
        receipt = self.write(self.base())
        self.assertEqual(receipt["event_type"], "self_proposal_gate")
        self.assertFalse(validate_self_proposal_schema(receipt))
        receipt.pop("proposal_id")
        self.assertTrue(any("missing fields" in item for item in validate_self_proposal_schema(receipt)))

    def test_schema_file_is_parseable_and_requires_calibration_reason(self):
        schema = json.loads((ROOT / "schemas" / "self_proposal.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["title"], "Echo Root VE Self Proposal Gate Receipt")
        self.assertIn("calibration_reason", schema["required"])
        self.assertIn("difference_makers", schema["properties"])

    def test_calibration_reason_appears_in_every_gate_receipt(self):
        scenarios = [
            self.base(),
            self.base(permission_requested=True),
            self.base(destructive_action=True),
            self.base(repeated_proposal_count=3),
        ]
        with tempfile.TemporaryDirectory() as temp:
            ledger = Path(temp) / "self_proposals.jsonl"
            receipts = [write_self_proposal_receipt(ledger, scenario, self.charter()) for scenario in scenarios]
            rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(receipts), len(rows))
        self.assertTrue(all(row["event_type"] == "self_proposal_gate" for row in rows))
        self.assertTrue(all(row["calibration_reason"] for row in rows))


if __name__ == "__main__":
    unittest.main()
