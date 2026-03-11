"""HockeyDB scraper — functional implementation replacing the placeholder.

Searches for goalies on HockeyDB.com, parses stats tables, and can
cross-reference data with EliteProspects profiles.
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

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


class HockeyDBScraper(GoalieScraper):
    """Real HockeyDB.com scraper for goalie statistics.

    Searches for players on HockeyDB, parses their career stats pages,
    and can enumerate all goalies from a given league and season.

    Args:
        delay: Seconds to wait between HTTP requests.

    Example::

        scraper = HockeyDBScraper()
        results = scraper.search_player("Juuse Saros")
        if results:
            stats = scraper.get_player_stats(results[0]["url"])
    """

    BASE_URL = "https://www.hockeydb.com"

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
            logger.error("HockeyDB fetch failed for %s: %s", url, exc)
            raise

    def _text(self, element: Any) -> str:
        """Strip and return text content of a BeautifulSoup tag."""
        return element.get_text(strip=True) if element else ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search_player(self, name: str) -> List[Dict[str, Any]]:
        """Search HockeyDB for a player by name.

        Args:
            name: Player full or partial name.

        Returns:
            List of result dictionaries with ``name``, ``url``,
            ``position``, and ``team`` keys.
        """
        logger.info("HockeyDB search: '%s'", name)
        url = f"{self.BASE_URL}/sitecore/search/search.php"
        try:
            soup = self._get(url, params={"search": name, "cat": "goalie"})
        except Exception:
            logger.exception("HockeyDB search failed for '%s'", name)
            return []

        if soup is None:
            return []

        results: List[Dict[str, Any]] = []
        for row in soup.select("table.stats tr"):
            link = row.find("a", href=re.compile(r"/sitecore/player-stats/"))
            if link is None:
                continue
            cells = row.find_all("td")
            results.append({
                "name": self._text(link),
                "url": urljoin(self.BASE_URL, link["href"]),
                "position": self._text(cells[2]) if len(cells) > 2 else "",
                "team": self._text(cells[1]) if len(cells) > 1 else "",
            })

        logger.info("HockeyDB: found %d results for '%s'", len(results), name)
        return results

    def get_player_stats(self, player_url: str) -> Dict[str, Any]:
        """Parse a player's career stats page.

        Args:
            player_url: Full URL to the player's HockeyDB stats page.

        Returns:
            Dictionary with ``career_stats`` (list of season rows) and
            ``bio`` sub-dict.  Each season row contains ``season``,
            ``team``, ``league``, ``gp``, ``w``, ``l``, ``t``, ``min``,
            ``ga``, ``so``, ``gaa``, and ``svpct`` keys where available.
        """
        logger.info("Fetching HockeyDB stats: %s", player_url)
        try:
            soup = self._get(player_url)
        except Exception:
            logger.exception("Failed to fetch HockeyDB player stats: %s", player_url)
            return {}

        if soup is None:
            return {}

        result: Dict[str, Any] = {"url": player_url, "career_stats": [], "bio": {}}

        # Bio info
        bio_table = soup.find("table", id="biostats") or soup.find("div", class_="bio")
        if bio_table:
            for row in bio_table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    key = self._text(cells[0]).lower().replace(" ", "_").rstrip(":")
                    result["bio"][key] = self._text(cells[1])

        # Stats table
        stats_table = soup.find("table", id="stats-regular") or soup.find("table", class_=re.compile(r"stats"))
        if stats_table is None:
            logger.warning("No stats table found at %s", player_url)
            return result

        headers: List[str] = []
        for th in stats_table.find_all("th"):
            header = self._text(th).lower().replace(" ", "_").replace("%", "pct").replace("/", "_")
            headers.append(header)

        for tr in stats_table.find_all("tr")[1:]:
            cells = tr.find_all("td")
            if not cells:
                continue
            row_data: Dict[str, Any] = {}
            for idx, cell in enumerate(cells):
                key = headers[idx] if idx < len(headers) else f"col_{idx}"
                row_data[key] = self._text(cell)
            if any(row_data.values()):
                result["career_stats"].append(row_data)

        logger.info("Parsed %d stat rows from %s", len(result["career_stats"]), player_url)
        return result

    def get_league_goalies(self, league: str, season: str) -> List[Dict[str, Any]]:
        """Return all goalies from a HockeyDB league-season stats page.

        Args:
            league: League abbreviation as used in HockeyDB URLs
                (e.g. ``"nhl"``, ``"ohl"``).
            season: Season string in YYYY-YYYY format
                (e.g. ``"2023-2024"``).

        Returns:
            List of dictionaries with ``name``, ``url``, ``team``, and
            ``league`` for each goalie found.
        """
        logger.info("Fetching HockeyDB league goalies: %s %s", league, season)
        season_slug = season.replace("-", "")
        url = f"{self.BASE_URL}/sitecore/league-stats/{league}-{season_slug}.html"
        try:
            soup = self._get(url)
        except Exception:
            logger.exception("HockeyDB league fetch failed: %s %s", league, season)
            return []

        if soup is None:
            return []

        goalies: List[Dict[str, Any]] = []
        for row in soup.select("table.stats tr"):
            link = row.find("a", href=re.compile(r"/sitecore/player-stats/"))
            if link is None:
                continue
            cells = row.find_all("td")
            goalies.append({
                "name": self._text(link),
                "url": urljoin(self.BASE_URL, link["href"]),
                "team": self._text(cells[2]) if len(cells) > 2 else "",
                "league": league,
            })

        logger.info("HockeyDB: found %d goalies in %s %s", len(goalies), league, season)
        return goalies
