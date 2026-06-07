"""Migration script to import existing JSON data into the SQLite database.

Usage::

    python -m goaliescout.database.import_json --json-path ./data/goalie_database.json
    # or call import_json_database() programmatically
"""

import json
import logging
from pathlib import Path
from typing import Optional

from .connection import get_engine, get_session
from .migrations import create_schema
from .repository import (
    add_nhl_comparison,
    add_scouting_report,
    add_season,
    create_goalie,
    get_goalie_by_legacy_id,
)

logger = logging.getLogger(__name__)


def import_json_database(
    json_path: str = "./data/goalie_database.json",
    db_url: Optional[str] = None,
    skip_existing: bool = True,
) -> dict:
    """Import goalie data from the legacy JSON database into SQLite.

    Args:
        json_path: Path to the JSON database file.
        db_url: Optional SQLAlchemy URL override.
        skip_existing: If ``True``, skip goalies already present in
            the database (matched by ``legacy_player_id``).

    Returns:
        Summary dict with ``imported``, ``skipped``, and ``errors`` counts.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
    """
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON database not found: {path}")

    engine = get_engine(db_url) if db_url else get_engine()
    create_schema(engine)

    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    goalies_data = data.get("goalies", [])
    logger.info(f"Found {len(goalies_data)} goalie(s) in JSON file.")

    imported = 0
    skipped = 0
    errors = 0

    for goalie_dict in goalies_data:
        legacy_id = goalie_dict.get("player_id")
        try:
            with get_session(engine) as session:
                if skip_existing and legacy_id:
                    existing = get_goalie_by_legacy_id(legacy_id, session)
                    if existing:
                        skipped += 1
                        continue

                demographics = goalie_dict.get("demographics", {})
                goalie = create_goalie(
                    {
                        "name": demographics.get("name", "Unknown"),
                        "dob": demographics.get("date_of_birth"),
                        "country": demographics.get("country"),
                        "height": demographics.get("height"),
                        "weight": demographics.get("weight"),
                        "catches": demographics.get("catches"),
                        "legacy_player_id": legacy_id,
                    },
                    session=session,
                )

                # Import performance metrics as seasons
                for metric in goalie_dict.get("performance_metrics", []):
                    add_season(
                        goalie.id,
                        {
                            "league": goalie_dict.get("league"),
                            "team": goalie_dict.get("current_team"),
                            "year": metric.get("season"),
                            "games": metric.get("games_played", 0),
                            "wins": metric.get("wins", 0),
                            "losses": metric.get("losses", 0),
                            "otl": metric.get("overtime_losses", 0),
                            "sv_pct": metric.get("save_percentage"),
                            "gaa": metric.get("goals_against_average"),
                            "shutouts": metric.get("shutouts", 0),
                            "shots_against": metric.get("shots_against", 0),
                            "saves": metric.get("saves", 0),
                            "goals_against": metric.get("goals_against", 0),
                            "minutes_played": metric.get("minutes_played"),
                        },
                        session=session,
                    )

                # Import AI analysis as a scouting report
                ai_analysis = goalie_dict.get("ai_analysis")
                if ai_analysis:
                    add_scouting_report(
                        goalie.id,
                        {
                            "date": ai_analysis.get("analysis_date", "")[:10],
                            "report_text": ai_analysis.get("scouting_notes"),
                            "ai_model_used": ai_analysis.get("model_used"),
                        },
                        session=session,
                    )

                # Import NHL comparisons
                for comp in goalie_dict.get("nhl_comparisons", []):
                    add_nhl_comparison(
                        goalie.id,
                        {
                            "nhl_comp_name": comp.get("comparable_player", ""),
                            "similarity_score": comp.get("similarity_score"),
                            "reasoning": comp.get("comparison_notes"),
                        },
                        session=session,
                    )

            imported += 1
            logger.info(f"Imported goalie: {demographics.get('name')} ({legacy_id})")

        except Exception as exc:
            errors += 1
            logger.error(f"Error importing goalie {legacy_id}: {exc}", exc_info=True)

    summary = {"imported": imported, "skipped": skipped, "errors": errors}
    logger.info(f"Import complete: {summary}")
    return summary


def main() -> None:
    """Entry-point for CLI invocation."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Import GoalieScout JSON data into SQLite database"
    )
    parser.add_argument(
        "--json-path",
        default="./data/goalie_database.json",
        help="Path to JSON database file",
    )
    parser.add_argument(
        "--db-url",
        default=None,
        help="SQLAlchemy database URL (defaults to sqlite:///./data/goaliescout.db)",
    )
    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Re-import goalies that already exist in the database",
    )
    args = parser.parse_args()

    summary = import_json_database(
        json_path=args.json_path,
        db_url=args.db_url,
        skip_existing=not args.no_skip_existing,
    )
    print(f"Import summary: {summary}")


if __name__ == "__main__":
    main()
