"""Goals Saved Above Expected (GSAx) calculations.

GSAx measures how many more (or fewer) goals a goalie saved compared
to what an average goalie would be expected to save given the same
shot attempts.

    GSAx = xGA - Actual GA

A positive GSAx means the goalie outperformed expectations; a negative
value means they allowed more goals than expected.
"""

from typing import Dict, Any, List, Optional

from .shot_quality import calculate_shot_xg


def calculate_gsax(
    shots_faced: List[Dict[str, Any]],
    actual_goals_against: int,
    model_weights: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """Calculate Goals Saved Above Expected for a set of shots.

    Each shot dictionary should contain at minimum ``distance`` and
    ``angle`` keys understood by :func:`~goaliescout.analytics.shot_quality.calculate_shot_xg`.
    Any additional shot-quality keys (``shot_type``, ``is_rebound``,
    ``is_rush``, ``is_power_play``, ``has_screen``) are forwarded.

    Args:
        shots_faced: List of shot dictionaries faced by the goalie.
        actual_goals_against: Number of goals the goalie actually allowed.
        model_weights: Optional overrides for the xG model multipliers.

    Returns:
        Dictionary with keys:

        - ``xga`` — total expected goals against
        - ``actual_ga`` — goals actually allowed
        - ``gsax`` — Goals Saved Above Expected  (positive = better)
        - ``shots_faced`` — total number of shot attempts evaluated
        - ``gsax_per_60`` — GSAx per 60 minutes (requires ``toi_minutes``
          to be set elsewhere; defaults to NaN when not calculable)

    Raises:
        ValueError: If ``actual_goals_against`` is negative.
    """
    if actual_goals_against < 0:
        raise ValueError(
            f"actual_goals_against must be non-negative, got {actual_goals_against}"
        )

    xga: float = 0.0
    for shot in shots_faced:
        xga += calculate_shot_xg(
            distance=shot.get("distance", 30.0),
            angle=shot.get("angle", 0.0),
            shot_type=shot.get("shot_type", "wrist"),
            is_rebound=shot.get("is_rebound", False),
            is_rush=shot.get("is_rush", False),
            is_power_play=shot.get("is_power_play", False),
            has_screen=shot.get("has_screen", False),
            model_weights=model_weights,
        )

    gsax = xga - actual_goals_against

    return {
        "xga": round(xga, 4),
        "actual_ga": actual_goals_against,
        "gsax": round(gsax, 4),
        "shots_faced": len(shots_faced),
    }


def calculate_game_gsax(
    games: List[Dict[str, Any]],
    model_weights: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """Calculate per-game GSAx for a list of game records.

    Each game dict must contain:
    - ``shots`` — list of shot dicts (see :func:`calculate_gsax`)
    - ``goals_against`` — int, actual goals allowed in the game

    Optional keys used verbatim in output:
    - ``date``, ``opponent``, ``toi_minutes``

    Args:
        games: List of game record dictionaries.
        model_weights: Optional xG model weight overrides.

    Returns:
        List of per-game results, each containing the original game keys
        plus ``xga``, ``gsax``, and ``shots_faced``.
    """
    results = []
    for game in games:
        shots = game.get("shots", [])
        ga = game.get("goals_against", 0)
        gsax_data = calculate_gsax(shots, ga, model_weights)
        result = {k: v for k, v in game.items() if k != "shots"}
        result.update(gsax_data)
        results.append(result)
    return results


def aggregate_gsax(
    game_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Aggregate per-game GSAx results into season or career totals.

    Args:
        game_results: Output from :func:`calculate_game_gsax`.

    Returns:
        Dictionary with keys:

        - ``total_xga`` — cumulative expected goals against
        - ``total_ga`` — cumulative actual goals against
        - ``total_gsax`` — cumulative GSAx
        - ``games`` — number of games
        - ``gsax_per_game`` — average GSAx per game
        - ``gsax_per_60`` — GSAx per 60 minutes (if toi_minutes available)
    """
    if not game_results:
        return {
            "total_xga": 0.0,
            "total_ga": 0,
            "total_gsax": 0.0,
            "games": 0,
            "gsax_per_game": 0.0,
            "gsax_per_60": None,
        }

    total_xga = sum(g.get("xga", 0.0) for g in game_results)
    total_ga = sum(g.get("actual_ga", 0) for g in game_results)
    total_gsax = sum(g.get("gsax", 0.0) for g in game_results)
    games = len(game_results)

    total_toi = sum(
        g.get("toi_minutes", 0.0) for g in game_results if g.get("toi_minutes")
    )
    gsax_per_60 = (total_gsax / total_toi * 60) if total_toi > 0 else None

    return {
        "total_xga": round(total_xga, 4),
        "total_ga": total_ga,
        "total_gsax": round(total_gsax, 4),
        "games": games,
        "gsax_per_game": round(total_gsax / games, 4) if games else 0.0,
        "gsax_per_60": round(gsax_per_60, 4) if gsax_per_60 is not None else None,
    }
