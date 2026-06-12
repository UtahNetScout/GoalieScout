"""Decision-support helpers for transparent goalie comparisons.

The module uses the documented GoalieScout composite score and keeps
illustrative portfolio data separate from real player records.
"""

from typing import Any, Dict, Iterable, List, Mapping

from .composite_score import WEIGHTS, calculate_black_ops_score


COMPONENT_LABELS = {
    "gsax": "GSAx per game",
    "hd_sv_pct": "High-danger save percentage",
    "rebound_control": "Rebound control",
    "consistency": "Consistency",
    "movement": "Movement efficiency",
    "puck_handling": "Puck handling",
    "development": "Development trajectory",
}

SCENARIO_WEIGHTS: Dict[str, Dict[str, float]] = {
    "Balanced evaluation": dict(WEIGHTS),
    "Win-now shot stopping": {
        "gsax": 0.35,
        "hd_sv_pct": 0.30,
        "rebound_control": 0.15,
        "consistency": 0.10,
        "movement": 0.05,
        "puck_handling": 0.05,
        "development": 0.00,
    },
    "Low-variance workload": {
        "gsax": 0.20,
        "hd_sv_pct": 0.15,
        "rebound_control": 0.15,
        "consistency": 0.30,
        "movement": 0.10,
        "puck_handling": 0.10,
        "development": 0.00,
    },
    "Development upside": {
        "gsax": 0.15,
        "hd_sv_pct": 0.15,
        "rebound_control": 0.10,
        "consistency": 0.10,
        "movement": 0.15,
        "puck_handling": 0.10,
        "development": 0.25,
    },
}


DEMO_CANDIDATES: List[Dict[str, Any]] = [
    {
        "candidate_id": "candidate_north",
        "name": "Candidate North",
        "role": "Established starter",
        "sample": "Illustrative 54-game evaluation packet",
        "games_played": 54,
        "inputs": {
            "gsax_per_game": 0.31,
            "hd_sv_pct": 0.918,
            "controlled_rebound_rate": 0.78,
            "consistency_score": 84.0,
            "movement_score": 76.0,
            "puck_handling_score": 68.0,
            "development_score": 55.0,
        },
        "evidence": [
            "Strong shot-stopping packet across a starter-sized sample",
            "Above-average consistency and rebound-control inputs",
            "Development input is intentionally modest for a win-now profile",
        ],
        "open_questions": [
            "Validate east-west recovery on video",
            "Review workload management plan",
        ],
    },
    {
        "candidate_id": "candidate_central",
        "name": "Candidate Central",
        "role": "High-upside challenger",
        "sample": "Illustrative 31-game evaluation packet",
        "games_played": 31,
        "inputs": {
            "gsax_per_game": 0.18,
            "hd_sv_pct": 0.907,
            "controlled_rebound_rate": 0.70,
            "consistency_score": 67.0,
            "movement_score": 91.0,
            "puck_handling_score": 82.0,
            "development_score": 93.0,
        },
        "evidence": [
            "High movement, puck-handling, and development inputs",
            "Positive shot-stopping packet in a smaller sample",
            "Greater upside and greater uncertainty than Candidate North",
        ],
        "open_questions": [
            "Test whether movement efficiency holds under heavier workload",
            "Review low-save-percentage game clusters",
        ],
    },
    {
        "candidate_id": "candidate_atlantic",
        "name": "Candidate Atlantic",
        "role": "Stable tandem option",
        "sample": "Illustrative 43-game evaluation packet",
        "games_played": 43,
        "inputs": {
            "gsax_per_game": 0.08,
            "hd_sv_pct": 0.901,
            "controlled_rebound_rate": 0.82,
            "consistency_score": 92.0,
            "movement_score": 71.0,
            "puck_handling_score": None,
            "development_score": 61.0,
        },
        "evidence": [
            "Best consistency and rebound-control inputs in the demo set",
            "Moderate shot-stopping profile with a 43-game sample",
            "Puck-handling evidence is missing and neutrally imputed",
        ],
        "open_questions": [
            "Collect puck-handling observations",
            "Determine whether the profile scales to a starter workload",
        ],
    },
]


def normalize_weights(weights: Mapping[str, float]) -> Dict[str, float]:
    """Normalize non-negative component weights to sum to one."""
    cleaned = {key: max(0.0, float(weights.get(key, 0.0))) for key in WEIGHTS}
    total = sum(cleaned.values())
    if total <= 0:
        raise ValueError("At least one component weight must be greater than zero")
    return {key: value / total for key, value in cleaned.items()}


