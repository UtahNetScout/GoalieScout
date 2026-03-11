"""Natural Stat Trick advanced goalie splits client.

Natural Stat Trick provides free advanced hockey statistics including
high/medium/low danger save percentages, 5v5/PP/PK situational splits,
Goals Saved Above Average (GSAA), and rebound rates for NHL goalies.
"""

import io
import logging
import time
from typing import Any, Dict, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
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

_NST_BASE = "https://www.naturalstattrick.com"
_NST_GOALIE_URL = "{base}/goaliestats.php"


class NaturalStatTrickError(Exception):
    """Raised when a Natural Stat Trick request fails."""


class NaturalStatTrickClient:
    """Client for Natural Stat Trick advanced goalie statistics.

    Retrieves goalie split statistics from Natural Stat Trick, including
    high/medium/low danger zone save percentages, situational splits
    (5v5, PP, PK), and GSAA.

    Args:
        delay: Seconds to wait between requests.
        timeout: HTTP request timeout in seconds.

    Example::

        client = NaturalStatTrickClient()
        df = client.get_goalie_splits("20232024")
        hd_df = client.get_danger_zone_stats("20232024")
    """

    def __init__(self, delay: float = 2.0, timeout: int = 30) -> None:
        self.delay = delay
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": _USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        })
        self._cache: Dict[str, pd.DataFrame] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @retry(
        retry=retry_if_exception_type(requests.RequestException),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _fetch(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Fetch raw HTML from *url* with retry logic.

        Args:
            url: Target URL.
            params: Optional query parameters.

        Returns:
            Response text (HTML).

        Raises:
            NaturalStatTrickError: On HTTP errors.
        """
        time.sleep(self.delay)
        try:
            response = self._session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.HTTPError as exc:
            raise NaturalStatTrickError(
                f"NST request failed [{exc.response.status_code}]: {url}"
            ) from exc

    def _parse_goalie_table(self, html: str) -> pd.DataFrame:
        """Extract the first stats table from an NST HTML response.

        Args:
            html: Raw HTML string from Natural Stat Trick.

        Returns:
            :class:`pandas.DataFrame` of the parsed stats table, or an
            empty DataFrame if no table is found.
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", {"id": "players"}) or soup.find("table")
        if table is None:
            logger.warning("No stats table found in Natural Stat Trick response")
            return pd.DataFrame()

        try:
            dfs = pd.read_html(io.StringIO(str(table)))
            return dfs[0] if dfs else pd.DataFrame()
        except Exception as exc:
            logger.error("Failed to parse NST table: %s", exc)
            return pd.DataFrame()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_goalie_splits(
        self, season: str, situation: str = "5v5"
    ) -> pd.DataFrame:
        """Return goalie stats for a given season and situation.

        Args:
            season: Eight-character season identifier such as
                ``"20232024"``.
            situation: Game situation filter. Common values are
                ``"5v5"``, ``"pp"``, ``"pk"``, and ``"all"``.

        Returns:
            :class:`pandas.DataFrame` with one row per goalie, containing
            columns such as ``Player``, ``Team``, ``GP``, ``TOI``,
            ``SV%``, ``GAA``, ``GSAA``, and ``xGAA``.

        Raises:
            NaturalStatTrickError: If the request fails.
        """
        cache_key = f"{season}_{situation}"
        if cache_key in self._cache:
            return self._cache[cache_key].copy()

        logger.info("Fetching NST goalie splits: season=%s situation=%s", season, situation)
        url = _NST_GOALIE_URL.format(base=_NST_BASE)

        # Map situation parameter to NST's sit= query value
        sit_map = {
            "5v5": "5v5",
            "pp": "pp",
            "pk": "pk",
            "all": "all",
            "4v5": "4v5",
            "5v4": "5v4",
            "ev": "ev",
        }
        sit_param = sit_map.get(situation.lower(), situation.lower())

        params = {
            "sit": sit_param,
            "score": "all",
            "stdoi": "g",
            "rate": "n",
            "team": "all",
            "pos": "G",
            "loc": "B",
            "toi": "0",
            "stype": "2",
            "fromseason": season,
            "thruseason": season,
        }

        try:
            html = self._fetch(url, params)
            df = self._parse_goalie_table(html)
            self._cache[cache_key] = df
            logger.info(
                "Retrieved %d goalies from NST season=%s situation=%s",
                len(df),
                season,
                situation,
            )
            return df.copy()
        except NaturalStatTrickError:
            logger.exception("Failed to fetch NST splits season=%s situation=%s", season, situation)
            return pd.DataFrame()

    def get_danger_zone_stats(self, season: str) -> pd.DataFrame:
        """Return high/medium/low danger zone statistics for all goalies.

        Args:
            season: Eight-character season identifier such as
                ``"20232024"``.

        Returns:
            :class:`pandas.DataFrame` containing danger-zone shot and
            save data with columns for ``HDSV%``, ``MDSV%``, ``LDSV%``,
            ``HDSOG``, ``MDSOG``, ``LDSOG``, and ``Player``.  Returns an
            empty DataFrame on failure.
        """
        cache_key = f"{season}_danger"
        if cache_key in self._cache:
            return self._cache[cache_key].copy()

        logger.info("Fetching NST danger zone stats for season %s", season)
        url = _NST_GOALIE_URL.format(base=_NST_BASE)
        params = {
            "sit": "all",
            "score": "all",
            "stdoi": "oi",
            "rate": "n",
            "team": "all",
            "pos": "G",
            "loc": "B",
            "toi": "0",
            "stype": "2",
            "fromseason": season,
            "thruseason": season,
        }

        try:
            html = self._fetch(url, params)
            df = self._parse_goalie_table(html)
            self._cache[cache_key] = df
            return df.copy()
        except NaturalStatTrickError:
            logger.exception("Failed to fetch NST danger zone stats for season %s", season)
            return pd.DataFrame()

    def get_individual_goalie(
        self, player_name: str, season: str
    ) -> Dict[str, Any]:
        """Return detailed splits for a single goalie.

        Fetches the all-situations split data and filters to the named
        goalie.

        Args:
            player_name: Full player name as it appears in NST data
                (e.g. ``"Connor Hellebuyck"``).
            season: Eight-character season identifier.

        Returns:
            Dictionary mapping situation labels (``"5v5"``, ``"pp"``,
            ``"pk"``) to the corresponding row dict of stats for that
            goalie.  Returns an empty dict if the goalie is not found in
            any situation.
        """
        result: Dict[str, Any] = {}
        name_lower = player_name.lower()

        for situation in ("5v5", "pp", "pk", "all"):
            df = self.get_goalie_splits(season, situation)
            if df.empty:
                continue

            # Try to find the player column (may be 'Player' or 'Name')
            player_col = None
            for col in ("Player", "Name", "player", "name"):
                if col in df.columns:
                    player_col = col
                    break

            if player_col is None:
                continue

            match = df[df[player_col].str.lower() == name_lower]
            if not match.empty:
                result[situation] = match.iloc[0].to_dict()

        if not result:
            logger.warning(
                "NST: no data found for '%s' season %s", player_name, season
            )
        return result
