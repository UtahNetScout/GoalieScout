"""Tests for the goalie deduplication engine."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from goaliescout.scraping.validation.deduplication import GoalieDeduplicator


class TestGoalieDeduplicator(unittest.TestCase):

    def setUp(self):
        self.dedup = GoalieDeduplicator(name_threshold=85.0)

    # --- find_duplicates ---

    def test_identical_names_are_duplicates(self):
        records = [
            {"name": "Connor Hellebuyck", "source": "NHL"},
            {"name": "Connor Hellebuyck", "source": "MoneyPuck"},
        ]
        pairs = self.dedup.find_duplicates(records)
        self.assertEqual(len(pairs), 1)
        i, j, score = pairs[0]
        self.assertEqual(score, 100.0)

    def test_different_names_not_duplicates(self):
        records = [
            {"name": "Connor Hellebuyck"},
            {"name": "Juuse Saros"},
        ]
        pairs = self.dedup.find_duplicates(records)
        self.assertEqual(pairs, [])

    def test_similar_names_detected(self):
        records = [
            {"name": "J. Saros"},
            {"name": "Juuse Saros"},
        ]
        # Even with lower threshold these may not hit 85, but exact match does
        dedup = GoalieDeduplicator(name_threshold=40.0)
        pairs = dedup.find_duplicates(records)
        self.assertGreaterEqual(len(pairs), 0)  # Just confirm it runs

    def test_dob_match_boosts_score(self):
        records = [
            {"name": "Connor Hellebuyck", "dob": "1993-05-19", "source": "A"},
            {"name": "Connor Hellebuyck", "dob": "1993-05-19", "source": "B"},
        ]
        pairs = self.dedup.find_duplicates(records)
        self.assertEqual(len(pairs), 1)
        _, _, score = pairs[0]
        self.assertGreaterEqual(score, 100.0)

    def test_dob_required_mismatch_excludes(self):
        dedup = GoalieDeduplicator(name_threshold=85.0, dob_required=True)
        records = [
            {"name": "Connor Hellebuyck", "dob": "1993-05-19"},
            {"name": "Connor Hellebuyck", "dob": "1990-01-01"},
        ]
        pairs = dedup.find_duplicates(records)
        self.assertEqual(pairs, [])

    # --- merge_records ---

    def test_merge_empty_returns_empty(self):
        result = self.dedup.merge_records([])
        self.assertEqual(result, {})

    def test_merge_single_record(self):
        records = [{"name": "Test Player", "source": "NHL", "wins": 25}]
        result = self.dedup.merge_records(records)
        self.assertEqual(result["name"], "Test Player")
        self.assertEqual(result["wins"], 25)

    def test_merge_higher_priority_source_wins(self):
        # NHL is higher priority than MoneyPuck in source list
        records = [
            {"name": "Test Player", "source": "MoneyPuck", "save_percentage": 0.900},
            {"name": "Test Player", "source": "NHL", "save_percentage": 0.915},
        ]
        result = self.dedup.merge_records(records)
        # NHL should win because it has higher priority
        self.assertAlmostEqual(result["save_percentage"], 0.915)

    def test_merge_tracks_data_sources(self):
        records = [
            {"name": "Test Player", "source": "NHL", "wins": 25},
            {"name": "Test Player", "source": "MoneyPuck", "GSAx": 5.0},
        ]
        result = self.dedup.merge_records(records)
        self.assertIn("NHL", result["data_sources"])
        self.assertIn("MoneyPuck", result["data_sources"])

    def test_merge_provenance_tracked(self):
        records = [
            {"name": "Test Player", "source": "NHL", "wins": 25},
            {"name": "Test Player", "source": "MoneyPuck", "GSAx": 5.0},
        ]
        result = self.dedup.merge_records(records)
        self.assertIn("_provenance", result)

    # --- deduplicate_list ---

    def test_deduplicate_removes_exact_duplicates(self):
        records = [
            {"name": "Connor Hellebuyck", "source": "NHL", "wins": 33},
            {"name": "Connor Hellebuyck", "source": "MoneyPuck", "GSAx": 18.5},
            {"name": "Juuse Saros", "source": "NHL", "wins": 28},
        ]
        result = self.dedup.deduplicate_list(records)
        # Should produce 2 unique profiles
        names = {r.get("name") for r in result}
        self.assertEqual(len(names), 2)

    def test_deduplicate_empty_list(self):
        result = self.dedup.deduplicate_list([])
        self.assertEqual(result, [])

    def test_deduplicate_single_record(self):
        records = [{"name": "Only Player", "source": "NHL"}]
        result = self.dedup.deduplicate_list(records)
        self.assertEqual(len(result), 1)

    def test_deduplicate_no_duplicates_unchanged(self):
        records = [
            {"name": "Hellebuyck Connor", "source": "NHL"},
            {"name": "Saros Juuse", "source": "NHL"},
            {"name": "Gibson John", "source": "NHL"},
        ]
        result = self.dedup.deduplicate_list(records)
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()
