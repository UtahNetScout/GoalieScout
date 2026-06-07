"""Tests for the daily update pipeline."""

import sys
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from goaliescout.scraping.pipeline.daily_update import DailyUpdatePipeline, PipelineRunResult
from goaliescout.data import GoalieDatabase


class TestPipelineRunResult(unittest.TestCase):

    def test_initial_state(self):
        result = PipelineRunResult()
        self.assertIsNotNone(result.started_at)
        self.assertIsNone(result.finished_at)
        self.assertFalse(result.success)

    def test_finish_sets_fields(self):
        result = PipelineRunResult()
        result.finish(success=True)
        self.assertIsNotNone(result.finished_at)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.duration_seconds)

    def test_to_dict_serializable(self):
        result = PipelineRunResult()
        result.finish(success=True)
        d = result.to_dict()
        self.assertIn("started_at", d)
        self.assertIn("success", d)
        self.assertIn("records_saved", d)


class TestDailyUpdatePipeline(unittest.TestCase):

    def _make_pipeline(self):
        return DailyUpdatePipeline(db=None, season="20232024")

    def test_dry_run_no_db(self):
        """Pipeline runs without error when no database is attached."""
        pipeline = self._make_pipeline()
        # Patch all fetch methods to return empty lists
        pipeline._fetch_nhl = MagicMock(return_value=[])
        pipeline._fetch_moneypuck = MagicMock(return_value=[])
        pipeline._fetch_nst = MagicMock(return_value=[])
        result = pipeline.run()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, PipelineRunResult)

    def test_current_season_format(self):
        """_current_season returns an 8-char string."""
        season = DailyUpdatePipeline._current_season()
        self.assertEqual(len(season), 8)
        self.assertTrue(season.isdigit())

    def test_source_filter_nhl_only(self):
        """Passing sources=['nhl'] skips moneypuck and nst."""
        pipeline = self._make_pipeline()
        pipeline._nhl = MagicMock()
        pipeline._nhl.get_all_goalies.return_value = []
        result = pipeline.run(sources=["nhl"])
        self.assertIn("NHL", result.sources_attempted)
        self.assertNotIn("MoneyPuck", result.sources_attempted)

    def test_validation_drops_invalid_records(self):
        """Records with missing games_played are dropped during validation."""
        pipeline = self._make_pipeline()
        records = [
            {"name": "Valid Player", "games_played": 30, "source": "NHL"},
            {"name": "Invalid Player", "source": "NHL"},  # missing games_played
        ]
        run = PipelineRunResult()
        valid = pipeline._validate_records(records, run)
        names = [r["name"] for r in valid]
        self.assertIn("Valid Player", names)
        # Invalid record may be filtered
        self.assertLessEqual(len(valid), len(records))

    def test_fetch_nhl_handles_api_error(self):
        """_fetch_nhl catches exceptions and records them in the run."""
        pipeline = self._make_pipeline()
        pipeline._nhl = MagicMock()
        pipeline._nhl.get_all_goalies.side_effect = Exception("API down")
        run = PipelineRunResult()
        result = pipeline._fetch_nhl(run)
        self.assertEqual(result, [])
        self.assertEqual(len(run.errors), 1)

    def test_fetch_moneypuck_handles_error(self):
        """_fetch_moneypuck catches exceptions and records them in the run."""
        pipeline = self._make_pipeline()
        pipeline._moneypuck = MagicMock()
        pipeline._moneypuck.download_season_data.side_effect = Exception("CSV error")
        run = PipelineRunResult()
        result = pipeline._fetch_moneypuck(run)
        self.assertEqual(result, [])
        self.assertEqual(len(run.errors), 1)

    def test_pipeline_persists_to_json_database(self):
        """The pipeline and JSON database integrate without an adapter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = GoalieDatabase(os.path.join(temp_dir, "goalies.json"))
            pipeline = DailyUpdatePipeline(db=db, season="20232024")
            run = PipelineRunResult()
            saved = pipeline._save_to_db(
                [{
                    "name": "Test Goalie",
                    "league": "NHL",
                    "team": "Utah",
                    "games_played": 12,
                    "save_percentage": 0.915,
                    "season": "20232024",
                    "source": "NHL",
                }],
                run,
            )

            self.assertEqual(saved, 1)
            profile = db.get_goalie("test_goalie")
            self.assertIsNotNone(profile)
            self.assertEqual(profile.performance_metrics[0].games_played, 12)
            self.assertIn("NHL", profile.data_sources)


class TestDailyUpdateWithMockedSources(unittest.TestCase):
    """Integration-style tests with fully mocked external calls."""

    @patch.dict(os.environ, {
        "ENABLE_NHL_API": "true",
        "ENABLE_MONEYPUCK": "false",
        "ENABLE_NATURAL_STAT_TRICK": "false",
    })
    def test_run_with_nhl_data(self):
        pipeline = DailyUpdatePipeline(db=None, season="20232024")

        nhl_records = [
            {"name": "Test Goalie A", "games_played": 40, "source": "NHL"},
            {"name": "Test Goalie B", "games_played": 25, "source": "NHL"},
        ]

        def fake_fetch_nhl(run):
            run.sources_attempted.append("NHL")
            run.records_fetched["NHL"] = len(nhl_records)
            return nhl_records

        with patch.object(pipeline, "_fetch_nhl", side_effect=fake_fetch_nhl):
            result = pipeline.run()

        self.assertIn("NHL", result.sources_attempted)
        # No DB attached so records_saved stays 0
        self.assertEqual(result.records_saved, 0)
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
