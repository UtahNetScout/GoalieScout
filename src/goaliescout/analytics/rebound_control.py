"""Rebound Control Rate analytics.

Tracks how often a goalie surrenders dangerous rebounds and classifies
each rebound as controlled or uncontrolled based on where the puck ends
up after the save.
"""

import math
from typing import Dict, Any, List, Optional


def _rebound_danger_score(
    rebound_distance: float,
    rebound_angle: float,
) -> float:
    """Calculate a danger score for a rebound's location.

    Higher score = more dangerous rebound position.

    Args:
        rebound_distance: Distance of rebound puck from net in feet.
        rebound_angle: Absolute horizontal angle of rebound location in degrees.

    Returns:
        Danger score in [0.0, 1.0].
    """
    # Simple inverse-distance, angle-weighted score
    if rebound_distance <= 0:
        rebound_distance = 0.1
    distance_factor = max(0.0, 1.0 - rebound_distance / 50.0)
    angle_factor = max(0.0, math.cos(math.radians(min(90.0, abs(rebound_angle)))))
    return round(distance_factor * angle_factor, 4)


def classify_rebound(
    rebound_distance: float,
    rebound_angle: float,
    controlled_distance_threshold: float = 10.0,
) -> str:
    """Classify a rebound as controlled or uncontrolled.

    A *controlled* rebound is one where the puck is directed to a safe
    area (corner, behind net) or absorbed.  An *uncontrolled* rebound
    lands in the danger zone in front of the crease.

    Args:
        rebound_distance: Distance of rebound puck from net in feet.
        rebound_angle: Absolute horizontal angle of rebound in degrees.
        controlled_distance_threshold: Maximum distance from net that still
            qualifies as an *uncontrolled* (dangerous) rebound.

    Returns:
        ``'controlled'`` or ``'uncontrolled'``.
    """
    if rebound_distance > controlled_distance_threshold:
        return "controlled"
    # Within threshold — use angle: rebounds deflected wide (>45°) are
    # considered controlled
    if abs(rebound_angle) > 45.0:
        return "controlled"
    return "uncontrolled"


def calculate_rebound_control(
    saves: List[Dict[str, Any]],
    controlled_distance_threshold: float = 10.0,
) -> Dict[str, Any]:
    """Calculate rebound control metrics from a list of save records.

    Each save dict may contain:

    - ``has_rebound`` — bool, whether a rebound occurred (default False)
    - ``rebound_distance`` — float, distance of the rebound from net (feet)
    - ``rebound_angle`` — float, absolute horizontal angle (degrees)

    Args:
        saves: List of save dictionaries.
        controlled_distance_threshold: Distance threshold for classifying
            a rebound as controlled vs. uncontrolled.

    Returns:
        Dictionary with keys:

        - ``total_saves`` — total number of saves
        - ``saves_with_rebound`` — how many saves resulted in a rebound
        - ``controlled_rebounds`` — rebounds classified as controlled
        - ``uncontrolled_rebounds`` — rebounds classified as uncontrolled
        - ``rebound_rate`` — fraction of saves that produce any rebound
        - ``controlled_rebound_rate`` — fraction of rebounds that are
          controlled
        - ``avg_rebound_danger`` — mean danger score of all rebounds
    """
    total_saves = len(saves)
    saves_with_rebound = 0
    controlled = 0
    uncontrolled = 0
    danger_scores: List[float] = []

    for save in saves:
        if not save.get("has_rebound", False):
            continue
        saves_with_rebound += 1
        r_dist = save.get("rebound_distance", 15.0)
        r_angle = save.get("rebound_angle", 0.0)
        classification = classify_rebound(
            r_dist, r_angle, controlled_distance_threshold
        )
        if classification == "controlled":
            controlled += 1
        else:
            uncontrolled += 1
        danger_scores.append(_rebound_danger_score(r_dist, r_angle))

    rebound_rate = (
        round(saves_with_rebound / total_saves, 4) if total_saves > 0 else 0.0
    )
    controlled_rate = (
        round(controlled / saves_with_rebound, 4) if saves_with_rebound > 0 else None
    )
    avg_danger = (
        round(sum(danger_scores) / len(danger_scores), 4) if danger_scores else 0.0
    )

    return {
        "total_saves": total_saves,
        "saves_with_rebound": saves_with_rebound,
        "controlled_rebounds": controlled,
        "uncontrolled_rebounds": uncontrolled,
        "rebound_rate": rebound_rate,
        "controlled_rebound_rate": controlled_rate,
        "avg_rebound_danger": avg_danger,
    }


def aggregate_rebound_control(
    game_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Aggregate per-game rebound control results into totals.

    Args:
        game_results: List of outputs from :func:`calculate_rebound_control`.

    Returns:
        Aggregated rebound control metrics.
    """
    if not game_results:
        return {
            "total_saves": 0,
            "saves_with_rebound": 0,
            "controlled_rebounds": 0,
            "uncontrolled_rebounds": 0,
            "rebound_rate": 0.0,
            "controlled_rebound_rate": None,
            "avg_rebound_danger": 0.0,
        }

    total_saves = sum(g.get("total_saves", 0) for g in game_results)
    saves_with_rebound = sum(g.get("saves_with_rebound", 0) for g in game_results)
    controlled = sum(g.get("controlled_rebounds", 0) for g in game_results)
    uncontrolled = sum(g.get("uncontrolled_rebounds", 0) for g in game_results)

    # Weighted average danger
    total_danger = sum(
        g.get("avg_rebound_danger", 0.0) * g.get("saves_with_rebound", 0)
        for g in game_results
    )
    avg_danger = (
        round(total_danger / saves_with_rebound, 4) if saves_with_rebound > 0 else 0.0
    )

    return {
        "total_saves": total_saves,
        "saves_with_rebound": saves_with_rebound,
        "controlled_rebounds": controlled,
        "uncontrolled_rebounds": uncontrolled,
        "rebound_rate": round(saves_with_rebound / total_saves, 4) if total_saves > 0 else 0.0,
        "controlled_rebound_rate": (
            round(controlled / saves_with_rebound, 4) if saves_with_rebound > 0 else None
        ),
        "avg_rebound_danger": avg_danger,
    }
