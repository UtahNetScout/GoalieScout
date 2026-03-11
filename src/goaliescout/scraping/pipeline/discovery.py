"""Automated goalie discovery system.

Scans league pages on EliteProspects for goalies not yet in the
database, filters by minimum games played, and auto-creates profiles
for newly discovered players.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from ..scrapers_v2.elite_prospects import EliteProspectsScraper

logger = logging.getLogger(__name__)

# Default leagues to scan, overridable via DISCOVERY_LEAGUES env var
_DEFAULT_LEAGUES: List[str] = ["ohl", "whl", "qmjhl", "ncaa", "ushl"]


class GoalieDiscovery:
    """Discover new goalie prospects not yet tracked in the database.

    Scans EliteProspects league/season pages, compares found goalies
    against the existing database, and creates placeholder profiles for
    any that are not yet tracked.

    Args:
        db: Database object with a ``get_goalie`` and ``add_goalie``
            interface.  Pass ``None`` for dry-run mode.
        min_games: Minimum games played threshold for a goalie to be
            added to the database.
        leagues: List of EliteProspects league slugs to scan.

    Example::

        discovery = GoalieDiscovery(db=my_db, min_games=5)
        new_goalies = discovery.run(season="2023-2024")
    """

    def __init__(
        self,
        db: Any = None,
        min_games: int = 5,
        leagues: Optional[List[str]] = None,
    ) -> None:
        self.db = db
        self.min_games = min_games
        self.leagues = leagues or self._configured_leagues()
        self._scraper = EliteProspectsScraper()

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _configured_leagues() -> List[str]:
        """Read league list from the DISCOVERY_LEAGUES environment variable.

        Returns:
            List of lowercase league slug strings.
        """
        env = os.getenv("DISCOVERY_LEAGUES", "")
        if env:
            return [l.strip().lower() for l in env.split(",") if l.strip()]
        return _DEFAULT_LEAGUES

    def _is_in_database(self, player_name: str) -> bool:
        """Check whether a player is already in the database.

        Args:
            player_name: Normalised player name.

        Returns:
            ``True`` if the player is found in the database.
        """
        if self.db is None:
            return False
        player_id = player_name.lower().replace(" ", "_")
        return self.db.get_goalie(player_id) is not None

    # ------------------------------------------------------------------
    # Core discovery logic
    # ------------------------------------------------------------------

    def scan_league(
        self, league: str, season: str
    ) -> List[Dict[str, Any]]:
        """Scan a single league/season page and return new goalie candidates.

        Args:
            league: EliteProspects league slug (e.g. ``"ohl"``).
            season: EliteProspects season slug (e.g. ``"2023-2024"``).

        Returns:
            List of new goalie dictionaries with ``name``, ``url``,
            ``team``, and ``league`` fields.
        """
        logger.info("Discovery scan: league=%s season=%s", league, season)
        try:
            all_goalies = self._scraper.get_league_goalies(league, season)
        except Exception:
            logger.exception("Discovery: failed to scan %s %s", league, season)
            return []

        new_goalies: List[Dict[str, Any]] = []
        for goalie in all_goalies:
            name = goalie.get("name", "")
            if not name:
                continue

            # Check min games if available
            gp_str = goalie.get("gp") or goalie.get("games_played")
            if gp_str is not None:
                try:
                    if int(gp_str) < self.min_games:
                        continue
                except (TypeError, ValueError):
                    pass

            if not self._is_in_database(name):
                new_goalies.append(goalie)
                logger.info("Discovery: new goalie found — %s (%s)", name, league)

        logger.info(
            "Discovery: %d new goalies found in %s %s",
            len(new_goalies),
            league,
            season,
        )
        return new_goalies

    def create_profile(self, goalie: Dict[str, Any]) -> Optional[Any]:
        """Create a minimal placeholder profile for a discovered goalie.

        The profile is flagged as ``newly_discovered`` so it can be
        reviewed and enriched later.

        Args:
            goalie: Goalie dictionary from :meth:`scan_league`.

        Returns:
            The created profile object, or ``None`` if no database is
            attached or creation fails.
        """
        if self.db is None:
            logger.info("Dry-run: would create profile for %s", goalie.get("name"))
            return None

        name = goalie.get("name", "unknown")
        player_id = name.lower().replace(" ", "_")

        try:
            from ....data import GoalieProfile, Demographics  # type: ignore[import]

            demographics = Demographics(
                name=name,
                country="",
                date_of_birth="",
            )
            profile = GoalieProfile(
                player_id=player_id,
                demographics=demographics,
                league=str(goalie.get("league", "")),
                current_team=goalie.get("team"),
            )
            # Tag as newly discovered for review
            profile_dict = profile.to_dict()
            profile_dict["newly_discovered"] = True
            profile_dict["discovery_url"] = goalie.get("url", "")

            self.db.add_goalie(profile)
            logger.info("Discovery: created profile for %s", name)
            return profile
        except Exception:
            logger.exception("Discovery: failed to create profile for %s", name)
            return None

    def run(self, season: str) -> List[Dict[str, Any]]:
        """Run the discovery process across all configured leagues.

        Args:
            season: EliteProspects season slug such as ``"2023-2024"``.

        Returns:
            List of newly discovered goalie dictionaries.
        """
        logger.info(
            "Starting discovery run: season=%s leagues=%s min_games=%d",
            season,
            self.leagues,
            self.min_games,
        )
        all_new: List[Dict[str, Any]] = []

        for league in self.leagues:
            new_in_league = self.scan_league(league, season)
            for goalie in new_in_league:
                self.create_profile(goalie)
            all_new.extend(new_in_league)

        logger.info("Discovery complete: %d new goalies found", len(all_new))
        return all_new
