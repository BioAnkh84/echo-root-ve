import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve_habitat_constitution import audit_event
from ve_lessons_ledger import append_lesson, list_lessons
from ve_mission_memory import load_mission, save_mission


class HabitatDoctrineTests(unittest.TestCase):
    def test_constitution_detects_violation(self):
        findings = audit_event({"decision_basis": "context_bypass_gate"})
        violations = [item for item in findings if item.status == "VIOLATION"]
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "context_evidence_not_permission")

    def test_lessons_ledger_filters_by_tag(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "lessons.jsonl"
            append_lesson(
                path,
                incident="Parallel audit writes",
                outcome="Race condition detected",
                fix="Single writer lock",
                lesson="Audit chain integrity depends on serialized writes",
                confidence="verified",
                tags=["audit", "race_condition"],
            )
            self.assertEqual(len(list_lessons(path, "audit")), 1)
            self.assertEqual(len(list_lessons(path, "missing")), 0)

    def test_mission_memory_round_trip(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "mission.json"
            mission = load_mission(path)
            save_mission(path, mission)
            loaded = load_mission(path)
            self.assertIn("Consent first", loaded.constraints)


if __name__ == "__main__":
    unittest.main()
