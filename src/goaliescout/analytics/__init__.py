"""Analytics module initialization."""

from .engine import GoalieAnalytics, ComparisonEngine
from .gsax import calculate_gsax, calculate_game_gsax, aggregate_gsax
from .shot_quality import calculate_shot_xg, classify_shot_danger, evaluate_shot_batch
from .rebound_control import calculate_rebound_control, aggregate_rebound_control
from .slot_save_pct import calculate_zone_save_pct, aggregate_zone_save_pct
from .movement_analysis import (
    calculate_lateral_efficiency,
    calculate_crease_depth,
    calculate_movement_score,
)
from .rush_defense import calculate_rush_defense, aggregate_rush_defense
from .game_state import calculate_game_state_splits, aggregate_game_state_splits
from .consistency import calculate_consistency, calculate_consistency_from_games
from .age_curves import project_development, age_curve_score
from .composite_score import calculate_black_ops_score, classify_tier

__all__ = [
    # Original engine
    "GoalieAnalytics",
    "ComparisonEngine",
    # GSAx
    "calculate_gsax",
    "calculate_game_gsax",
    "aggregate_gsax",
    # Shot quality / xG
    "calculate_shot_xg",
    "classify_shot_danger",
    "evaluate_shot_batch",
    # Rebound control
    "calculate_rebound_control",
    "aggregate_rebound_control",
    # Zone save percentages
    "calculate_zone_save_pct",
    "aggregate_zone_save_pct",
    # Movement analysis
    "calculate_lateral_efficiency",
    "calculate_crease_depth",
    "calculate_movement_score",
    # Rush defense
    "calculate_rush_defense",
    "aggregate_rush_defense",
    # Game-state splits
    "calculate_game_state_splits",
    "aggregate_game_state_splits",
    # Consistency
    "calculate_consistency",
    "calculate_consistency_from_games",
    # Age curves
    "project_development",
    "age_curve_score",
    # Composite score
    "calculate_black_ops_score",
    "classify_tier",
]
