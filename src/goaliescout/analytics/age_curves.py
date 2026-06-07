"""Development Trajectory Prediction (Age Curves).

Models expected development based on age and current performance,
comparing to historical NHL goalie development curves, and projects
future performance windows (peak age, decline onset).
"""

import math
from typing import Dict, Any, List, Optional, Tuple


# Historical NHL goalie development curve parameters
# Based on published research on goalie aging curves.
# Save percentage peaks around ages 26-29 and declines thereafter.
_PEAK_AGE: float = 27.5
_PEAK_SV_PCT: float = 0.920  # league-average peak SV%
_DEVELOPMENT_RATE: float = 0.003  # SV% gained per year pre-peak
_DECLINE_RATE: float = 0.002   # SV% lost per year post-peak


def _league_curve_sv_pct(age: float) -> float:
    """Return the league-average expected SV% for a given age.

    Uses a simple triangular model peaking at :data:`_PEAK_AGE`.

    Args:
        age: Player age in years.

    Returns:
        Expected SV% for the age, in [0.880, 0.920].
    """
    if age <= _PEAK_AGE:
        delta = (_PEAK_AGE - age) * _DEVELOPMENT_RATE
    else:
        delta = (age - _PEAK_AGE) * _DECLINE_RATE
    return round(max(0.880, _PEAK_SV_PCT - delta), 4)


def project_development(
    current_age: float,
    current_sv_pct: float,
    seasons_ahead: int = 5,
    games_played: int = 0,
) -> Dict[str, Any]:
    """Project a goalie's development trajectory over the next N seasons.

    The projection assumes the goalie's SV% will converge toward the
    age-curve expectation over time, adjusted by their current delta
    above or below the curve.

    Args:
        current_age: Player's current age in years.
        current_sv_pct: Current career / recent-season save percentage.
        seasons_ahead: Number of future seasons to project.
        games_played: Career games played (used for confidence weight).

    Returns:
        Dictionary with keys:

        - ``current_age`` — input age
        - ``current_sv_pct`` — input save percentage
        - ``expected_sv_pct_now`` — league-curve SV% at current age
        - ``delta_vs_curve`` — how far above/below the curve the goalie is
        - ``peak_age_projection`` — projected age of peak performance
        - ``seasons`` — list of per-season projections
        - ``development_phase`` — ``'developing'``, ``'prime'``, or
          ``'declining'``
        - ``confidence`` — ``'high'``, ``'medium'``, or ``'low'``

    Raises:
        ValueError: If ``current_age`` is not in [14, 50] or
            ``current_sv_pct`` is not in [0, 1].
    """
    if not (14.0 <= current_age <= 50.0):
        raise ValueError(f"current_age must be in [14, 50], got {current_age}")
    if not (0.0 <= current_sv_pct <= 1.0):
        raise ValueError(
            f"current_sv_pct must be in [0, 1], got {current_sv_pct}"
        )

    expected_now = _league_curve_sv_pct(current_age)
    delta = current_sv_pct - expected_now

    # Determine development phase
    if current_age < 24:
        phase = "developing"
    elif current_age <= 30:
        phase = "prime"
    else:
        phase = "declining"

    # Confidence based on sample size
    if games_played >= 100:
        confidence = "high"
    elif games_played >= 30:
        confidence = "medium"
    else:
        confidence = "low"

    # Regress individual delta toward 0 over time (regression to the mean)
    regression_rate = 0.15  # 15% regression per season

    seasons: List[Dict[str, Any]] = []
    projected_delta = delta
    for i in range(1, seasons_ahead + 1):
        projected_age = current_age + i
        projected_delta *= (1.0 - regression_rate)
        projected_sv = _league_curve_sv_pct(projected_age) + projected_delta
        projected_sv = round(max(0.880, min(0.960, projected_sv)), 4)
        seasons.append({
            "season_offset": i,
            "projected_age": round(projected_age, 1),
            "projected_sv_pct": projected_sv,
            "league_curve_sv_pct": _league_curve_sv_pct(projected_age),
        })

    # Simple peak projection
    if current_age < _PEAK_AGE:
        peak_projection = _PEAK_AGE + (delta / _DEVELOPMENT_RATE) * 0.1
    else:
        peak_projection = current_age - 1  # already past peak

    return {
        "current_age": current_age,
        "current_sv_pct": current_sv_pct,
        "expected_sv_pct_now": expected_now,
        "delta_vs_curve": round(delta, 4),
        "peak_age_projection": round(peak_projection, 1),
        "seasons": seasons,
        "development_phase": phase,
        "confidence": confidence,
    }


def age_curve_score(
    current_age: float,
    current_sv_pct: float,
    games_played: int = 0,
) -> float:
    """Return a 0-100 development trajectory score.

    The score reflects both current quality relative to age expectations
    and projected future upside.

    Args:
        current_age: Player age in years.
        current_sv_pct: Current save percentage.
        games_played: Career games played (for confidence weighting).

    Returns:
        Trajectory score in [0, 100].
    """
    expected_now = _league_curve_sv_pct(current_age)
    delta = current_sv_pct - expected_now

    # Normalise delta: +0.020 above curve → +20 points; -0.020 → -20 points
    delta_score = delta * 1000.0

    # Base score: comparison to curve
    base = 50.0 + delta_score

    # Bonus/penalty for development phase
    if current_age < 24:
        base += 10.0  # upside bonus for young goalies
    elif current_age > 33:
        base -= 5.0   # small discount for older goalies

    # Sample-size confidence discount
    if games_played < 10:
        base -= 10.0
    elif games_played < 30:
        base -= 5.0

    return round(max(0.0, min(100.0, base)), 2)
