import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve_contact_registry import Contact, checkin_suggestions, most_recent, record_interaction, upsert_contact


class ContactRegistryTests(unittest.TestCase):
    def test_recent_contacts_are_sorted(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "contacts.jsonl"
            upsert_contact(path, Contact("a", "Alpha", "human", "regular"))
            upsert_contact(path, Contact("b", "Beta", "ai", "regular"))
            record_interaction(path, "a", "2026-01-01T00:00:00+00:00")
            record_interaction(path, "b", "2026-02-01T00:00:00+00:00")
            self.assertEqual(most_recent(path, 1)[0].contact_id, "b")

    def test_suggests_stale_regular_contact(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "contacts.jsonl"
            upsert_contact(
                path,
                Contact(
                    "a",
                    "Alpha",
                    "human",
                    "regular",
                    last_interaction_utc="2026-01-01T00:00:00+00:00",
                ),
            )
            suggestions = checkin_suggestions(path, datetime(2026, 2, 1, tzinfo=timezone.utc))
            self.assertEqual(len(suggestions), 1)
            self.assertTrue(suggestions[0]["ask_human_first"])

    def test_paused_contact_has_no_suggestion(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "contacts.jsonl"
            upsert_contact(path, Contact("a", "Alpha", "human", "paused"))
            self.assertEqual(checkin_suggestions(path), [])


if __name__ == "__main__":
    unittest.main()
