"""Tests for grounded AI scouting prompts."""

from goaliescout.ai.services import OpenAIService


def _profile():
    return {
        "demographics": {
            "name": "Test Goalie",
            "country": "USA",
            "date_of_birth": "1993-05-19",
            "height": "6'4\"",
            "weight": "207 lbs",
            "catches": "L",
        },
        "current_team": "Test Team",
        "league": "NHL",
        "last_updated": "2026-06-10T08:00:00",
        "performance_metrics": [{
            "season": "2024-25",
            "games_played": 63,
            "wins": 47,
            "losses": 12,
            "overtime_losses": 3,
            "save_percentage": 0.925,
            "goals_against_average": 2.00,
        }],
        "notable_achievements": ["2024-25 Hart Memorial Trophy"],
        "data_sources": ["NHL.com player statistics"],
        "ai_analysis": {
            "overall_rating": 97,
            "nhl_readiness": "Elite NHL Starter",
            "strengths": ["Curated positioning assessment"],
            "weaknesses": ["Playoff translation requires review"],
            "scouting_notes": "Curated notes.",
        },
        "nhl_comparisons": [],
    }


def test_report_prompt_includes_evidence_and_freshness():
    service = OpenAIService(api_key=None)

    prompt = service._create_report_prompt(_profile())

    assert "2024-25" in prompt
    assert "SV%=0.925" in prompt
    assert "2024-25 Hart Memorial Trophy" in prompt
    assert "Dataset last updated: 2026-06-10T08:00:00" in prompt
    assert "NHL.com player statistics" in prompt


def test_report_prompt_requires_grounding_and_human_review():
    service = OpenAIService(api_key=None)

    prompt = service._create_report_prompt(_profile())

    assert "Do not invent statistics" in prompt
    assert "not established by the available data" in prompt
    assert "Human Review Checklist" in prompt
    assert "Do not describe an established NHL player as a prospect" in prompt


def test_profile_round_trip_preserves_achievements():
    from goaliescout.data.models import GoalieProfile

    profile = GoalieProfile.from_dict({
        "player_id": "test_1",
        "demographics": {
            "name": "Test Goalie",
            "country": "USA",
            "date_of_birth": "2000-01-01",
        },
        "league": "NHL",
        "notable_achievements": ["Award"],
    })

    assert profile.to_dict()["notable_achievements"] == ["Award"]


def test_fallback_report_remains_evidence_first():
    service = OpenAIService(api_key=None)

    report = service._fallback_report(_profile())

    assert "## Evidence Snapshot" in report
    assert "2024-25 Hart Memorial Trophy" in report
    assert "Dataset updated" in report
    assert "No new scouting claims were generated" in report
