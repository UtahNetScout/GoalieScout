"""Tests for the SQLite database layer (CRUD and JSON migration)."""

import json
import os
import tempfile

import pytest
from sqlalchemy import create_engine

from goaliescout.database.connection import get_session, reset_engine
from goaliescout.database.migrations import create_schema, get_schema_version
from goaliescout.database.models import Goalie, Season
from goaliescout.database.repository import (
    add_season,
    add_scouting_report,
    create_goalie,
    delete_goalie,
    get_goalie,
    get_goalie_by_legacy_id,
    get_scouting_reports,
    get_seasons,
    list_goalies,
    update_goalie,
)
from goaliescout.database.import_json import import_json_database


@pytest.fixture()
def engine():
    """In-memory SQLite engine for isolated tests."""
    eng = create_engine("sqlite:///:memory:")
    create_schema(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session(engine):
    """Provide a session bound to the in-memory engine."""
    with get_session(engine) as s:
        yield s


class TestSchemaCreation:
    def test_schema_version_after_create(self, engine):
        assert get_schema_version(engine) == 1

    def test_tables_exist(self, engine):
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        for expected in ("goalies", "seasons", "game_logs", "advanced_metrics",
                         "injuries", "scouting_reports", "nhl_comparisons"):
            assert expected in tables


class TestGoalieCRUD:
    def test_create_and_get(self, engine):
        with get_session(engine) as s:
            goalie = create_goalie(
                {"name": "Test Goalie", "country": "Canada", "legacy_player_id": "test_goalie"},
                session=s,
            )
            gid = goalie.id
        with get_session(engine) as s:
            fetched = get_goalie(gid, session=s)
            assert fetched is not None
            assert fetched.name == "Test Goalie"

    def test_get_by_legacy_id(self, engine):
        with get_session(engine) as s:
            create_goalie({"name": "Legacy", "legacy_player_id": "legacy_001"}, session=s)
        with get_session(engine) as s:
            goalie = get_goalie_by_legacy_id("legacy_001", session=s)
            assert goalie is not None
            assert goalie.name == "Legacy"

    def test_update_goalie(self, engine):
        with get_session(engine) as s:
            goalie = create_goalie({"name": "Old Name"}, session=s)
            gid = goalie.id
        with get_session(engine) as s:
            updated = update_goalie(gid, {"name": "New Name"}, session=s)
            assert updated.name == "New Name"

    def test_delete_goalie(self, engine):
        with get_session(engine) as s:
            goalie = create_goalie({"name": "To Delete"}, session=s)
            gid = goalie.id
        with get_session(engine) as s:
            result = delete_goalie(gid, session=s)
            assert result is True
        with get_session(engine) as s:
            assert get_goalie(gid, session=s) is None

    def test_delete_nonexistent(self, engine):
        with get_session(engine) as s:
            result = delete_goalie(99999, session=s)
            assert result is False

    def test_list_goalies(self, engine):
        with get_session(engine) as s:
            create_goalie({"name": "G1", "country": "Canada"}, session=s)
            create_goalie({"name": "G2", "country": "Finland"}, session=s)
        with get_session(engine) as s:
            goalies = list_goalies(session=s)
            assert len(goalies) == 2


class TestSeasonCRUD:
    def test_add_and_get_season(self, engine):
        with get_session(engine) as s:
            goalie = create_goalie({"name": "Season Test"}, session=s)
            gid = goalie.id
            add_season(gid, {"year": "2023-24", "games": 40, "sv_pct": 0.915}, session=s)
        with get_session(engine) as s:
            seasons = get_seasons(gid, session=s)
            assert len(seasons) == 1
            assert seasons[0].year == "2023-24"


class TestScoutingReportCRUD:
    def test_add_and_get_report(self, engine):
        with get_session(engine) as s:
            goalie = create_goalie({"name": "Report Test"}, session=s)
            gid = goalie.id
            add_scouting_report(
                gid,
                {"report_text": "Excellent goalie", "black_ops_score": 87.5},
                session=s,
            )
        with get_session(engine) as s:
            reports = get_scouting_reports(gid, session=s)
            assert len(reports) == 1
            assert reports[0].black_ops_score == pytest.approx(87.5)


class TestJsonImport:
    def test_import_from_json(self, tmp_path, engine):
        json_data = {
            "goalies": [
                {
                    "player_id": "test_import_001",
                    "demographics": {
                        "name": "Import Test",
                        "country": "USA",
                        "date_of_birth": "2000-01-01",
                    },
                    "league": "AHL",
                    "current_team": "Test Team",
                    "performance_metrics": [
                        {
                            "season": "2023-24",
                            "games_played": 30,
                            "wins": 18,
                            "losses": 10,
                            "overtime_losses": 2,
                            "save_percentage": 0.912,
                            "goals_against_average": 2.45,
                        }
                    ],
                    "nhl_comparisons": [],
                    "injury_history": [],
                }
            ]
        }
        json_file = tmp_path / "test_db.json"
        json_file.write_text(json.dumps(json_data))

        summary = import_json_database(
            json_path=str(json_file),
            db_url="sqlite:///:memory:",
        )
        assert summary["imported"] == 1
        assert summary["errors"] == 0

    def test_skip_existing(self, tmp_path):
        json_data = {
            "goalies": [
                {
                    "player_id": "skip_test_001",
                    "demographics": {"name": "Skip Test", "country": "Canada"},
                    "league": "NHL",
                    "performance_metrics": [],
                    "nhl_comparisons": [],
                    "injury_history": [],
                }
            ]
        }
        json_file = tmp_path / "skip_db.json"
        json_file.write_text(json.dumps(json_data))
        db_url = f"sqlite:///{tmp_path / 'skip.db'}"

        summary1 = import_json_database(str(json_file), db_url=db_url)
        summary2 = import_json_database(str(json_file), db_url=db_url, skip_existing=True)

        assert summary1["imported"] == 1
        assert summary2["skipped"] == 1
        assert summary2["imported"] == 0

    def test_missing_json_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            import_json_database(
                str(tmp_path / "nonexistent.json"),
                db_url="sqlite:///:memory:",
            )
