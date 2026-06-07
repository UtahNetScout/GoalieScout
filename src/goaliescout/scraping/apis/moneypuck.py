"""MoneyPuck advanced goalie analytics client.

MoneyPuck provides freely downloadable CSV files with comprehensive
advanced hockey analytics including Goals Saved Above Expected (GSAx),
expected goals against, shot quality data, and rebound statistics.
"""

import io
import logging
from typing import Any, Dict, Optional

import pandas as pd
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

# MoneyPuck goalie CSV data URL pattern
_MP_BASE_URL = "https://moneypuck.com/moneypuck/playerData/seasonSummary"
_MP_GOALIE_CSV = "{base}/{season}/regular/goalies.csv"


class MoneyPuckError(Exception):
    """Raised when a MoneyPuck data request fails."""


class MoneyPuckClient:
    """Client for MoneyPuck free goalie analytics CSV data.

    Downloads and parses MoneyPuck's season summary CSV files which
    contain advanced goalie metrics such as GSAx, xGoals Against,
    high-danger/medium-danger/low-danger save percentages, and
    rebound rates.

    Args:
        timeout: HTTP request timeout in seconds.

    Example::

        client = MoneyPuckClient()
        df = client.download_season_data("2023")
        rankings = client.get_all_goalie_rankings("2023")
    """

    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": _USER_AGENT})
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
    def _download_csv(self, url: str) -> pd.DataFrame:
        """Download and parse a CSV from *url*.

        Args:
            url: Direct URL to the CSV file.

        Returns:
            Parsed :class:`pandas.DataFrame`.

        Raises:
            MoneyPuckError: On HTTP errors or CSV parse failures.
        """
        try:
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return pd.read_csv(io.StringIO(response.text))
        except requests.HTTPError as exc:
            raise MoneyPuckError(
                f"MoneyPuck download failed [{exc.response.status_code}]: {url}"
            ) from exc
        except Exception as exc:
            raise MoneyPuckError(f"Failed to parse MoneyPuck CSV: {exc}") from exc

    def _season_url(self, season: str) -> str:
        """Build the CSV download URL for a given season.

        Args:
            season: Four-digit season year such as ``"2023"`` for the
                2023-24 season.

        Returns:
            Full download URL string.
        """
        return _MP_GOALIE_CSV.format(base=_MP_BASE_URL, season=season)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def download_season_data(self, season: str) -> pd.DataFrame:
        """Download and return the full goalie season CSV as a DataFrame.

        Results are cached in memory so repeated calls for the same season
        do not make additional network requests.

        Args:
            season: Four-digit year identifying the season
                (e.g. ``"2023"`` = 2023-24).

        Returns:
            :class:`pandas.DataFrame` with one row per goalie containing
            columns such as ``name``, ``team``, ``situation``,
            ``icetime``, ``xGoals``, ``goalsAllowed``, ``savedShotsOnGoal``,
            ``xGoalsPercentage``, and ``GSAx``.

        Raises:
            MoneyPuckError: If the download or parse fails.
        """
        if season not in self._cache:
            url = self._season_url(season)
            logger.info("Downloading MoneyPuck season data for %s from %s", season, url)
            df = self._download_csv(url)
            # Keep only goalie rows for the "all" situation by default so the
            # caller gets one summary row per goalie; we store the full frame.
            self._cache[season] = df
            logger.info(
                "Downloaded %d rows for MoneyPuck season %s", len(df), season
            )
        return self._cache[season].copy()

    def get_goalie_gsax(self, player_name: str, season: str) -> Dict[str, Any]:
        """Return GSAx and related metrics for a named goalie.

        Args:
            player_name: Player full name as it appears in MoneyPuck data
                (e.g. ``"Connor Hellebuyck"``).
            season: Four-digit season year.

        Returns:
            Dictionary with keys ``name``, ``season``, ``situation``,
            ``GSAx``, ``xGoals``, ``goalsAllowed``, ``icetime``, and
            ``xGoalsPercentage``.  Returns an empty dict if the goalie is
            not found.
        """
        df = self.download_season_data(season)
        # Filter to "all" situation for a single summary row
        situation_df = df[df.get("situation", pd.Series()).eq("all")] if "situation" in df.columns else df
        match = situation_df[situation_df["name"].str.lower() == player_name.lower()]
        if match.empty:
            logger.warning("MoneyPuck: no data found for '%s' season %s", player_name, season)
            return {}
        row = match.iloc[0].to_dict()
        return {
            "name": row.get("name", player_name),
            "season": season,
            "situation": row.get("situation", "all"),
            "GSAx": row.get("GSAx"),
            "xGoals": row.get("xGoals"),
            "goalsAllowed": row.get("goalsAllowed"),
            "icetime": row.get("icetime"),
            "xGoalsPercentage": row.get("xGoalsPercentage"),
        }

    def get_all_goalie_rankings(self, season: str) -> pd.DataFrame:
        """Return all goalies ranked by GSAx for a season.

        Args:
            season: Four-digit season year.

        Returns:
            :class:`pandas.DataFrame` sorted by ``GSAx`` descending,
            filtered to the ``"all"`` situation.  Includes a ``rank``
            column.
        """
        df = self.download_season_data(season)
        if "situation" in df.columns:
            df = df[df["situation"] == "all"].copy()
        if "GSAx" not in df.columns:
            logger.warning("GSAx column not found in MoneyPuck data for season %s", season)
            return df

        df = df.sort_values("GSAx", ascending=False).reset_index(drop=True)
        df.insert(0, "rank", df.index + 1)
        return df

    def get_shot_quality_data(self, player_name: str, season: str) -> Dict[str, Any]:
        """Return shot-quality breakdown (HD/MD/LD) for a specific goalie.

        Args:
            player_name: Player full name as it appears in MoneyPuck data.
            season: Four-digit season year.

        Returns:
            Dictionary with separate rows for each shot danger situation
            (``"highDanger"``, ``"mediumDanger"``, ``"lowDanger"``).
            Each value is a sub-dict of stats for that situation.
            Returns an empty dict if no data is found.
        """
        df = self.download_season_data(season)
        situations = ["highDanger", "mediumDanger", "lowDanger"]
        result: Dict[str, Any] = {}

        name_lower = player_name.lower()
        for situation in situations:
            if "situation" in df.columns:
                sub = df[
                    (df["situation"] == situation)
                    & (df["name"].str.lower() == name_lower)
                ]
            else:
                sub = df[df["name"].str.lower() == name_lower]

            if not sub.empty:
                result[situation] = sub.iloc[0].to_dict()

        if not result:
            logger.warning(
                "MoneyPuck: no shot quality data for '%s' season %s", player_name, season
            )
        return result
