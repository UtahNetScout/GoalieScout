"""Scraping module initialization."""

from .scrapers import (
    GoalieScraper,
    EliteProspectsScaper,
    HockeyDBScraper,
    DataEnricher
)
from .apis import NHLAPIClient, MoneyPuckClient, NaturalStatTrickClient
from .scrapers_v2 import EliteProspectsScraper, HockeyDBScraper as HockeyDBScraperV2
from .validation import GoalieDataValidator, ValidationResult, DataNormalizer, GoalieDeduplicator
from .pipeline import DailyUpdatePipeline, GoalieDiscovery, PipelineScheduler, PipelineHealthCheck

__all__ = [
    # Legacy (v1) scrapers — preserved for backward compatibility
    'GoalieScraper',
    'EliteProspectsScaper',
    'HockeyDBScraper',
    'DataEnricher',
    # API clients
    'NHLAPIClient',
    'MoneyPuckClient',
    'NaturalStatTrickClient',
    # v2 scrapers
    'EliteProspectsScraper',
    'HockeyDBScraperV2',
    # Validation
    'GoalieDataValidator',
    'ValidationResult',
    'DataNormalizer',
    'GoalieDeduplicator',
    # Pipeline
    'DailyUpdatePipeline',
    'GoalieDiscovery',
    'PipelineScheduler',
    'PipelineHealthCheck',
]
