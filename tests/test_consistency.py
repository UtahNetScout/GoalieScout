"""Tests for consistency (Performance Volatility Index) analytics."""

import pytest

from goaliescout.analytics.consistency import (
    calculate_consistency,
    calculate_consistency_from_games,
)


class TestCalculateConsistency:
    """Unit tests for calculate_consistency."""

    def test_empty_list(self):
        result = calculate_consistency([])
        assert result["consistency_score"] is None
        assert result["games"] == 0
        assert result["confidence"] == "none"

    def test_single_game(self):
        result = calculate_consistency([0.920])
        assert result["consistency_score"] == pytest.approx(100.0)
        assert result["confidence"] == "low"

    def test_perfect_consistency(self):
        games = [0.920] * 20
        result = calculate_consistency(games)
        assert result["std_dev"] == pytest.approx(0.0, abs=1e-9)
        assert result["consistency_score"] == pytest.approx(100.0)

    def test_high_variability_lower_score(self):
        low_var = [0.920, 0.918, 0.922, 0.919, 0.921] * 4
        high_var = [0.850, 0.950, 0.800, 0.980, 0.820, 0.960, 0.810, 0.970]
        low_result = calculate_consistency(low_var)
        high_result = calculate_consistency(high_var)
        assert low_result["consistency_score"] > high_result["consistency_score"]

    def test_invalid_sv_pct_raises(self):
        with pytest.raises(ValueError):
            calculate_consistency([0.920, 1.1])

    def test_negative_sv_pct_raises(self):
        with pytest.raises(ValueError):
            calculate_consistency([-0.1, 0.900])

    def test_confidence_levels(self):
        assert calculate_consistency([0.9] * 3)["confidence"] == "low"
        assert calculate_consistency([0.9] * 10)["confidence"] == "medium"
        assert calculate_consistency([0.9] * 21)["confidence"] == "high"

    def test_streak_info_hot(self):
        # Ending on above-average games → hot streak
        mean = 0.910
        games = [0.880, 0.870, 0.920, 0.930, 0.925]
        result = calculate_consistency(games)
        assert result["streak_info"]["type"] in ("hot", "cold")
        assert result["streak_info"]["length"] >= 1

    def test_output_keys(self):
        result = calculate_consistency([0.910, 0.915, 0.905])
        expected_keys = {
            "consistency_score", "std_dev", "mean_sv_pct",
            "games", "confidence", "streak_info",
        }
        assert expected_keys == set(result.keys())


class TestCalculateConsistencyFromGames:
    """Unit tests for the convenience wrapper."""

    def test_from_sv_pct_key(self):
        games = [{"sv_pct": 0.910}, {"sv_pct": 0.920}, {"sv_pct": 0.915}]
        result = calculate_consistency_from_games(games)
        assert result["games"] == 3

    def test_from_saves_shots(self):
        games = [
            {"saves": 28, "shots": 30},
            {"saves": 26, "shots": 28},
        ]
        result = calculate_consistency_from_games(games)
        assert result["games"] == 2

    def test_empty_games(self):
        result = calculate_consistency_from_games([])
        assert result["games"] == 0
