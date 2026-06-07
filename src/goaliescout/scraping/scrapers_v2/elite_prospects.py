"""EliteProspects scraper — functional implementation replacing the placeholder.

Searches for goalies on EliteProspects.com, navigates to player pages,
and parses career stats tables and biographical information.
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlencode

import requests
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..scrapers import GoalieScraper

logger = logging.getLogger(__name__)


class EliteProspectsScraper(GoalieScraper):
    """Real EliteProspects.com scraper for goalie data.

    Searches for players by name, parses player profile pages and career
    stats tables, and can enumerate all goalies from a specific league
    and season page.  Respects rate limits and provides retry logic for
    transient failures.

    Args:
        delay: Seconds to wait between HTTP requests.

    Example::

        scraper = EliteProspectsScraper()
        results = scraper.search_player("Spencer Knight")
        if results:
            profile = scraper.get_player_profile(results[0]["url"])
    """

    BASE_URL = "https://www.eliteprospects.com"

    def __init__(self, delay: float = 2.0) -> None:
        super().__init__(delay=delay)
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @retry(
        retry=retry_if_exception_type(requests.RequestException),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _get(self, url: str, params: Optional[Dict[str, str]] = None) -> Optional[BeautifulSoup]:
        """Fetch *url* and return a parsed BeautifulSoup tree.

        Args:
            url: Target URL.
            params: Optional query parameters.

        Returns:
            Parsed page or ``None`` on failure.
        """
        time.sleep(self.delay)
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as exc:
            logger.error("EliteProspects fetch failed for %s: %s", url, exc)
            raise

    def _text(self, element: Any) -> str:
        """Strip and return text content of a BeautifulSoup tag."""
        return element.get_text(strip=True) if element else ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search_player(self, name: str) -> List[Dict[str, Any]]:
        """Search EliteProspects for a player by name.

        Args:
            name: Player full or partial name to search for.

        Returns:
            List of result dictionaries, each containing ``name``,
            ``url``, ``position``, ``team``, and ``league`` keys.
        """
        logger.info("EliteProspects search: '%s'", name)
        url = f"{self.BASE_URL}/search"
        try:
            soup = self._get(url, params={"q": name})
        except Exception:
            logger.exception("Search failed for '%s'", name)
            return []

        if soup is None:
            return []

        results: List[Dict[str, Any]] = []
        # EP search returns player cards in a list
        for row in soup.select("table.player-search-results tr"):
            cells = row.find_all("td")
            if not cells:
                continue
            link = row.find("a", href=re.compile(r"/player/"))
            if link is None:
                continue

            position_cell = cells[2] if len(cells) > 2 else None
            position = self._text(position_cell).upper()
            if position and "G" not in position and "GOALIE" not in position:
                continue  # Skip non-goalies

            results.append({
                "name": self._text(link),
                "url": urljoin(self.BASE_URL, link["href"]),
                "position": position,
                "team": self._text(cells[3]) if len(cells) > 3 else "",
                "league": self._text(cells[4]) if len(cells) > 4 else "",
            })

        logger.info("EliteProspects: found %d results for '%s'", len(results), name)
        return results

    def get_player_profile(self, player_url: str) -> Dict[str, Any]:
        """Parse a player profile page and return biographical data.

        Args:
            player_url: Full URL to the player's EliteProspects page.

        Returns:
            Dictionary with biographical fields: ``name``, ``dob``,
            ``nationality``, ``height_cm``, ``weight_kg``, ``catches``,
            ``position``, and ``current_team``.
        """
        logger.info("Fetching EP profile: %s", player_url)
        try:
            soup = self._get(player_url)
        except Exception:
            logger.exception("Failed to fetch profile: %s", player_url)
            return {}

        if soup is None:
            return {}

        profile: Dict[str, Any] = {"url": player_url}

        # Name
        h1 = soup.find("h1", class_=re.compile(r"player"))
        if h1:
            profile["name"] = self._text(h1)

        # Bio block: key-value pairs in the info table
        for row in soup.select("div.player-info table tr, table.player-facts tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                key = self._text(cells[0]).lower().replace(" ", "_").rstrip(":")
                value = self._text(cells[1])
                profile[key] = value

        # Normalise common fields
        profile.setdefault("dob", profile.pop("date_of_birth", ""))
        profile.setdefault("nationality", profile.pop("nation", ""))
        profile.setdefault("catches", profile.pop("catches/shoots", ""))

        return profile

    def get_career_stats(self, player_url: str) -> List[Dict[str, Any]]:
        """Parse the career stats table for a player.

        Args:
            player_url: Full URL to the player's EliteProspects page.

        Returns:
            List of season stat dictionaries, each containing ``season``,
            ``team``, ``league``, ``gp``, ``w``, ``l``, ``t_otl``,
            ``gaa``, ``svpct``, and ``so`` keys where available.
        """
        logger.info("Fetching EP career stats: %s", player_url)
        try:
            soup = self._get(player_url)
        except Exception:
            logger.exception("Failed to fetch career stats: %s", player_url)
            return []

        if soup is None:
            return []

        rows: List[Dict[str, Any]] = []
        # EP uses a table with class "table-responsive" for stats
        stats_table = soup.find("table", class_=re.compile(r"stats"))
        if stats_table is None:
            stats_table = soup.find("table", class_=re.compile(r"table"))

        if stats_table is None:
            logger.warning("No stats table found at %s", player_url)
            return []

        headers: List[str] = []
        for th in stats_table.find_all("th"):
            headers.append(self._text(th).lower().replace(" ", "_").replace("%", "pct").replace("/", "_"))

        for tr in stats_table.find_all("tr")[1:]:
            cells = tr.find_all("td")
            if not cells:
                continue
            row_data: Dict[str, Any] = {}
            for idx, cell in enumerate(cells):
                key = headers[idx] if idx < len(headers) else f"col_{idx}"
                row_data[key] = self._text(cell)

            # Skip empty/header-repeat rows
            if not any(row_data.values()):
                continue
            rows.append(row_data)

        logger.info("Parsed %d career stat rows from %s", len(rows), player_url)
        return rows

    def get_league_goalies(self, league: str, season: str) -> List[Dict[str, Any]]:
        """Enumerate all goalies listed for a league and season on EP.

        Args:
            league: League URL slug as used by EliteProspects
                (e.g. ``"ohl"``, ``"ncaa"``, ``"shl"``).
            season: Season slug as used by EliteProspects
                (e.g. ``"2023-2024"``).

        Returns:
            List of dictionaries with ``name``, ``url``, ``team``, and
            ``league`` keys for each goalie found.
        """
        logger.info("Fetching EP league goalies: %s season %s", league, season)
        url = f"{self.BASE_URL}/league/{league}/stats/{season}/G/league/desc/0/All"
        try:
            soup = self._get(url)
        except Exception:
            logger.exception("Failed to fetch league goalies: %s %s", league, season)
            return []

        if soup is None:
            return []

        goalies: List[Dict[str, Any]] = []
        for row in soup.select("table.table-sortable tr, table.stats tr"):
            link = row.find("a", href=re.compile(r"/player/"))
            if link is None:
                continue
            cells = row.find_all("td")
            goalies.append({
                "name": self._text(link),
                "url": urljoin(self.BASE_URL, link["href"]),
                "team": self._text(cells[2]) if len(cells) > 2 else "",
                "league": league,
            })

        logger.info("Found %d goalies for %s season %s", len(goalies), league, season)
        return goalies
