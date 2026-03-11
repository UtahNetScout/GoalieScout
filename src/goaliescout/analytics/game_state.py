"""Game-state split analytics.

Breaks down all key goalie metrics by game state: even strength (5v5),
power play (opponent on PP), penalty kill (own PK), empty net, and
score-effect buckets (leading / trailing / tied).
"""

from typing import Dict, Any, List, Optional

# Game-state labels
STRENGTH_STATES = {"even_strength", "power_play", "penalty_kill", "empty_net", "other"}
SCORE_STATES = {"leading", "trailing", "tied"}


def _sv_pct(shots: int, goals: int) -> Optional[float]:
    """Safe save-percentage helper."""
    if shots == 0:
        return None
    return round((shots - goals) / shots, 4)


def calculate_game_state_splits(
    shots: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Calculate save percentages split by game state.

    Each shot dict should contain:

    - ``goal`` — bool, whether the shot resulted in a goal
    - ``strength_state`` — str, one of ``'even_strength'``,
      ``'power_play'`` (opponent PP), ``'penalty_kill'`` (own PK),
      ``'empty_net'`` (defaults to ``'even_strength'`` if missing)
    - ``score_state`` — str, one of ``'leading'``, ``'trailing'``,
      ``'tied'`` (defaults to ``'tied'`` if missing)

    Args:
        shots: List of shot dictionaries.

    Returns:
        Dictionary containing save percentages and shot counts for each
        game-state combination.  Top-level keys:

        - ``by_strength`` — dict keyed by strength state
        - ``by_score_state`` — dict keyed by score state
        - ``overall`` — overall sv_pct, shots, goals
    """
    strength_shots: Dict[str, int] = {s: 0 for s in STRENGTH_STATES}
    strength_goals: Dict[str, int] = {s: 0 for s in STRENGTH_STATES}
    score_shots: Dict[str, int] = {s: 0 for s in SCORE_STATES}
    score_goals: Dict[str, int] = {s: 0 for s in SCORE_STATES}

    total_shots = 0
    total_goals = 0

    for shot in shots:
        strength = shot.get("strength_state", "even_strength")
        if strength not in STRENGTH_STATES:
            strength = "other"
        score = shot.get("score_state", "tied")
        if score not in SCORE_STATES:
            score = "tied"
        is_goal = bool(shot.get("goal", False))

        strength_shots[strength] += 1
        score_shots[score] += 1
        total_shots += 1

        if is_goal:
            strength_goals[strength] += 1
            score_goals[score] += 1
            total_goals += 1

    by_strength = {}
    for state in STRENGTH_STATES:
        by_strength[state] = {
            "sv_pct": _sv_pct(strength_shots[state], strength_goals[state]),
            "shots": strength_shots[state],
            "goals": strength_goals[state],
        }

    by_score = {}
    for state in SCORE_STATES:
        by_score[state] = {
            "sv_pct": _sv_pct(score_shots[state], score_goals[state]),
            "shots": score_shots[state],
            "goals": score_goals[state],
        }

    return {
        "by_strength": by_strength,
        "by_score_state": by_score,
        "overall": {
            "sv_pct": _sv_pct(total_shots, total_goals),
            "shots": total_shots,
            "goals": total_goals,
        },
    }


def aggregate_game_state_splits(
    game_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Aggregate per-game game-state splits into season/career totals.

    Args:
        game_results: List of outputs from :func:`calculate_game_state_splits`.

    Returns:
        Aggregated game-state splits using the same schema.
    """
    agg_strength_shots: Dict[str, int] = {s: 0 for s in STRENGTH_STATES}
    agg_strength_goals: Dict[str, int] = {s: 0 for s in STRENGTH_STATES}
    agg_score_shots: Dict[str, int] = {s: 0 for s in SCORE_STATES}
    agg_score_goals: Dict[str, int] = {s: 0 for s in SCORE_STATES}
    total_shots = 0
    total_goals = 0

    for game in game_results:
        for state in STRENGTH_STATES:
            entry = game.get("by_strength", {}).get(state, {})
            agg_strength_shots[state] += entry.get("shots", 0)
            agg_strength_goals[state] += entry.get("goals", 0)
        for state in SCORE_STATES:
            entry = game.get("by_score_state", {}).get(state, {})
            agg_score_shots[state] += entry.get("shots", 0)
            agg_score_goals[state] += entry.get("goals", 0)
        overall = game.get("overall", {})
        total_shots += overall.get("shots", 0)
        total_goals += overall.get("goals", 0)

    by_strength = {
        s: {
            "sv_pct": _sv_pct(agg_strength_shots[s], agg_strength_goals[s]),
            "shots": agg_strength_shots[s],
            "goals": agg_strength_goals[s],
        }
        for s in STRENGTH_STATES
    }
    by_score = {
        s: {
            "sv_pct": _sv_pct(agg_score_shots[s], agg_score_goals[s]),
            "shots": agg_score_shots[s],
            "goals": agg_score_goals[s],
        }
        for s in SCORE_STATES
    }

    return {
        "by_strength": by_strength,
        "by_score_state": by_score,
        "overall": {
            "sv_pct": _sv_pct(total_shots, total_goals),
            "shots": total_shots,
            "goals": total_goals,
        },
    }
