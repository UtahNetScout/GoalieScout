"""API client modules for goalie data collection."""

from .nhl_api import NHLAPIClient
from .moneypuck import MoneyPuckClient
from .natural_stat_trick import NaturalStatTrickClient

__all__ = [
    'NHLAPIClient',
    'MoneyPuckClient',
    'NaturalStatTrickClient',
]
