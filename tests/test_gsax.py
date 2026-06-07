"""Tests for GSAx (Goals Saved Above Expected) calculations."""

import pytest

from goaliescout.analytics.gsax import (
    aggregate_gsax,
    calculate_game_gsax,
    calculate_gsax,
)


def _make_shots(n: int, distance: float = 30.0, angle: float = 0.0):
    """Helper to build a list of identical shot dicts."""
    return [{"distance": distance, "angle": angle} for _ in range(n)]


class TestCalculateGsax:
    """Unit tests for calculate_gsax."""

    def test_perfect_shutout_positive_gsax(self):
        shots = _make_shots(20)
        result = calculate_gsax(shots, actual_goals_against=0)
        assert result["gsax"] > 0

    def test_allowing_all_expected_goals_near_zero(self):
        shots = _make_shots(10, distance=30.0, angle=0.0)
        xga = result = calculate_gsax(shots, 0)["xga"]
        # Allow all the xGA — GSAx should be very close to -xga
        result2 = calculate_gsax(shots, round(xga))
        assert abs(result2["gsax"]) < xga + 0.1

    def test_negative_goals_against_raises(self):
        with pytest.raises(ValueError):
            calculate_gsax([], -1)

    def test_output_keys(self):
        result = calculate_gsax(_make_shots(5), 1)
        assert {"xga", "actual_ga", "gsax", "shots_faced"} == set(result.keys())

    def test_shots_faced_count(self):
        shots = _make_shots(15)
        result = calculate_gsax(shots, 0)
        assert result["shots_faced"] == 15

    def test_empty_shots(self):
        result = calculate_gsax([], 0)
        assert result["xga"] == 0.0
        assert result["gsax"] == 0.0


class TestCalculateGameGsax:
    """Unit tests for calculate_game_gsax."""

    def test_returns_list(self):
        games = [
            {"shots": _make_shots(25), "goals_against": 2, "date": "2024-01-01"},
        ]
        results = calculate_game_gsax(games)
        assert isinstance(results, list)
        assert len(results) == 1

    def test_preserves_game_keys(self):
        games = [{"shots": _make_shots(20), "goals_against": 1, "date": "2024-02-01"}]
        results = calculate_game_gsax(games)
        assert results[0]["date"] == "2024-02-01"

    def test_shots_key_removed_from_output(self):
        games = [{"shots": _make_shots(20), "goals_against": 1}]
        results = calculate_game_gsax(games)
        assert "shots" not in results[0]


class TestAggregateGsax:
    """Unit tests for aggregate_gsax."""

    def test_empty_list(self):
        result = aggregate_gsax([])
        assert result["games"] == 0
        assert result["total_gsax"] == 0.0

    def test_aggregated_totals(self):
        game_results = [
            {"xga": 1.5, "actual_ga": 1, "gsax": 0.5, "shots_faced": 30},
            {"xga": 2.0, "actual_ga": 3, "gsax": -1.0, "shots_faced": 35},
        ]
        result = aggregate_gsax(game_results)
        assert result["games"] == 2
        assert abs(result["total_xga"] - 3.5) < 0.01
        assert result["total_ga"] == 4
        assert abs(result["total_gsax"] - (-0.5)) < 0.01

    def test_gsax_per_game(self):
        game_results = [
            {"xga": 1.0, "actual_ga": 1, "gsax": 0.0},
            {"xga": 2.0, "actual_ga": 2, "gsax": 0.0},
        ]
        result = aggregate_gsax(game_results)
        assert result["gsax_per_game"] == 0.0
