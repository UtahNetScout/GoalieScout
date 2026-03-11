"""High-Danger Save Percentage (HD/MD/LD) analytics.

Defines shot danger zones and calculates split save percentages for
high-danger (HD), medium-danger (MD), and low-danger (LD) shots.

Zone definitions
----------------
High-danger (HD)
    Shot distance ≤ 30 ft *and* absolute angle ≤ 35°
    — equivalent to the slot / inner slot area.

Medium-danger (MD)
    Shot distance ≤ 50 ft *or* absolute angle ≤ 55°,
    but not meeting the HD threshold.

Low-danger (LD)
    Everything else (perimeter, long-distance shots).
"""

from typing import Dict, Any, List

# Zone boundary constants (feet / degrees)
HD_MAX_DISTANCE: float = 30.0
HD_MAX_ANGLE: float = 35.0
MD_MAX_DISTANCE: float = 50.0
MD_MAX_ANGLE: float = 55.0


def classify_shot(distance: float, angle: float) -> str:
    """Classify a shot into a danger zone based on distance and angle.

    Args:
        distance: Distance from the net in feet.
        angle: Absolute horizontal angle from the slot centre-line in
               degrees (0 = directly in front, 90 = side boards).

    Returns:
        Zone string: ``'high'``, ``'medium'``, or ``'low'``.
    """
    abs_angle = abs(angle)
    if distance <= HD_MAX_DISTANCE and abs_angle <= HD_MAX_ANGLE:
        return "high"
    if distance <= MD_MAX_DISTANCE or abs_angle <= MD_MAX_ANGLE:
        return "medium"
    return "low"


def calculate_zone_save_pct(
    shots: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Calculate HD/MD/LD save percentages from a list of shot records.

    Each shot dict must contain:

    - ``distance`` — float, distance from net in feet
    - ``angle`` — float, absolute horizontal angle in degrees
    - ``goal`` — bool, whether the shot resulted in a goal

    Optional keys (forwarded to output for reference):

    - ``shot_type``, ``is_rebound``, ``is_rush``

    Args:
        shots: List of shot dictionaries faced by the goalie.

    Returns:
        Dictionary with keys:

        - ``hd_sv_pct`` — High-danger save percentage (or None if 0 shots)
        - ``md_sv_pct`` — Medium-danger save percentage
        - ``ld_sv_pct`` — Low-danger save percentage
        - ``overall_sv_pct`` — Overall save percentage
        - ``hd_shots`` — Number of high-danger shots faced
        - ``md_shots`` — Medium-danger shots faced
        - ``ld_shots`` — Low-danger shots faced
        - ``total_shots`` — Total shots faced
        - ``hd_goals`` — Goals allowed on high-danger shots
        - ``md_goals`` — Goals on medium-danger shots
        - ``ld_goals`` — Goals on low-danger shots
    """
    counts: Dict[str, int] = {"high": 0, "medium": 0, "low": 0}
    goals: Dict[str, int] = {"high": 0, "medium": 0, "low": 0}

    for shot in shots:
        zone = classify_shot(
            distance=shot.get("distance", 30.0),
            angle=shot.get("angle", 0.0),
        )
        counts[zone] += 1
        if shot.get("goal", False):
            goals[zone] += 1

    def _sv_pct(zone: str) -> Optional[float]:
        if counts[zone] == 0:
            return None
        saves = counts[zone] - goals[zone]
        return round(saves / counts[zone], 4)

    total_shots = sum(counts.values())
    total_goals = sum(goals.values())
    overall_sv_pct = (
        round((total_shots - total_goals) / total_shots, 4) if total_shots > 0 else None
    )

    return {
        "hd_sv_pct": _sv_pct("high"),
        "md_sv_pct": _sv_pct("medium"),
        "ld_sv_pct": _sv_pct("low"),
        "overall_sv_pct": overall_sv_pct,
        "hd_shots": counts["high"],
        "md_shots": counts["medium"],
        "ld_shots": counts["low"],
        "total_shots": total_shots,
        "hd_goals": goals["high"],
        "md_goals": goals["medium"],
        "ld_goals": goals["low"],
    }


def aggregate_zone_save_pct(
    game_zone_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Aggregate per-game zone save percentages into season/career totals.

    Args:
        game_zone_results: List of outputs from :func:`calculate_zone_save_pct`.

    Returns:
        Aggregated zone save percentages and shot counts using the same
        schema as :func:`calculate_zone_save_pct`.
    """
    totals: Dict[str, int] = {
        "hd_shots": 0,
        "md_shots": 0,
        "ld_shots": 0,
        "hd_goals": 0,
        "md_goals": 0,
        "ld_goals": 0,
    }
    for result in game_zone_results:
        for key in totals:
            totals[key] += result.get(key, 0)

    def _sv(shots_key: str, goals_key: str) -> Optional[float]:
        s = totals[shots_key]
        g = totals[goals_key]
        if s == 0:
            return None
        return round((s - g) / s, 4)

    total_shots = totals["hd_shots"] + totals["md_shots"] + totals["ld_shots"]
    total_goals = totals["hd_goals"] + totals["md_goals"] + totals["ld_goals"]

    return {
        "hd_sv_pct": _sv("hd_shots", "hd_goals"),
        "md_sv_pct": _sv("md_shots", "md_goals"),
        "ld_sv_pct": _sv("ld_shots", "ld_goals"),
        "overall_sv_pct": (
            round((total_shots - total_goals) / total_shots, 4)
            if total_shots > 0
            else None
        ),
        "hd_shots": totals["hd_shots"],
        "md_shots": totals["md_shots"],
        "ld_shots": totals["ld_shots"],
        "total_shots": total_shots,
        "hd_goals": totals["hd_goals"],
        "md_goals": totals["md_goals"],
        "ld_goals": totals["ld_goals"],
    }
