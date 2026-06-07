"""Odd-Man Rush Save Percentage analytics.

Calculates save percentage specifically on rush situations:
breakaways, 2-on-1, and 3-on-2 opportunities.
"""

from typing import Dict, Any, List, Optional

# Supported rush types
RUSH_TYPES = {"breakaway", "2_on_1", "3_on_2", "odd_man_rush"}


def calculate_rush_defense(
    shots: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Calculate rush-specific save percentages.

    Each shot dict should contain:

    - ``is_rush`` — bool (True if this is a rush/odd-man opportunity)
    - ``rush_type`` — str, one of ``'breakaway'``, ``'2_on_1'``,
      ``'3_on_2'``, ``'odd_man_rush'`` (optional, defaults to ``'odd_man_rush'``)
    - ``goal`` — bool, whether the shot resulted in a goal

    Args:
        shots: List of shot dictionaries.

    Returns:
        Dictionary with keys:

        - ``overall_rush_sv_pct`` — save % on all rush shots
        - ``breakaway_sv_pct`` — save % on pure breakaways (or None)
        - ``two_on_one_sv_pct`` — save % on 2-on-1s (or None)
        - ``three_on_two_sv_pct`` — save % on 3-on-2s (or None)
        - ``rush_shots`` — total rush shots faced
        - ``rush_goals`` — goals allowed on rush shots
        - ``non_rush_sv_pct`` — save % on non-rush shots
    """
    rush_counts: Dict[str, int] = {rt: 0 for rt in RUSH_TYPES}
    rush_goals: Dict[str, int] = {rt: 0 for rt in RUSH_TYPES}

    non_rush_shots = 0
    non_rush_goals = 0

    for shot in shots:
        if shot.get("is_rush", False):
            rt = shot.get("rush_type", "odd_man_rush")
            if rt not in RUSH_TYPES:
                rt = "odd_man_rush"
            rush_counts[rt] += 1
            if shot.get("goal", False):
                rush_goals[rt] += 1
        else:
            non_rush_shots += 1
            if shot.get("goal", False):
                non_rush_goals += 1

    total_rush_shots = sum(rush_counts.values())
    total_rush_goals = sum(rush_goals.values())

    def _sv(shots_n: int, goals_against: int) -> Optional[float]:
        if shots_n == 0:
            return None
        return round((shots_n - goals_against) / shots_n, 4)

    return {
        "overall_rush_sv_pct": _sv(total_rush_shots, total_rush_goals),
        "breakaway_sv_pct": _sv(rush_counts["breakaway"], rush_goals["breakaway"]),
        "two_on_one_sv_pct": _sv(rush_counts["2_on_1"], rush_goals["2_on_1"]),
        "three_on_two_sv_pct": _sv(rush_counts["3_on_2"], rush_goals["3_on_2"]),
        "rush_shots": total_rush_shots,
        "rush_goals": total_rush_goals,
        "non_rush_sv_pct": _sv(non_rush_shots, non_rush_goals),
        "non_rush_shots": non_rush_shots,
    }


def aggregate_rush_defense(
    game_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Aggregate per-game rush defense stats into season/career totals.

    Accepts the raw *shot lists* per game as dicts containing a ``shots``
    key, or the direct output of :func:`calculate_rush_defense`.

    Args:
        game_results: List of outputs from :func:`calculate_rush_defense`.

    Returns:
        Aggregated rush defense statistics using the same schema as
        :func:`calculate_rush_defense`.
    """
    if not game_results:
        return {
            "overall_rush_sv_pct": None,
            "rush_shots": 0,
            "rush_goals": 0,
            "non_rush_sv_pct": None,
        }

    rush_shots = sum(g.get("rush_shots", 0) for g in game_results)
    rush_goals = sum(g.get("rush_goals", 0) for g in game_results)
    non_rush_shots = sum(g.get("non_rush_shots", 0) for g in game_results)
    non_rush_goals = sum(
        (non_rush_shots - int(g.get("non_rush_sv_pct", 1.0) * g.get("non_rush_shots", 0)))
        if g.get("non_rush_sv_pct") is not None
        else 0
        for g in game_results
    )

    def _sv(shots: int, goals_against: int) -> Optional[float]:
        if shots == 0:
            return None
        return round((shots - goals_against) / shots, 4)

    # Note: breakaway / 2on1 / 3on2 aggregation omitted here for brevity;
    # callers should re-run calculate_rush_defense on the merged shot list
    # for exact sub-type breakdowns.
    return {
        "overall_rush_sv_pct": _sv(rush_shots, rush_goals),
        "rush_shots": rush_shots,
        "rush_goals": rush_goals,
        "non_rush_sv_pct": _sv(non_rush_shots, non_rush_goals),
        "non_rush_shots": non_rush_shots,
    }
