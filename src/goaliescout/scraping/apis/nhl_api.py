"""NHL API client using the nhl-api-py package for goalie data retrieval.

This module provides structured access to the official NHL stats API,
including goalie rosters, season stats, game logs, and biographical data.
"""

import logging
import time
from datetime import date
from typing import Any, Dict, List, Optional

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

try:
    from importlib.metadata import version as _pkg_version
    _VERSION = _pkg_version("goaliescout")
except Exception:
    _VERSION = "0"

_USER_AGENT = f"GoalieScout/{_VERSION} (research)"

logger = logging.getLogger(__name__)

# Base URL for the NHL public stats API
_NHL_API_BASE = "https://api-web.nhle.com/v1"
_NHL_STATS_BASE = "https://api.nhle.com/stats/rest/en"


class NHLAPIError(Exception):
    """Raised when the NHL API returns an unexpected response."""


class NHLAPIClient:
    """Client for the NHL public stats API.

    Wraps the free NHL stats API endpoints to retrieve goalie rosters,
    per-season stats, game-by-game logs, biographical data, and today's
    scheduled games.  No API key is required.

    Args:
        delay: Minimum seconds between consecutive requests for polite
            rate limiting.
        timeout: Request timeout in seconds.

    Example::

        client = NHLAPIClient()
        goalies = client.get_all_goalies("20232024")
    """

    _POSITION_CODE = "G"

    def __init__(self, delay: float = 0.5, timeout: int = 15) -> None:
        self.delay = delay
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": _USER_AGENT})

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Issue a GET request with retry logic and rate limiting.

        Args:
            url: Full URL to request.
            params: Optional query-string parameters.

        Returns:
            Parsed JSON payload.

        Raises:
            NHLAPIError: On HTTP errors or malformed responses.
        """
        time.sleep(self.delay)
        return self._get_with_retry(url, params)

    @retry(
        retry=retry_if_exception_type(requests.RequestException),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _get_with_retry(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Internal retry-wrapped GET.

        Args:
            url: Full URL to request.
            params: Optional query-string parameters.

        Returns:
            Parsed JSON payload.

        Raises:
            NHLAPIError: On non-2xx responses.
        """
        try:
            response = self._session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as exc:
            raise NHLAPIError(
                f"NHL API request failed [{exc.response.status_code}]: {url}"
            ) from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_all_goalies(self, season: str) -> List[Dict[str, Any]]:
        """Return all NHL goalies who recorded stats in *season*.

        Args:
            season: Eight-character season identifier such as ``"20232024"``.

        Returns:
            List of goalie dictionaries containing ``playerId``, ``skaterFullName``,
            ``gamesPlayed``, ``wins``, ``losses``, ``otLosses``, ``savePctg``,
            ``goalsAgainstAverage``, and ``shutouts`` keys (among others).

        Raises:
            NHLAPIError: If the API request fails.
        """
        logger.info("Fetching all NHL goalies for season %s", season)
        url = f"{_NHL_STATS_BASE}/goalie/summary"
        all_goalies: List[Dict[str, Any]] = []
        start = 0
        limit = 100

        while True:
            params = {
                "cayenneExp": f"seasonId={season} and gameTypeId=2",
                "start": start,
                "limit": limit,
            }
            try:
                payload = self._get(url, params)
            except NHLAPIError:
                logger.exception("Failed to fetch goalies for season %s", season)
                break

            records: List[Dict[str, Any]] = payload.get("data", [])
            if not records:
                break

            all_goalies.extend(records)
            if len(records) < limit:
                break
            start += limit

        logger.info("Retrieved %d goalies for season %s", len(all_goalies), season)
        return all_goalies

    def get_goalie_stats(self, player_id: int, season: str) -> Dict[str, Any]:
        """Return season summary stats for a specific goalie.

        Args:
            player_id: Numeric NHL player identifier.
            season: Eight-character season string such as ``"20232024"``.

        Returns:
            Dictionary with keys such as ``wins``, ``losses``, ``savePctg``,
            ``goalsAgainstAverage``, ``gamesStarted``, and ``shutouts``.
            Returns an empty dict if no data is found.

        Raises:
            NHLAPIError: If the API request fails.
        """
        logger.info("Fetching stats for player %d, season %s", player_id, season)
        url = f"{_NHL_STATS_BASE}/goalie/summary"
        params = {
            "cayenneExp": (
                f"playerId={player_id} and seasonId={season} and gameTypeId=2"
            ),
            "limit": 1,
        }
        try:
            payload = self._get(url, params)
            records: List[Dict[str, Any]] = payload.get("data", [])
            return records[0] if records else {}
        except NHLAPIError:
            logger.exception(
                "Failed to fetch stats for player %d season %s", player_id, season
            )
            return {}

    def get_game_log(self, player_id: int, season: str) -> List[Dict[str, Any]]:
        """Return game-by-game log for a goalie in a given season.

        Args:
            player_id: Numeric NHL player identifier.
            season: Eight-character season string such as ``"20232024"``.

        Returns:
            List of game log dictionaries with keys such as ``gameDate``,
            ``shotsAgainst``, ``saves``, ``goalsAgainst``, ``savePctg``,
            ``toi``, ``decision``, ``opponentAbbrev``, and ``homeRoadFlag``.

        Raises:
            NHLAPIError: If the API request fails.
        """
        logger.info("Fetching game log for player %d season %s", player_id, season)
        url = f"{_NHL_API_BASE}/player/{player_id}/game-log/{season}/2"
        try:
            payload = self._get(url)
            return payload.get("gameLog", [])
        except NHLAPIError:
            logger.exception(
                "Failed to fetch game log for player %d season %s",
                player_id,
                season,
            )
            return []

    def get_goalie_bio(self, player_id: int) -> Dict[str, Any]:
        """Return biographical information for a player.

        Args:
            player_id: Numeric NHL player identifier.

        Returns:
            Dictionary with biographical keys including ``firstName``,
            ``lastName``, ``birthDate``, ``birthCity``, ``birthCountry``,
            ``heightInInches``, ``weightInPounds``, ``catches``,
            ``draftYear``, ``draftRound``, and ``draftOverall``.

        Raises:
            NHLAPIError: If the API request fails.
        """
        logger.info("Fetching bio for player %d", player_id)
        url = f"{_NHL_API_BASE}/player/{player_id}/landing"
        try:
            payload = self._get(url)
            bio: Dict[str, Any] = {
                "playerId": player_id,
                "firstName": payload.get("firstName", {}).get("default", ""),
                "lastName": payload.get("lastName", {}).get("default", ""),
                "birthDate": payload.get("birthDate", ""),
                "birthCity": payload.get("birthCity", {}).get("default", ""),
                "birthCountry": payload.get("birthCountry", ""),
                "heightInInches": payload.get("heightInInches"),
                "weightInPounds": payload.get("weightInPounds"),
                "catches": payload.get("catches", ""),
                "currentTeamAbbrev": payload.get("currentTeamAbbrev", ""),
                "position": payload.get("position", ""),
                "sweaterNumber": payload.get("sweaterNumber"),
                "draftDetails": payload.get("draftDetails", {}),
            }
            return bio
        except NHLAPIError:
            logger.exception("Failed to fetch bio for player %d", player_id)
            return {}

    def get_todays_games(self) -> List[Dict[str, Any]]:
        """Return today's scheduled NHL games.

        Returns:
            List of game dictionaries containing ``id``, ``gameDate``,
            ``awayTeam``, ``homeTeam``, ``gameState``, and ``startTimeUTC``.
            Returns an empty list if no games are scheduled today.

        Raises:
            NHLAPIError: If the API request fails.
        """
        today = date.today().isoformat()
        logger.info("Fetching today's games (%s)", today)
        url = f"{_NHL_API_BASE}/schedule/{today}"
        try:
            payload = self._get(url)
            game_week: List[Dict[str, Any]] = payload.get("gameWeek", [])
            for day_entry in game_week:
                if day_entry.get("date") == today:
                    return day_entry.get("games", [])
            return []
        except NHLAPIError:
            logger.exception("Failed to fetch today's schedule")
            return []
