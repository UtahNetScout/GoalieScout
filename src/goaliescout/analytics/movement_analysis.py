"""Lateral Movement & Crease Depth positioning analytics.

Analyses goalie positioning efficiency when tracking/coordinate data is
available.  When only aggregate positional data is provided the module
falls back to tier-based estimates.
"""

import math
from typing import Dict, Any, List, Optional


def calculate_lateral_efficiency(
    tracking_events: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Calculate lateral movement efficiency from a list of tracking events.

    Each event dict should contain:

    - ``x_before`` — goalie x-position before the shot (feet, crease centre = 0)
    - ``x_ideal`` — ideal (optimal) x-position for that shot angle
    - ``x_after`` — goalie x-position immediately after the shot (optional)
    - ``timestamp_before`` — seconds elapsed (optional, for speed calc)
    - ``timestamp_after`` — seconds elapsed (optional, for speed calc)

    Args:
        tracking_events: List of positional tracking event dicts.

    Returns:
        Dictionary with keys:

        - ``avg_position_error`` — mean absolute difference between actual
          and ideal x-position at shot time (feet)
        - ``avg_lateral_speed`` — mean lateral movement speed (ft/s)
          (None if timestamps unavailable)
        - ``positioning_efficiency`` — 0-100 score (100 = perfect)
        - ``events_analyzed`` — number of events used
    """
    if not tracking_events:
        return {
            "avg_position_error": None,
            "avg_lateral_speed": None,
            "positioning_efficiency": None,
            "events_analyzed": 0,
        }

    errors: List[float] = []
    speeds: List[float] = []

    for ev in tracking_events:
        x_before = ev.get("x_before", 0.0)
        x_ideal = ev.get("x_ideal")
        if x_ideal is not None:
            errors.append(abs(x_before - x_ideal))

        x_after = ev.get("x_after")
        t_before = ev.get("timestamp_before")
        t_after = ev.get("timestamp_after")
        if x_after is not None and t_before is not None and t_after is not None:
            dt = t_after - t_before
            if dt > 0:
                speeds.append(abs(x_after - x_before) / dt)

    avg_error = round(sum(errors) / len(errors), 4) if errors else None
    avg_speed = round(sum(speeds) / len(speeds), 4) if speeds else None

    # Positioning efficiency: score of 100 when error = 0, decay with error
    # A 3-foot average positioning error ≈ 50/100
    efficiency: Optional[float] = None
    if avg_error is not None:
        efficiency = round(max(0.0, 100.0 * math.exp(-0.3 * avg_error)), 2)

    return {
        "avg_position_error": avg_error,
        "avg_lateral_speed": avg_speed,
        "positioning_efficiency": efficiency,
        "events_analyzed": len(tracking_events),
    }


def calculate_crease_depth(
    depth_readings: List[float],
) -> Dict[str, Any]:
    """Analyse crease-depth positioning from a series of depth readings.

    Crease depth is measured in feet from the goal line (0 = on line,
    positive = out toward the shooter).  NHL goalies typically play
    between 1–5 feet out depending on situation.

    Args:
        depth_readings: List of crease-depth measurements (feet).

    Returns:
        Dictionary with keys:

        - ``avg_depth`` — mean crease depth in feet
        - ``min_depth`` — shallowest position recorded
        - ``max_depth`` — deepest/most aggressive position
        - ``depth_variability`` — standard deviation of depth readings
        - ``style`` — qualitative label: ``'butterfly_aggressive'``,
          ``'mid_depth'``, or ``'deep_crease'``
    """
    if not depth_readings:
        return {
            "avg_depth": None,
            "min_depth": None,
            "max_depth": None,
            "depth_variability": None,
            "style": "unknown",
        }

    import statistics as _stats

    avg = round(sum(depth_readings) / len(depth_readings), 4)
    mn = round(min(depth_readings), 4)
    mx = round(max(depth_readings), 4)
    variability = round(_stats.stdev(depth_readings), 4) if len(depth_readings) > 1 else 0.0

    if avg >= 3.5:
        style = "butterfly_aggressive"
    elif avg >= 2.0:
        style = "mid_depth"
    else:
        style = "deep_crease"

    return {
        "avg_depth": avg,
        "min_depth": mn,
        "max_depth": mx,
        "depth_variability": variability,
        "style": style,
    }


def calculate_movement_score(
    lateral_result: Optional[Dict[str, Any]] = None,
    depth_result: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute a combined movement efficiency score (0-100).

    Combines lateral positioning efficiency and crease-depth consistency
    into a single metric.

    Args:
        lateral_result: Output from :func:`calculate_lateral_efficiency`.
        depth_result: Output from :func:`calculate_crease_depth`.

    Returns:
        Combined movement score in [0, 100].  Returns 50.0 if no data
        is available (neutral / unknown).
    """
    components: List[float] = []

    if lateral_result and lateral_result.get("positioning_efficiency") is not None:
        components.append(lateral_result["positioning_efficiency"])

    if depth_result and depth_result.get("depth_variability") is not None:
        # Lower variability = more consistent depth = higher score
        var = depth_result["depth_variability"]
        depth_score = max(0.0, 100.0 * math.exp(-0.5 * var))
        components.append(depth_score)

    if not components:
        return 50.0  # neutral default when no tracking data

    return round(sum(components) / len(components), 2)
