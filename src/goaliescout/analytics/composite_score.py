"""Black Ops Score — Composite Goalie Rating (0-100).

The Black Ops Score is the signature metric of the GoalieScout platform.
It aggregates all advanced analytics modules into a single, interpretable
0-100 rating with NHL-grade tier classification and confidence intervals.

Weights
-------
- GSAx (normalised)          25 %
- High-danger SV%            20 %
- Rebound control rate       15 %
- Consistency index          15 %
- Movement efficiency        10 %
- Puck handling (proxy)      10 %
- Development trajectory      5 %

Total                       100 %
"""

import math
from typing import Dict, Any, Optional


# Tier thresholds
TIER_THRESHOLDS = [
    (90, "Elite", "NHL Starter"),
    (80, "Above Average", "NHL/AHL"),
    (70, "Average", "AHL/Top College"),
    (60, "Below Average", "Developmental"),
    (0, "Needs Improvement", "Development League"),
]

# Component weights (must sum to 1.0)
WEIGHTS: Dict[str, float] = {
    "gsax": 0.25,
    "hd_sv_pct": 0.20,
    "rebound_control": 0.15,
    "consistency": 0.15,
    "movement": 0.10,
    "puck_handling": 0.10,
    "development": 0.05,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Component weights must sum to 1.0"

# Reference ranges for normalisation
# Each tuple: (worst_expected, best_expected) → maps to 0-100 range
_NORM_RANGES: Dict[str, tuple] = {
    "gsax_per_game": (-0.5, 0.5),      # goals saved above expected per game
    "hd_sv_pct": (0.820, 0.960),       # high-danger save pct
    "controlled_rebound_rate": (0.40, 0.90),  # fraction of rebounds controlled
    "consistency_score": (0.0, 100.0),  # already 0-100
    "movement_score": (0.0, 100.0),    # already 0-100
    "puck_handling_score": (0.0, 100.0),
    "development_score": (0.0, 100.0),
}


def _normalise(value: float, low: float, high: float) -> float:
    """Linearly normalise *value* from [low, high] into [0, 100].

    Args:
        value: Raw metric value.
        low: Minimum expected value (maps to 0).
        high: Maximum expected value (maps to 100).

    Returns:
        Clamped normalised score in [0, 100].
    """
    if high == low:
        return 50.0
    norm = (value - low) / (high - low) * 100.0
    return max(0.0, min(100.0, norm))


def _confidence_interval(
    score: float, games_played: int
) -> Dict[str, float]:
    """Estimate ±95 % confidence interval for the composite score.

    The interval is wider for small sample sizes and narrows as games
    accumulate toward a reference of 40+ games.

    Args:
        score: Composite Black Ops Score.
        games_played: Number of games in the sample.

    Returns:
        Dict with ``lower`` and ``upper`` bounds.
    """
    if games_played <= 0:
        return {"lower": 0.0, "upper": 100.0}
    # Standard error proxy: wider at low N
    se = 15.0 / math.sqrt(max(1, games_played))
    margin = 1.96 * se
    return {
        "lower": round(max(0.0, score - margin), 2),
        "upper": round(min(100.0, score + margin), 2),
    }


def classify_tier(score: float) -> Dict[str, str]:
    """Classify a Black Ops Score into a named tier.

    Args:
        score: Black Ops Score in [0, 100].

    Returns:
        Dict with ``tier`` and ``description`` keys.
    """
    for threshold, tier, description in TIER_THRESHOLDS:
        if score >= threshold:
            return {"tier": tier, "description": description}
    return {"tier": "Needs Improvement", "description": "Development League"}


def calculate_black_ops_score(
    gsax_per_game: Optional[float] = None,
    hd_sv_pct: Optional[float] = None,
    controlled_rebound_rate: Optional[float] = None,
    consistency_score: Optional[float] = None,
    movement_score: Optional[float] = None,
    puck_handling_score: Optional[float] = None,
    development_score: Optional[float] = None,
    games_played: int = 0,
    custom_weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Calculate the Black Ops composite score for a goalie.

    Any ``None`` components are replaced with a neutral score of 50.0
    (unknown / unavailable), so the function always produces a result.

    Args:
        gsax_per_game: Goals Saved Above Expected per game
            (positive = better; typical range -0.5 to +0.5).
        hd_sv_pct: High-danger save percentage (0.0-1.0).
        controlled_rebound_rate: Fraction of rebounds that are
            controlled (0.0-1.0).
        consistency_score: Performance Volatility Index score (0-100).
        movement_score: Lateral movement efficiency score (0-100).
        puck_handling_score: Puck-handling score (0-100).
        development_score: Development trajectory score (0-100).
        games_played: Total games played (used for confidence interval).
        custom_weights: Optional dict to override default component weights.
            Must contain the same keys as :data:`WEIGHTS` and sum to 1.0.

    Returns:
        Dictionary with keys:

        - ``black_ops_score`` — composite score in [0, 100]
        - ``tier`` — classification tier string
        - ``tier_description`` — tier description
        - ``confidence_interval`` — dict with ``lower`` / ``upper`` bounds
        - ``component_scores`` — normalised 0-100 score for each component
        - ``component_weights`` — weights applied to each component
        - ``games_played`` — input games played
        - ``data_completeness`` — fraction of components with real data

    Raises:
        ValueError: If ``custom_weights`` does not sum to 1.0.
    """
    weights = dict(WEIGHTS)
    if custom_weights:
        if abs(sum(custom_weights.values()) - 1.0) > 0.001:
            raise ValueError("custom_weights must sum to 1.0")
        weights.update(custom_weights)

    # Map raw inputs to 0-100 normalised component scores
    components: Dict[str, Optional[float]] = {
        "gsax": gsax_per_game,
        "hd_sv_pct": hd_sv_pct,
        "rebound_control": controlled_rebound_rate,
        "consistency": consistency_score,
        "movement": movement_score,
        "puck_handling": puck_handling_score,
        "development": development_score,
    }

    # Normalisation config per component
    norm_map = {
        "gsax": ("gsax_per_game", _NORM_RANGES["gsax_per_game"]),
        "hd_sv_pct": ("hd_sv_pct", _NORM_RANGES["hd_sv_pct"]),
        "rebound_control": ("controlled_rebound_rate", _NORM_RANGES["controlled_rebound_rate"]),
        "consistency": ("consistency_score", _NORM_RANGES["consistency_score"]),
        "movement": ("movement_score", _NORM_RANGES["movement_score"]),
        "puck_handling": ("puck_handling_score", _NORM_RANGES["puck_handling_score"]),
        "development": ("development_score", _NORM_RANGES["development_score"]),
    }

    normalised: Dict[str, float] = {}
    real_data_count = 0

    for key, raw_value in components.items():
        _, (low, high) = norm_map[key]
        if raw_value is None:
            normalised[key] = 50.0  # neutral imputation
        else:
            normalised[key] = _normalise(raw_value, low, high)
            real_data_count += 1

    data_completeness = round(real_data_count / len(components), 4)

    # Weighted composite
    composite = sum(normalised[k] * weights[k] for k in weights)
    composite = round(max(0.0, min(100.0, composite)), 2)

    tier_info = classify_tier(composite)
    ci = _confidence_interval(composite, games_played)

    return {
        "black_ops_score": composite,
        "tier": tier_info["tier"],
        "tier_description": tier_info["description"],
        "confidence_interval": ci,
        "component_scores": {k: round(v, 2) for k, v in normalised.items()},
        "component_weights": weights,
        "games_played": games_played,
        "data_completeness": data_completeness,
    }
