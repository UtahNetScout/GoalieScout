"""GoalieScout database module.

Provides SQLAlchemy ORM models, connection management, schema migrations,
a repository (data-access layer), and a JSON import utility.
"""

from .connection import get_engine, get_session, get_session_factory, reset_engine
from .migrations import create_schema, drop_schema, migrate
from .models import (
    AdvancedMetrics,
    Base,
    GameLog,
    Goalie,
    Injury,
    NHLComparison,
    ScoutingReport,
    Season,
)
from .repository import (
    add_game_log,
    add_nhl_comparison,
    add_scouting_report,
    add_season,
    create_goalie,
    delete_goalie,
    get_game_logs,
    get_goalie,
    get_goalie_by_legacy_id,
    get_scouting_reports,
    get_seasons,
    list_goalies,
    update_goalie,
    upsert_advanced_metrics,
)

__all__ = [
    # Connection
    "get_engine",
    "get_session",
    "get_session_factory",
    "reset_engine",
    # Migrations
    "create_schema",
    "drop_schema",
    "migrate",
    # Models
    "Base",
    "Goalie",
    "Season",
    "GameLog",
    "AdvancedMetrics",
    "Injury",
    "ScoutingReport",
    "NHLComparison",
    # Repository
    "create_goalie",
    "get_goalie",
    "get_goalie_by_legacy_id",
    "list_goalies",
    "update_goalie",
    "delete_goalie",
    "add_season",
    "get_seasons",
    "add_game_log",
    "get_game_logs",
    "upsert_advanced_metrics",
    "add_scouting_report",
    "get_scouting_reports",
    "add_nhl_comparison",
]
