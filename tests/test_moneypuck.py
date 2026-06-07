"""Tests for the MoneyPuck CSV client.

Uses mocked HTTP responses with sample CSV data to verify download,
parsing, and query methods without real network calls.
"""

import io
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from goaliescout.scraping.apis.moneypuck import MoneyPuckClient, MoneyPuckError

_SAMPLE_CSV = (
    "name,team,situation,icetime,xGoals,goalsAllowed,savedShotsOnGoal,GSAx,xGoalsPercentage\n"
    "Connor Hellebuyck,WPG,all,3200,98.5,80,2180,18.5,0.551\n"
    "Connor Hellebuyck,WPG,highDanger,400,30.0,28,320,-2.0,0.490\n"
    "Connor Hellebuyck,WPG,mediumDanger,1000,35.0,28,800,7.0,0.520\n"
    "Connor Hellebuyck,WPG,lowDanger,1800,33.5,24,1060,9.5,0.580\n"
    "Juuse Saros,NSH,all,2800,110.0,95,2050,15.0,0.535\n"
    "Juuse Saros,NSH,highDanger,380,28.0,30,300,-2.0,0.480\n"
)


def _mock_csv_response(csv_text: str) -> MagicMock:
    mock = MagicMock()
    mock.status_code = 200
    mock.text = csv_text
    mock.raise_for_status = MagicMock()
    return mock


class TestMoneyPuckClient(unittest.TestCase):

    def setUp(self):
        self.client = MoneyPuckClient()

    @patch("goaliescout.scraping.apis.moneypuck.requests.Session.get")
    def test_download_season_data_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_csv_response(_SAMPLE_CSV)
        df = self.client.download_season_data("2023")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        self.assertIn("name", df.columns)

    @patch("goaliescout.scraping.apis.moneypuck.requests.Session.get")
    def test_download_caches_result(self, mock_get):
        """Second call for the same season should not make another HTTP request."""
        mock_get.return_value = _mock_csv_response(_SAMPLE_CSV)
        self.client.download_season_data("2023")
        self.client.download_season_data("2023")
        self.assertEqual(mock_get.call_count, 1)

    @patch("goaliescout.scraping.apis.moneypuck.requests.Session.get")
    def test_get_goalie_gsax_found(self, mock_get):
        mock_get.return_value = _mock_csv_response(_SAMPLE_CSV)
        result = self.client.get_goalie_gsax("Connor Hellebuyck", "2023")
        self.assertEqual(result["name"], "Connor Hellebuyck")
        self.assertAlmostEqual(result["GSAx"], 18.5)

    @patch("goaliescout.scraping.apis.moneypuck.requests.Session.get")
    def test_get_goalie_gsax_not_found(self, mock_get):
        mock_get.return_value = _mock_csv_response(_SAMPLE_CSV)
        result = self.client.get_goalie_gsax("Unknown Player", "2023")
        self.assertEqual(result, {})

    @patch("goaliescout.scraping.apis.moneypuck.requests.Session.get")
    def test_get_all_goalie_rankings(self, mock_get):
        mock_get.return_value = _mock_csv_response(_SAMPLE_CSV)
        df = self.client.get_all_goalie_rankings("2023")
        self.assertIsInstance(df, pd.DataFrame)
        # Should be sorted by GSAx descending
        if len(df) > 1 and "GSAx" in df.columns:
            self.assertGreaterEqual(df.iloc[0]["GSAx"], df.iloc[1]["GSAx"])
        self.assertIn("rank", df.columns)
        self.assertEqual(df.iloc[0]["rank"], 1)

    @patch("goaliescout.scraping.apis.moneypuck.requests.Session.get")
    def test_get_shot_quality_data(self, mock_get):
        mock_get.return_value = _mock_csv_response(_SAMPLE_CSV)
        result = self.client.get_shot_quality_data("Connor Hellebuyck", "2023")
        self.assertIn("highDanger", result)
        self.assertIn("mediumDanger", result)
        self.assertIn("lowDanger", result)


if __name__ == "__main__":
    unittest.main()