def score_candidate(
    candidate: Mapping[str, Any],
    weights: Mapping[str, float],
) -> Dict[str, Any]:
    """Score one candidate with the documented composite model."""
    inputs = candidate.get("inputs", {})
    result = calculate_black_ops_score(
        gsax_per_game=inputs.get("gsax_per_game"),
        hd_sv_pct=inputs.get("hd_sv_pct"),
        controlled_rebound_rate=inputs.get("controlled_rebound_rate"),
        consistency_score=inputs.get("consistency_score"),
        movement_score=inputs.get("movement_score"),
        puck_handling_score=inputs.get("puck_handling_score"),
        development_score=inputs.get("development_score"),
        games_played=int(candidate.get("games_played", 0)),
        custom_weights=normalize_weights(weights),
    )
    return {
        **result,
        "candidate_id": candidate.get("candidate_id"),
        "name": candidate.get("name", "Unknown candidate"),
        "role": candidate.get("role", "Unspecified"),
        "sample": candidate.get("sample", "Unknown sample"),
        "evidence": list(candidate.get("evidence", [])),
        "open_questions": list(candidate.get("open_questions", [])),
    }


def rank_candidates(
    candidates: Iterable[Mapping[str, Any]],
    weights: Mapping[str, float],
) -> List[Dict[str, Any]]:
    """Score and rank candidates from highest to lowest composite score."""
    scored = [score_candidate(candidate, weights) for candidate in candidates]
    return sorted(
        scored,
        key=lambda item: (
            item["black_ops_score"],
            item["data_completeness"],
            item["games_played"],
        ),
        reverse=True,
    )


def build_sensitivity_rows(
    candidates: Iterable[Mapping[str, Any]],
    scenarios: Mapping[str, Mapping[str, float]] = SCENARIO_WEIGHTS,
) -> List[Dict[str, Any]]:
    """Return one ranking row per candidate and documented scenario."""
    candidate_list = list(candidates)
    rows: List[Dict[str, Any]] = []
    for scenario, weights in scenarios.items():
        rankings = rank_candidates(candidate_list, weights)
        for position, result in enumerate(rankings, start=1):
            rows.append({
                "Scenario": scenario,
                "Rank": position,
                "Candidate": result["name"],
                "Score": result["black_ops_score"],
                "Completeness": result["data_completeness"],
            })
    return rows


def build_decision_brief(
    scenario_name: str,
    rankings: List[Mapping[str, Any]],
    weights: Mapping[str, float],
    review_status: Mapping[str, bool],
) -> str:
    """Build an exportable Markdown decision record."""
    leader = rankings[0]
    normalized = normalize_weights(weights)
    approved = all(review_status.values())
    status = "Ready for accountable human decision" if approved else "Review incomplete"
    weight_lines = "\n".join(
        f"- {COMPONENT_LABELS[key]}: {value * 100:.1f}%"
        for key, value in normalized.items()
    )
    ranking_lines = "\n".join(
        (
            f"{position}. **{item['name']}** - {item['black_ops_score']:.2f}/100, "
            f"{item['data_completeness'] * 100:.0f}% complete, "
            f"{item['tier']} tier"
        )
        for position, item in enumerate(rankings, start=1)
    )
    evidence_lines = "\n".join(f"- {item}" for item in leader["evidence"])
    question_lines = "\n".join(f"- {item}" for item in leader["open_questions"])
    review_lines = "\n".join(
        f"- {'Complete' if complete else 'Pending'}: {label}"
        for label, complete in review_status.items()
    )

    return f"""# GoalieScout Decision Brief

## Decision Status

**{status}**

This portfolio workflow uses anonymized illustrative candidate packets. It
demonstrates product behavior and does not represent real-player evaluation.

## Scenario

{scenario_name}

## Ranking

{ranking_lines}

## Recommended Candidate

**{leader['name']}** currently ranks first for this scenario. The recommendation
is conditional on the open questions and human review gates below.

### Supporting Evidence

{evidence_lines}

### Open Questions

{question_lines}

## Model Priorities

{weight_lines}

## Human Review Record

{review_lines}

## Responsible Use

The composite weights and normalization ranges are product hypotheses. Missing inputs receive a neutral score and remain visible through data completeness.
This output supports, but does not replace, video review, medical evaluation,
official statistics, or professional judgment.
"""
