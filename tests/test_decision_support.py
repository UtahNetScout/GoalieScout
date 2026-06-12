"""Tests for transparent decision-support workflows."""

import pytest

from goaliescout.analytics.decision_support import (
    DEMO_CANDIDATES,
    SCENARIO_WEIGHTS,
    build_decision_brief,
    build_sensitivity_rows,
    normalize_weights,
    rank_candidates,
)


def test_normalize_weights_sums_to_one():
    result = normalize_weights({"gsax": 25, "hd_sv_pct": 20})
    assert sum(result.values()) == pytest.approx(1.0)
    assert result["gsax"] > result["hd_sv_pct"]


def test_normalize_weights_rejects_all_zero():
    with pytest.raises(ValueError):
        normalize_weights({})


def test_rank_candidates_returns_score_and_completeness():
    rankings = rank_candidates(
        DEMO_CANDIDATES,
        SCENARIO_WEIGHTS["Balanced evaluation"],
    )

    assert len(rankings) == 3
    assert rankings[0]["black_ops_score"] >= rankings[-1]["black_ops_score"]
    assert all(0 <= item["data_completeness"] <= 1 for item in rankings)


def test_missing_component_remains_visible():
    rankings = rank_candidates(
        DEMO_CANDIDATES,
        SCENARIO_WEIGHTS["Balanced evaluation"],
    )
    atlantic = next(item for item in rankings if item["name"] == "Candidate Atlantic")

    assert atlantic["data_completeness"] < 1.0
    assert atlantic["component_scores"]["puck_handling"] == 50.0


def test_sensitivity_rows_cover_every_candidate_and_scenario():
    rows = build_sensitivity_rows(DEMO_CANDIDATES)
    assert len(rows) == len(DEMO_CANDIDATES) * len(SCENARIO_WEIGHTS)
    assert {row["Scenario"] for row in rows} == set(SCENARIO_WEIGHTS)


def test_decision_brief_discloses_demo_and_review_status():
    rankings = rank_candidates(
        DEMO_CANDIDATES,
        SCENARIO_WEIGHTS["Balanced evaluation"],
    )
    brief = build_decision_brief(
        "Balanced evaluation",
        rankings,
        SCENARIO_WEIGHTS["Balanced evaluation"],
        {
            "Evidence reviewed": True,
            "Video review complete": False,
        },
    )

    assert "anonymized illustrative candidate packets" in brief
    assert "Review incomplete" in brief
    assert rankings[0]["name"] in brief
    assert "Missing inputs receive a neutral score" in brief
