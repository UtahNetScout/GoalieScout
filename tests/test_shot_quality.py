"""Tests for the shot_quality (xG) model."""

import math
import pytest

from goaliescout.analytics.shot_quality import (
    SHOT_TYPE_WEIGHTS,
    calculate_shot_xg,
    classify_shot_danger,
    evaluate_shot_batch,
)


class TestCalculateShotXg:
    """Unit tests for calculate_shot_xg."""

    def test_close_shot_has_higher_xg_than_distant(self):
        close = calculate_shot_xg(distance=10.0, angle=0.0)
        far = calculate_shot_xg(distance=60.0, angle=0.0)
        assert close > far

    def test_direct_angle_higher_than_side_angle(self):
        direct = calculate_shot_xg(distance=20.0, angle=0.0)
        side = calculate_shot_xg(distance=20.0, angle=80.0)
        assert direct > side

    def test_tip_shot_multiplier(self):
        wrist = calculate_shot_xg(distance=20.0, angle=0.0, shot_type="wrist")
        tip = calculate_shot_xg(distance=20.0, angle=0.0, shot_type="tip")
        assert tip > wrist

    def test_rebound_multiplier(self):
        base = calculate_shot_xg(distance=15.0, angle=10.0)
        rebound = calculate_shot_xg(distance=15.0, angle=10.0, is_rebound=True)
        assert rebound > base

    def test_power_play_multiplier(self):
        es = calculate_shot_xg(distance=20.0, angle=0.0)
        pp = calculate_shot_xg(distance=20.0, angle=0.0, is_power_play=True)
        assert pp > es

    def test_result_is_probability(self):
        xg = calculate_shot_xg(distance=5.0, angle=0.0, is_rebound=True, is_rush=True)
        assert 0.0 <= xg <= 1.0

    def test_negative_distance_raises(self):
        with pytest.raises(ValueError):
            calculate_shot_xg(distance=-1.0, angle=0.0)

    def test_invalid_angle_raises(self):
        with pytest.raises(ValueError):
            calculate_shot_xg(distance=20.0, angle=91.0)

    def test_custom_model_weights(self):
        default = calculate_shot_xg(distance=15.0, angle=0.0, is_rebound=True)
        custom = calculate_shot_xg(
            distance=15.0, angle=0.0, is_rebound=True,
            model_weights={"rebound": 3.0}
        )
        assert custom > default

    def test_unknown_shot_type_falls_back_to_default(self):
        xg = calculate_shot_xg(distance=20.0, angle=0.0, shot_type="mystery")
        assert 0.0 <= xg <= 1.0


class TestClassifyShotDanger:
    """Unit tests for classify_shot_danger."""

    def test_close_centre_is_high(self):
        assert classify_shot_danger(10.0, 0.0) == "high"

    def test_very_long_shot_is_low(self):
        assert classify_shot_danger(90.0, 5.0) == "low"

    def test_mid_range_is_medium(self):
        result = classify_shot_danger(40.0, 20.0)
        assert result in ("medium", "low")


class TestEvaluateShotBatch:
    """Unit tests for evaluate_shot_batch."""

    def test_adds_xg_key(self):
        shots = [{"distance": 20.0, "angle": 5.0}]
        results = evaluate_shot_batch(shots)
        assert "xg" in results[0]

    def test_adds_danger_zone_key(self):
        shots = [{"distance": 20.0, "angle": 5.0}]
        results = evaluate_shot_batch(shots)
        assert "danger_zone" in results[0]

    def test_empty_batch_returns_empty(self):
        assert evaluate_shot_batch([]) == []

    def test_original_keys_preserved(self):
        shots = [{"distance": 25.0, "angle": 10.0, "player": "test"}]
        results = evaluate_shot_batch(shots)
        assert results[0]["player"] == "test"
