"""Tests for the goalie discovery system."""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from goaliescout.scraping.pipeline.discovery import GoalieDiscovery


class TestGoalieDiscovery(unittest.TestCase):

    def _make_discovery(self, db=None):
        return GoalieDiscovery(db=db, min_games=5, leagues=["ohl"])

    def test_dry_run_no_db(self):
        """Discovery runs without error when no database is attached."""
        discovery = self._make_discovery(db=None)
        discovery._scraper = MagicMock()
        discovery._scraper.get_league_goalies.return_value = [
            {"name": "New Player", "league": "ohl", "team": "Test Team"},
        ]
        new = discovery.run("2023-2024")
        self.assertEqual(len(new), 1)
        self.assertEqual(new[0]["name"], "New Player")

    def test_known_players_excluded(self):
        """Goalies already in the database should not be returned."""
        mock_db = MagicMock()
        mock_db.get_goalie.return_value = object()  # Non-None = found
        discovery = self._make_discovery(db=mock_db)
        discovery._scraper = MagicMock()
        discovery._scraper.get_league_goalies.return_value = [
            {"name": "Known Player", "league": "ohl", "team": "Test Team"},
        ]
        new = discovery.run("2023-2024")
        self.assertEqual(new, [])

    def test_new_players_included(self):
        """Goalies not in the database should be returned."""
        mock_db = MagicMock()
        mock_db.get_goalie.return_value = None  # None = not found
        discovery = self._make_discovery(db=mock_db)
        discovery._scraper = MagicMock()
        discovery._scraper.get_league_goalies.return_value = [
            {"name": "Brand New Player", "league": "ohl", "team": "Test Team"},
        ]
        new = discovery.run("2023-2024")
        self.assertEqual(len(new), 1)

    def test_min_games_filter(self):
        """Goalies below the minimum games threshold are excluded."""
        discovery = self._make_discovery(db=None)
        discovery._scraper = MagicMock()
        discovery._scraper.get_league_goalies.return_value = [
            {"name": "Starter", "league": "ohl", "gp": "20"},
            {"name": "Backup", "league": "ohl", "gp": "2"},  # Below min_games=5
        ]
        new = discovery.run("2023-2024")
        names = [g["name"] for g in new]
        self.assertIn("Starter", names)
        self.assertNotIn("Backup", names)

    def test_scraper_failure_handled(self):
        """A scraper exception should not crash the discovery run."""
        discovery = self._make_discovery(db=None)
        discovery._scraper = MagicMock()
        discovery._scraper.get_league_goalies.side_effect = Exception("Network error")
        new = discovery.run("2023-2024")
        self.assertEqual(new, [])

    def test_multiple_leagues(self):
        """Discovery scans all configured leagues."""
        discovery = GoalieDiscovery(db=None, min_games=1, leagues=["ohl", "whl"])
        discovery._scraper = MagicMock()
        discovery._scraper.get_league_goalies.side_effect = lambda league, season: [
            {"name": f"Player in {league}", "league": league}
        ]
        new = discovery.run("2023-2024")
        leagues_found = {g["league"] for g in new}
        self.assertIn("ohl", leagues_found)
        self.assertIn("whl", leagues_found)

    def test_configured_leagues_from_env(self):
        """DISCOVERY_LEAGUES env var controls the default league list."""
        with patch.dict(os.environ, {"DISCOVERY_LEAGUES": "ncaa,ushl"}):
            from importlib import reload
            import goaliescout.scraping.pipeline.discovery as disc_module
            leagues = disc_module.GoalieDiscovery._configured_leagues()
            self.assertIn("ncaa", leagues)
            self.assertIn("ushl", leagues)


if __name__ == "__main__":
    unittest.main()
