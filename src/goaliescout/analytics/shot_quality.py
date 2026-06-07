"""Expected Goals (xG) model for shot quality evaluation.

Evaluates shot danger based on multiple contextual factors and returns
a probability (0.0-1.0) that each shot results in a goal.
"""

import math
from typing import Dict, Any, Optional


# Shot type danger multipliers (relative danger vs. wrist shot baseline)
SHOT_TYPE_WEIGHTS: Dict[str, float] = {
    "wrist": 1.00,
    "snap": 1.10,
    "slap": 0.85,
    "backhand": 0.90,
    "tip": 1.40,
    "deflection": 1.35,
    "wrap": 1.15,
    "penalty_shot": 1.20,
    "other": 1.00,
}

# Distance decay — baseline xG at various distances (feet from net)
# Derived from publicly available NHL shot data research
_DISTANCE_XG_BASELINE: Dict[int, float] = {
    5: 0.30,
    10: 0.20,
    15: 0.13,
    20: 0.09,
    30: 0.06,
    40: 0.04,
    50: 0.025,
    60: 0.015,
    80: 0.008,
    100: 0.004,
}


def _interpolate_distance_xg(distance: float) -> float:
    """Interpolate baseline xG for a given distance.

    Args:
        distance: Shot distance from net in feet.

    Returns:
        Interpolated baseline xG value.
    """
    distances = sorted(_DISTANCE_XG_BASELINE.keys())
    if distance <= distances[0]:
        return _DISTANCE_XG_BASELINE[distances[0]]
    if distance >= distances[-1]:
        return _DISTANCE_XG_BASELINE[distances[-1]]

    for i in range(len(distances) - 1):
        d0, d1 = distances[i], distances[i + 1]
        if d0 <= distance <= d1:
            t = (distance - d0) / (d1 - d0)
            xg0 = _DISTANCE_XG_BASELINE[d0]
            xg1 = _DISTANCE_XG_BASELINE[d1]
            return xg0 + t * (xg1 - xg0)
    return 0.005


def _angle_multiplier(angle_degrees: float) -> float:
    """Calculate an angle-based multiplier for xG.

    Shots from directly in front (0 degrees) are most dangerous.
    The multiplier decays as angle from center increases.

    Args:
        angle_degrees: Absolute angle from the slot centre-line (0–90 degrees).

    Returns:
        Multiplicative factor (0.3–1.0).
    """
    clamped = max(0.0, min(90.0, abs(angle_degrees)))
    # cosine decay: 1.0 at 0°, ~0.3 at 90°
    return max(0.30, math.cos(math.radians(clamped)))


def calculate_shot_xg(
    distance: float,
    angle: float,
    shot_type: str = "wrist",
    is_rebound: bool = False,
    is_rush: bool = False,
    is_power_play: bool = False,
    has_screen: bool = False,
    model_weights: Optional[Dict[str, float]] = None,
) -> float:
    """Calculate expected goals (xG) probability for a single shot.

    Args:
        distance: Distance from net in feet (positive number).
        angle: Absolute horizontal angle from the slot centre-line in degrees
               (0 = directly in front, 90 = side boards).
        shot_type: Shot type string — one of 'wrist', 'snap', 'slap',
                   'backhand', 'tip', 'deflection', 'wrap', 'penalty_shot'.
        is_rebound: Whether this is a rebound shot.
        is_rush: Whether this is an odd-man rush or breakaway opportunity.
        is_power_play: Whether the shooting team is on a power play.
        has_screen: Whether a screen/traffic obscures the goalie's view.
        model_weights: Optional dictionary to override default multipliers.
                       Supported keys: ``rebound``, ``rush``, ``power_play``,
                       ``screen``.

    Returns:
        Probability in [0.0, 1.0] representing the likelihood this shot
        results in a goal.

    Raises:
        ValueError: If ``distance`` is negative or ``angle`` is outside 0–90.
    """
    if distance < 0:
        raise ValueError(f"distance must be non-negative, got {distance}")
    if not (0.0 <= abs(angle) <= 90.0):
        raise ValueError(f"angle must be between 0 and 90 degrees, got {angle}")

    defaults = {
        "rebound": 1.85,
        "rush": 1.50,
        "power_play": 1.20,
        "screen": 1.25,
    }
    if model_weights:
        defaults.update(model_weights)

    # Base xG from distance
    xg = _interpolate_distance_xg(distance)

    # Apply angle multiplier
    xg *= _angle_multiplier(angle)

    # Apply shot type multiplier
    shot_key = shot_type.lower().strip() if shot_type else "wrist"
    xg *= SHOT_TYPE_WEIGHTS.get(shot_key, 1.00)

    # Apply situational multipliers
    if is_rebound:
        xg *= defaults["rebound"]
    if is_rush:
        xg *= defaults["rush"]
    if is_power_play:
        xg *= defaults["power_play"]
    if has_screen:
        xg *= defaults["screen"]

    # Clamp to valid probability range
    return max(0.0, min(1.0, xg))


def classify_shot_danger(
    distance: float,
    angle: float,
    shot_type: str = "wrist",
    is_rebound: bool = False,
    is_rush: bool = False,
) -> str:
    """Classify a shot into a danger zone category.

    Args:
        distance: Distance from net in feet.
        angle: Absolute horizontal angle from centre in degrees.
        shot_type: Shot type string.
        is_rebound: Whether this is a rebound.
        is_rush: Whether this is a rush opportunity.

    Returns:
        Danger classification: ``'high'``, ``'medium'``, or ``'low'``.
    """
    xg = calculate_shot_xg(
        distance=distance,
        angle=angle,
        shot_type=shot_type,
        is_rebound=is_rebound,
        is_rush=is_rush,
    )
    if xg >= 0.12:
        return "high"
    if xg >= 0.05:
        return "medium"
    return "low"


def evaluate_shot_batch(
    shots: list,
    model_weights: Optional[Dict[str, float]] = None,
) -> list:
    """Evaluate xG for a list of shot dictionaries.

    Each dict in ``shots`` should contain at minimum ``distance`` and
    ``angle`` keys.  All other keys map to :func:`calculate_shot_xg`
    parameters and are optional.

    Args:
        shots: List of shot dictionaries.
        model_weights: Optional model weight overrides passed to each shot.

    Returns:
        List of the input shot dicts, each augmented with an ``xg`` key
        and a ``danger_zone`` key.
    """
    results = []
    for shot in shots:
        xg = calculate_shot_xg(
            distance=shot.get("distance", 30.0),
            angle=shot.get("angle", 0.0),
            shot_type=shot.get("shot_type", "wrist"),
            is_rebound=shot.get("is_rebound", False),
            is_rush=shot.get("is_rush", False),
            is_power_play=shot.get("is_power_play", False),
            has_screen=shot.get("has_screen", False),
            model_weights=model_weights,
        )
        enriched = dict(shot)
        enriched["xg"] = xg
        enriched["danger_zone"] = classify_shot_danger(
            distance=shot.get("distance", 30.0),
            angle=shot.get("angle", 0.0),
            shot_type=shot.get("shot_type", "wrist"),
            is_rebound=shot.get("is_rebound", False),
            is_rush=shot.get("is_rush", False),
        )
        results.append(enriched)
    return results
