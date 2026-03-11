"""Tests for the data validation engine."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from goaliescout.scraping.validation.validators import GoalieDataValidator, ValidationResult


class TestValidationResult(unittest.TestCase):

    def test_default_passes(self):
        result = ValidationResult()
        self.assertTrue(result.passed)
        self.assertTrue(bool(result))

    def test_fail_sets_passed_false(self):
        result = ValidationResult()
        result.fail("Something went wrong", "field_x")
        self.assertFalse(result.passed)
        self.assertIn("Something went wrong", result.errors)
        self.assertEqual(result.field_errors["field_x"], "Something went wrong")

    def test_warn_does_not_fail(self):
        result = ValidationResult()
        result.warn("Unusual value")
        self.assertTrue(result.passed)
        self.assertIn("Unusual value", result.warnings)


class TestGoalieDataValidatorStats(unittest.TestCase):

    def setUp(self):
        self.validator = GoalieDataValidator()

    def test_valid_stats_pass(self):
        stats = {
            "games_played": 40,
            "wins": 25,
            "losses": 10,
            "overtime_losses": 5,
            "save_percentage": 0.915,
            "goals_against_average": 2.50,
            "shutouts": 3,
        }
        result = self.validator.validate_stats(stats)
        self.assertTrue(result.passed)

    def test_missing_games_played_fails(self):
        stats = {"save_percentage": 0.915}
        result = self.validator.validate_stats(stats)
        self.assertFalse(result.passed)
        self.assertIn("games_played", result.field_errors)

    def test_save_percentage_above_1_fails(self):
        stats = {"games_played": 10, "save_percentage": 1.05}
        result = self.validator.validate_stats(stats)
        self.assertFalse(result.passed)

    def test_save_percentage_negative_fails(self):
        stats = {"games_played": 10, "save_percentage": -0.1}
        result = self.validator.validate_stats(stats)
        self.assertFalse(result.passed)

    def test_negative_gaa_fails(self):
        stats = {"games_played": 10, "goals_against_average": -1.0}
        result = self.validator.validate_stats(stats)
        self.assertFalse(result.passed)

    def test_w_l_otl_exceeds_gp_fails(self):
        stats = {"games_played": 10, "wins": 8, "losses": 5, "overtime_losses": 2}
        result = self.validator.validate_stats(stats)
        self.assertFalse(result.passed)

    def test_low_svpct_warns(self):
        stats = {"games_played": 10, "save_percentage": 0.800}
        result = self.validator.validate_stats(stats)
        self.assertTrue(result.passed)
        self.assertTrue(len(result.warnings) > 0)

    def test_non_numeric_stat_fails(self):
        stats = {"games_played": 10, "save_percentage": "not_a_number"}
        result = self.validator.validate_stats(stats)
        self.assertFalse(result.passed)


class TestGoalieDataValidatorBio(unittest.TestCase):

    def setUp(self):
        self.validator = GoalieDataValidator()

    def test_valid_bio_passes(self):
        bio = {
            "name": "Test Player",
            "dob": "1998-05-15",
            "nationality": "Canada",
            "catches": "L",
        }
        result = self.validator.validate_bio(bio)
        self.assertTrue(result.passed)

    def test_missing_name_fails(self):
        bio = {"dob": "1998-05-15"}
        result = self.validator.validate_bio(bio)
        self.assertFalse(result.passed)

    def test_invalid_dob_format_fails(self):
        bio = {"name": "Test Player", "dob": "not-a-date"}
        result = self.validator.validate_bio(bio)
        self.assertFalse(result.passed)

    def test_valid_dob_formats(self):
        for dob_str in ("1998-05-15", "05/15/1998", "May 15, 1998"):
            bio = {"name": "Test Player", "dob": dob_str}
            result = self.validator.validate_bio(bio)
            self.assertTrue(result.passed, f"DOB format failed: {dob_str}")

    def test_unusual_height_warns(self):
        bio = {"name": "Test Player", "height_inches": 50}
        result = self.validator.validate_bio(bio)
        self.assertTrue(result.passed)
        self.assertTrue(len(result.warnings) > 0)

    def test_invalid_catches_warns(self):
        bio = {"name": "Test Player", "catches": "Both"}
        result = self.validator.validate_bio(bio)
        self.assertTrue(len(result.warnings) > 0)


class TestCombinedValidation(unittest.TestCase):

    def setUp(self):
        self.validator = GoalieDataValidator()

    def test_validate_record_combines_errors(self):
        # Missing name (bio error) AND invalid save_pct (stats error)
        record = {"save_percentage": 1.5, "games_played": 5}
        result = self.validator.validate_record(record)
        self.assertFalse(result.passed)
        self.assertTrue(len(result.errors) >= 2)


if __name__ == "__main__":
    unittest.main()
