"""Improved scraper implementations for goalie data collection."""

from .elite_prospects import EliteProspectsScraper
from .hockey_db import HockeyDBScraper

__all__ = [
    'EliteProspectsScraper',
    'HockeyDBScraper',
]
