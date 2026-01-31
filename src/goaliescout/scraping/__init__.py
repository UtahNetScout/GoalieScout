"""Scraping module initialization."""

from .scrapers import (
    GoalieScraper,
    EliteProspectsScaper,
    HockeyDBScraper,
    DataEnricher
)

__all__ = [
    'GoalieScraper',
    'EliteProspectsScaper',
    'HockeyDBScraper',
    'DataEnricher'
]
