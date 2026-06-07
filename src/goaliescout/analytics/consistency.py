"""Performance Volatility Index (Consistency) analytics.

Measures how consistent a goalie is game-to-game by computing the
standard deviation of their per-game save percentage and translating
that into a 0-100 consistency score (100 = perfectly consistent).
"""

import math
import statistics
from typing import Dict, Any, List, Optional


def calculate_consistency(
    game_sv_pcts: List[float],
    min_games: int = 5,
) -> Dict[str, Any]:
    """Calculate the Performance Volatility Index from game-level SV%.

    Args:
        game_sv_pcts: List of per-game save percentages (each in [0, 1]).
        min_games: Minimum number of games required for a meaningful
            consistency score.

    Returns:
        Dictionary with keys:

        - ``consistency_score`` — 0-100 score (100 = perfectly stable)
        - ``std_dev`` — standard deviation of per-game save percentage
        - ``mean_sv_pct`` — average per-game save percentage
        - ``games`` — number of games used
        - ``confidence`` — ``'high'``, ``'medium'``, or ``'low'`` based
          on sample size
        - ``streak_info`` — dict with current hot/cold streak details

    Raises:
        ValueError: If any value in ``game_sv_pcts`` is outside [0, 1].
    """
    for v in game_sv_pcts:
        if not (0.0 <= v <= 1.0):
            raise ValueError(
                f"All save percentages must be in [0, 1], got {v}"
            )

    n = len(game_sv_pcts)

    if n == 0:
        return {
            "consistency_score": None,
            "std_dev": None,
            "mean_sv_pct": None,
            "games": 0,
            "confidence": "none",
            "streak_info": {"type": "none", "length": 0},
        }

    mean_sv = statistics.mean(game_sv_pcts)

    if n < 2:
        return {
            "consistency_score": 100.0,
            "std_dev": 0.0,
            "mean_sv_pct": round(mean_sv, 4),
            "games": n,
            "confidence": "low",
            "streak_info": _streak_info(game_sv_pcts, mean_sv),
        }

    std_dev = statistics.stdev(game_sv_pcts)

    # Convert std_dev to a 0-100 score:
    # A std_dev of 0 → 100; a std_dev of 0.05 (~5pp) → ~0
    # Using exponential decay: score = 100 * exp(-40 * std_dev)
    consistency_score = round(100.0 * math.exp(-40.0 * std_dev), 2)
    consistency_score = max(0.0, min(100.0, consistency_score))

    confidence: str
    if n >= 20:
        confidence = "high"
    elif n >= min_games:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "consistency_score": consistency_score,
        "std_dev": round(std_dev, 6),
        "mean_sv_pct": round(mean_sv, 4),
        "games": n,
        "confidence": confidence,
        "streak_info": _streak_info(game_sv_pcts, mean_sv),
    }


def _streak_info(game_sv_pcts: List[float], mean_sv: float) -> Dict[str, Any]:
    """Determine current hot/cold streak from game results.

    A 'hot' game is one where SV% exceeds the career mean; 'cold' is below.

    Args:
        game_sv_pcts: Ordered list of per-game save percentages.
        mean_sv: Mean save percentage to use as threshold.

    Returns:
        Dict with ``type`` (``'hot'``, ``'cold'``, ``'neutral'``) and
        ``length`` (number of consecutive games).
    """
    if not game_sv_pcts:
        return {"type": "none", "length": 0}

    streak_type = "hot" if game_sv_pcts[-1] >= mean_sv else "cold"
    length = 0

    for sv in reversed(game_sv_pcts):
        if streak_type == "hot" and sv >= mean_sv:
            length += 1
        elif streak_type == "cold" and sv < mean_sv:
            length += 1
        else:
            break

    return {"type": streak_type, "length": length}


def calculate_consistency_from_games(
    games: List[Dict[str, Any]],
    min_games: int = 5,
) -> Dict[str, Any]:
    """Convenience wrapper to compute consistency from raw game records.

    Each game dict must contain either:
    - ``sv_pct`` — pre-computed save percentage float in [0, 1], or
    - ``saves`` and ``shots`` — to compute SV% on-the-fly.

    Args:
        games: List of game record dictionaries.
        min_games: Minimum games for a meaningful consistency score.

    Returns:
        Output of :func:`calculate_consistency`.
    """
    sv_pcts: List[float] = []
    for g in games:
        if "sv_pct" in g:
            sv_pcts.append(float(g["sv_pct"]))
        elif g.get("shots", 0) > 0:
            sv_pcts.append(g["saves"] / g["shots"])
    return calculate_consistency(sv_pcts, min_games=min_games)
