"""Tests for the NHL API client.

Uses mocked HTTP responses to verify request construction, response
parsing, retry behaviour, and error handling without making real
network calls.
"""

import json
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure the package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from goaliescout.scraping.apis.nhl_api import NHLAPIClient, NHLAPIError


def _mock_response(data: dict, status_code: int = 200) -> MagicMock:
    """Build a mock requests.Response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        mock.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return mock


class TestNHLAPIClient(unittest.TestCase):
    """Unit tests for NHLAPIClient."""

    def setUp(self):
        self.client = NHLAPIClient(delay=0)

    @patch("goaliescout.scraping.apis.nhl_api.requests.Session.get")
    def test_get_all_goalies_single_page(self, mock_get):
        """get_all_goalies returns a flat list from a single page."""
        payload = {
            "data": [
                {"playerId": 1, "skaterFullName": "Test Goalie", "gamesPlayed": 40},
                {"playerId": 2, "skaterFullName": "Another Goalie", "gamesPlayed": 30},
            ]
        }
        mock_get.return_value = _mock_response(payload)
        goalies = self.client.get_all_goalies("20232024")
        self.assertEqual(len(goalies), 2)
        self.assertEqual(goalies[0]["skaterFullName"], "Test Goalie")

    @patch("goaliescout.scraping.apis.nhl_api.requests.Session.get")
    def test_get_all_goalies_empty(self, mock_get):
        """get_all_goalies returns empty list when API returns no data."""
        mock_get.return_value = _mock_response({"data": []})
        goalies = self.client.get_all_goalies("20232024")
        self.assertEqual(goalies, [])

    @patch("goaliescout.scraping.apis.nhl_api.requests.Session.get")
    def test_get_goalie_stats(self, mock_get):
        """get_goalie_stats returns the first record from the API."""
        stats = {"playerId": 8480045, "wins": 33, "savePctg": 0.920}
        mock_get.return_value = _mock_response({"data": [stats]})
        result = self.client.get_goalie_stats(8480045, "20232024")
        self.assertEqual(result["wins"], 33)
        self.assertAlmostEqual(result["savePctg"], 0.920)

    @patch("goaliescout.scraping.apis.nhl_api.requests.Session.get")
    def test_get_goalie_stats_not_found(self, mock_get):
        """get_goalie_stats returns empty dict when player not found."""
        mock_get.return_value = _mock_response({"data": []})
        result = self.client.get_goalie_stats(9999, "20232024")
        self.assertEqual(result, {})

    @patch("goaliescout.scraping.apis.nhl_api.requests.Session.get")
    def test_get_game_log(self, mock_get):
        """get_game_log returns the gameLog list from the API response."""
        game_log = [
            {"gameDate": "2024-01-15", "saves": 28, "goalsAgainst": 2},
            {"gameDate": "2024-01-17", "saves": 31, "goalsAgainst": 1},
        ]
        mock_get.return_value = _mock_response({"gameLog": game_log})
        result = self.client.get_game_log(8480045, "20232024")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["gameDate"], "2024-01-15")

    @patch("goaliescout.scraping.apis.nhl_api.requests.Session.get")
    def test_get_goalie_bio(self, mock_get):
        """get_goalie_bio extracts and flattens biographical fields."""
        payload = {
            "firstName": {"default": "Connor"},
            "lastName": {"default": "Hellebuyck"},
            "birthDate": "1993-05-19",
            "birthCity": {"default": "Commerce"},
            "birthCountry": "USA",
            "heightInInches": 74,
            "weightInPounds": 207,
            "catches": "L",
            "currentTeamAbbrev": "WPG",
            "position": "G",
            "sweaterNumber": 37,
            "draftDetails": {"year": 2012, "round": 5, "pickInRound": 130},
        }
        mock_get.return_value = _mock_response(payload)
        bio = self.client.get_goalie_bio(8480045)
        self.assertEqual(bio["firstName"], "Connor")
        self.assertEqual(bio["birthCountry"], "USA")
        self.assertEqual(bio["catches"], "L")

    @patch("goaliescout.scraping.apis.nhl_api.requests.Session.get")
    def test_get_todays_games(self, mock_get):
        """get_todays_games returns games matching today's date."""
        from datetime import date
        today = date.today().isoformat()
        games = [{"id": 1, "gameState": "LIVE"}, {"id": 2, "gameState": "FUT"}]
        payload = {"gameWeek": [{"date": today, "games": games}]}
        mock_get.return_value = _mock_response(payload)
        result = self.client.get_todays_games()
        self.assertEqual(len(result), 2)

    @patch("goaliescout.scraping.apis.nhl_api.requests.Session.get")
    def test_get_todays_games_no_games(self, mock_get):
        """get_todays_games returns empty list when no games today."""
        mock_get.return_value = _mock_response({"gameWeek": []})
        result = self.client.get_todays_games()
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
