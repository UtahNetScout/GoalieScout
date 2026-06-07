"""Tests for data normalization utilities."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from goaliescout.scraping.validation.normalization import DataNormalizer


class TestDataNormalizer(unittest.TestCase):

    def setUp(self):
        self.normalizer = DataNormalizer()

    # --- Name normalization ---

    def test_name_strips_accents(self):
        self.assertEqual(self.normalizer.normalize_name("Tuukka Räsänen"), "Tuukka Rasanen")

    def test_name_collapses_whitespace(self):
        self.assertEqual(self.normalizer.normalize_name("  John   Doe  "), "John Doe")

    def test_name_empty_string(self):
        self.assertEqual(self.normalizer.normalize_name(""), "")

    def test_name_preserves_case(self):
        self.assertEqual(self.normalizer.normalize_name("Connor Hellebuyck"), "Connor Hellebuyck")

    # --- League normalization ---

    def test_league_full_name_maps_to_code(self):
        self.assertEqual(self.normalizer.normalize_league("Ontario Hockey League"), "OHL")
        self.assertEqual(self.normalizer.normalize_league("Western Hockey League"), "WHL")
        self.assertEqual(self.normalizer.normalize_league("National Hockey League"), "NHL")

    def test_league_abbreviation_preserved(self):
        self.assertEqual(self.normalizer.normalize_league("OHL"), "OHL")
        self.assertEqual(self.normalizer.normalize_league("NHL"), "NHL")
        self.assertEqual(self.normalizer.normalize_league("NCAA"), "NCAA")

    def test_league_case_insensitive(self):
        self.assertEqual(self.normalizer.normalize_league("ontario hockey league"), "OHL")
        self.assertEqual(self.normalizer.normalize_league("KHL"), "KHL")

    def test_league_unknown_returns_uppercase(self):
        result = self.normalizer.normalize_league("Super Mystery League")
        self.assertTrue(result.isupper() or result)

    def test_league_empty_returns_empty(self):
        self.assertEqual(self.normalizer.normalize_league(""), "")

    # --- Field name normalization ---

    def test_field_gp_maps_to_games_played(self):
        result = self.normalizer.normalize_stat_fields({"GP": 30})
        self.assertIn("games_played", result)
        self.assertEqual(result["games_played"], 30)

    def test_field_svpct_maps_to_save_percentage(self):
        result = self.normalizer.normalize_stat_fields({"SV%": 0.915})
        self.assertIn("save_percentage", result)

    def test_field_gaa_maps_to_goals_against_average(self):
        result = self.normalizer.normalize_stat_fields({"GAA": 2.5})
        self.assertIn("goals_against_average", result)

    def test_unknown_field_preserved(self):
        result = self.normalizer.normalize_stat_fields({"weird_metric": 42})
        self.assertIn("weird_metric", result)

    # --- Unit conversions ---

    def test_height_cm_to_inches(self):
        val = self.normalizer.convert_height(180, "cm", "inches")
        self.assertAlmostEqual(val, 70.9, places=0)

    def test_height_inches_to_cm(self):
        val = self.normalizer.convert_height(74, "inches", "cm")
        self.assertAlmostEqual(val, 187.96, places=0)

    def test_height_same_unit(self):
        val = self.normalizer.convert_height(74, "inches", "inches")
        self.assertEqual(val, 74.0)

    def test_height_unknown_unit(self):
        val = self.normalizer.convert_height(74, "furlongs", "meters")
        self.assertIsNone(val)

    def test_weight_lbs_to_kg(self):
        val = self.normalizer.convert_weight(200, "lbs", "kg")
        self.assertAlmostEqual(val, 90.7, places=0)

    def test_weight_kg_to_lbs(self):
        val = self.normalizer.convert_weight(90, "kg", "lbs")
        self.assertAlmostEqual(val, 198.4, places=0)

    # --- Full record normalization ---

    def test_normalize_record_applies_all(self):
        record = {
            "name": "Tuukka Räsänen",
            "league": "Ontario Hockey League",
            "GP": 30,
            "SV%": 0.915,
        }
        result = self.normalizer.normalize_record(record)
        self.assertEqual(result["name"], "Tuukka Rasanen")
        self.assertEqual(result["league"], "OHL")
        self.assertIn("games_played", result)
        self.assertIn("save_percentage", result)


if __name__ == "__main__":
    unittest.main()
