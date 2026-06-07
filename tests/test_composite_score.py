"""Tests for the Black Ops Score composite rating."""

import pytest

from goaliescout.analytics.composite_score import (
    WEIGHTS,
    calculate_black_ops_score,
    classify_tier,
)


class TestClassifyTier:
    """Unit tests for classify_tier."""

    def test_elite_tier(self):
        result = classify_tier(95.0)
        assert result["tier"] == "Elite"

    def test_above_average_tier(self):
        result = classify_tier(85.0)
        assert result["tier"] == "Above Average"

    def test_average_tier(self):
        result = classify_tier(75.0)
        assert result["tier"] == "Average"

    def test_below_average_tier(self):
        result = classify_tier(65.0)
        assert result["tier"] == "Below Average"

    def test_needs_improvement_tier(self):
        result = classify_tier(30.0)
        assert result["tier"] == "Needs Improvement"

    def test_boundary_90(self):
        assert classify_tier(90.0)["tier"] == "Elite"

    def test_boundary_80(self):
        assert classify_tier(80.0)["tier"] == "Above Average"


class TestCalculateBlackOpsScore:
    """Unit tests for calculate_black_ops_score."""

    def test_returns_score_in_range(self):
        result = calculate_black_ops_score(
            gsax_per_game=0.2,
            hd_sv_pct=0.910,
            controlled_rebound_rate=0.70,
            consistency_score=75.0,
            movement_score=65.0,
            puck_handling_score=60.0,
            development_score=55.0,
            games_played=50,
        )
        assert 0.0 <= result["black_ops_score"] <= 100.0

    def test_all_none_returns_neutral_score(self):
        result = calculate_black_ops_score()
        # All components imputed as 50 → score should be 50
        assert result["black_ops_score"] == pytest.approx(50.0, abs=1.0)

    def test_excellent_inputs_high_score(self):
        result = calculate_black_ops_score(
            gsax_per_game=0.5,
            hd_sv_pct=0.960,
            controlled_rebound_rate=0.90,
            consistency_score=95.0,
            movement_score=90.0,
            puck_handling_score=90.0,
            development_score=90.0,
            games_played=60,
        )
        assert result["black_ops_score"] >= 80.0

    def test_poor_inputs_low_score(self):
        result = calculate_black_ops_score(
            gsax_per_game=-0.5,
            hd_sv_pct=0.820,
            controlled_rebound_rate=0.40,
            consistency_score=10.0,
            movement_score=10.0,
            puck_handling_score=10.0,
            development_score=10.0,
            games_played=20,
        )
        assert result["black_ops_score"] <= 30.0

    def test_confidence_interval_present(self):
        result = calculate_black_ops_score(games_played=30)
        assert "confidence_interval" in result
        ci = result["confidence_interval"]
        assert ci["lower"] <= result["black_ops_score"] <= ci["upper"]

    def test_confidence_interval_widens_with_fewer_games(self):
        wide = calculate_black_ops_score(games_played=5)
        narrow = calculate_black_ops_score(games_played=100)
        wide_range = wide["confidence_interval"]["upper"] - wide["confidence_interval"]["lower"]
        narrow_range = narrow["confidence_interval"]["upper"] - narrow["confidence_interval"]["lower"]
        assert wide_range > narrow_range

    def test_component_scores_present(self):
        result = calculate_black_ops_score(gsax_per_game=0.1)
        assert set(result["component_scores"].keys()) == set(WEIGHTS.keys())

    def test_tier_is_assigned(self):
        result = calculate_black_ops_score(gsax_per_game=0.3, games_played=40)
        assert "tier" in result
        assert isinstance(result["tier"], str)

    def test_data_completeness_with_all_none(self):
        result = calculate_black_ops_score()
        assert result["data_completeness"] == 0.0

    def test_data_completeness_partial(self):
        result = calculate_black_ops_score(gsax_per_game=0.1, hd_sv_pct=0.900)
        assert 0.0 < result["data_completeness"] < 1.0

    def test_custom_weights_invalid_raises(self):
        with pytest.raises(ValueError):
            calculate_black_ops_score(
                custom_weights={"gsax": 0.6, "hd_sv_pct": 0.5}  # sums to 1.1 → invalid
            )

    def test_weights_sum_to_one(self):
        assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9
