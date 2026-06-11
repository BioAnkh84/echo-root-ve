import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from repo_map import build_delta_receipt, build_receipt, build_repo_map, build_snapshot, map_hash


class RepoMapTests(unittest.TestCase):
    def test_repo_map_excludes_noise_and_limits_depth(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "src" / "deep").mkdir()
            (root / "src" / "deep" / "skip.py").write_text("skip\n", encoding="utf-8")
            (root / "archive").mkdir()
            (root / "archive" / "old.txt").write_text("old\n", encoding="utf-8")

            entries = build_repo_map(root, depth=2)
            paths = {entry.path for entry in entries}

            self.assertIn("src", paths)
            self.assertIn("src/app.py", paths)
            self.assertIn("src/deep", paths)
            self.assertNotIn("src/deep/skip.py", paths)
            self.assertNotIn("archive/old.txt", paths)

    def test_repo_map_hash_is_deterministic(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "b.txt").write_text("b\n", encoding="utf-8")
            (root / "a.txt").write_text("a\n", encoding="utf-8")

            first = map_hash(build_repo_map(root, depth=1))
            second = map_hash(build_repo_map(root, depth=1))

            self.assertEqual(first, second)

    def test_receipt_records_orientation_not_health_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("# ok\n", encoding="utf-8")
            entries = build_repo_map(root, depth=1)
            receipt = build_receipt(root, 1, entries, set())

            self.assertEqual(receipt["receipt_type"], "repo_map")
            self.assertIn("map_hash", receipt)
            self.assertIn("not proof", receipt["orientation_use"])

    def test_delta_receipt_reports_added_removed_kind_and_size(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "same.txt").write_text("same\n", encoding="utf-8")
            (root / "size.txt").write_text("old\n", encoding="utf-8")
            (root / "removed.txt").write_text("gone\n", encoding="utf-8")
            (root / "kind").write_text("file\n", encoding="utf-8")
            previous = build_snapshot(root, 1, build_repo_map(root, depth=1), set())

            (root / "size.txt").write_text("new-size\n", encoding="utf-8")
            (root / "removed.txt").unlink()
            (root / "added.txt").write_text("new\n", encoding="utf-8")
            (root / "kind").unlink()
            (root / "kind").mkdir()
            current = build_snapshot(root, 1, build_repo_map(root, depth=1), set())

            delta = build_delta_receipt(previous, current)

            self.assertEqual(delta["receipt_type"], "repo_map_delta")
            self.assertIn("added.txt", delta["added"])
            self.assertIn("removed.txt", delta["removed"])
            self.assertEqual(delta["kind_changed"][0]["path"], "kind")
            self.assertEqual(delta["size_changed"][0]["path"], "size.txt")
            self.assertIn("not proof", delta["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
