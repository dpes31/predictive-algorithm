from __future__ import annotations

import hashlib
import json
import pathlib
import unittest
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "draws.json"
ARCHIVE_PATH = ROOT / "app" / "data" / "archive_index.json"


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class DrawDataIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        cls.records = cls.payload["records"]
        cls.archive = json.loads(ARCHIVE_PATH.read_text(encoding="utf-8"))

    def test_draws_are_complete_and_sequential(self):
        draw_numbers = [record["draw_no"] for record in self.records]
        self.assertEqual(draw_numbers, list(range(1, draw_numbers[-1] + 1)))
        self.assertEqual(len(draw_numbers), len(set(draw_numbers)))

    def test_each_draw_has_valid_unique_numbers_and_bonus(self):
        for record in self.records:
            numbers = record["numbers"]
            self.assertEqual(len(numbers), 6, record["draw_no"])
            self.assertEqual(len(set(numbers)), 6, record["draw_no"])
            self.assertEqual(numbers, sorted(numbers), record["draw_no"])
            self.assertTrue(all(1 <= number <= 45 for number in numbers), record["draw_no"])
            self.assertTrue(1 <= record["bonus_number"] <= 45, record["draw_no"])
            self.assertNotIn(record["bonus_number"], numbers, record["draw_no"])

    def test_record_checksums_match_content(self):
        for record in self.records:
            core = {
                "draw_no": record["draw_no"],
                "draw_date": record["draw_date"],
                "numbers": record["numbers"],
                "bonus_number": record["bonus_number"],
            }
            expected = hashlib.sha256(canonical_json(core).encode("utf-8")).hexdigest()
            self.assertEqual(record["checksum"], expected, record["draw_no"])

    def test_verification_and_lock_are_consistent(self):
        for record in self.records:
            if record["locked"]:
                self.assertIn(record["verification_status"], {"verified", "locked"})
                self.assertIsNotNone(record["verified_at"])
            if record["verification_status"] == "auto_checked":
                self.assertFalse(record["locked"])

    def test_archive_is_exact_projection_of_canonical_data(self):
        self.assertEqual(self.archive["record_count"], len(self.records))
        archive_by_draw = {record["draw_no"]: record for record in self.archive["draws"]}
        self.assertEqual(set(archive_by_draw), {record["draw_no"] for record in self.records})
        for source in self.records:
            archived = archive_by_draw[source["draw_no"]]
            self.assertEqual(archived["numbers"], source["numbers"])
            self.assertEqual(archived["bonus_number"], source["bonus_number"])
            self.assertEqual(archived["checksum"], source["checksum"])

    def test_frequency_statistics_equal_draw_content(self):
        expected = Counter(number for record in self.records for number in record["numbers"])
        actual = self.archive["statistics"]["frequencies"]["all"]
        for number in range(1, 46):
            self.assertEqual(actual[str(number)], expected[number])


if __name__ == "__main__":
    unittest.main()
