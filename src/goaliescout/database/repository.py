"""Data access layer (repository pattern) for GoalieScout.

Provides CRUD operations for all ORM models.  All methods accept an
optional ``session`` parameter; if omitted they open a short-lived
session via :func:`~goaliescout.database.connection.get_session`.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from .connection import get_session
from .models import (
    AdvancedMetrics,
    GameLog,
    Goalie,
    Injury,
    NHLComparison,
    ScoutingReport,
    Season,
)


# ---------------------------------------------------------------------------
# Goalie CRUD
# ---------------------------------------------------------------------------


def create_goalie(data: Dict[str, Any], session: Optional[Session] = None) -> Goalie:
    """Insert a new goalie record.

    Args:
        data: Dictionary of :class:`~goaliescout.database.models.Goalie`
              field values.
        session: Optional open session.  A new session is used if omitted.

    Returns:
        The persisted :class:`Goalie` instance with ``id`` populated.
    """
    def _create(s: Session) -> Goalie:
        goalie = Goalie(**{k: v for k, v in data.items() if hasattr(Goalie, k)})
        s.add(goalie)
        s.flush()
        return goalie

    if session is not None:
        return _create(session)
    with get_session() as s:
        goalie = _create(s)
        s.expunge(goalie)
        return goalie


def get_goalie(goalie_id: int, session: Optional[Session] = None) -> Optional[Goalie]:
    """Fetch a goalie by primary key.

    Args:
        goalie_id: Primary key.
        session: Optional open session.

    Returns:
        :class:`Goalie` or ``None`` if not found.
    """
    if session is not None:
        return session.get(Goalie, goalie_id)
    with get_session() as s:
        goalie = s.get(Goalie, goalie_id)
        if goalie:
            s.expunge(goalie)
        return goalie


def get_goalie_by_legacy_id(
    legacy_id: str, session: Optional[Session] = None
) -> Optional[Goalie]:
    """Fetch a goalie by the JSON legacy player_id.

    Args:
        legacy_id: The ``player_id`` string from the JSON database.
        session: Optional open session.

    Returns:
        :class:`Goalie` or ``None``.
    """
    if session is not None:
        return (
            session.query(Goalie)
            .filter(Goalie.legacy_player_id == legacy_id)
            .first()
        )
    with get_session() as s:
        goalie = (
            s.query(Goalie).filter(Goalie.legacy_player_id == legacy_id).first()
        )
        if goalie:
            s.expunge(goalie)
        return goalie


def list_goalies(
    league: Optional[str] = None,
    country: Optional[str] = None,
    session: Optional[Session] = None,
) -> List[Goalie]:
    """List goalies, optionally filtered by league/country.

    Args:
        league: Filter by season league (requires a Season join).
        country: Filter by country.
        session: Optional open session.

    Returns:
        List of :class:`Goalie` instances.
    """
    def _query(s: Session) -> List[Goalie]:
        q = s.query(Goalie)
        if country:
            q = q.filter(Goalie.country == country)
        return q.all()

    if session is not None:
        return _query(session)
    with get_session() as s:
        goalies = _query(s)
        for g in goalies:
            s.expunge(g)
        return goalies


def update_goalie(
    goalie_id: int, data: Dict[str, Any], session: Optional[Session] = None
) -> Optional[Goalie]:
    """Update goalie fields.

    Args:
        goalie_id: Primary key.
        data: Dictionary of fields to update.
        session: Optional open session.

    Returns:
        Updated :class:`Goalie` or ``None`` if not found.
    """
    def _update(s: Session) -> Optional[Goalie]:
        goalie = s.get(Goalie, goalie_id)
        if not goalie:
            return None
        for key, value in data.items():
            if hasattr(goalie, key):
                setattr(goalie, key, value)
        s.flush()
        return goalie

    if session is not None:
        return _update(session)
    with get_session() as s:
        goalie = _update(s)
        if goalie:
            s.expunge(goalie)
        return goalie


def delete_goalie(goalie_id: int, session: Optional[Session] = None) -> bool:
    """Delete a goalie and all related records (cascade).

    Args:
        goalie_id: Primary key.
        session: Optional open session.

    Returns:
        ``True`` if deleted, ``False`` if not found.
    """
    def _delete(s: Session) -> bool:
        goalie = s.get(Goalie, goalie_id)
        if not goalie:
            return False
        s.delete(goalie)
        return True

    if session is not None:
        return _delete(session)
    with get_session() as s:
        return _delete(s)


# ---------------------------------------------------------------------------
# Season CRUD
# ---------------------------------------------------------------------------


def add_season(
    goalie_id: int, data: Dict[str, Any], session: Optional[Session] = None
) -> Season:
    """Add a season record for a goalie.

    Args:
        goalie_id: Goalie primary key.
        data: Season field values.
        session: Optional open session.

    Returns:
        Persisted :class:`Season`.
    """
    def _add(s: Session) -> Season:
        season = Season(
            goalie_id=goalie_id,
            **{k: v for k, v in data.items() if hasattr(Season, k) and k != "goalie_id"},
        )
        s.add(season)
        s.flush()
        return season

    if session is not None:
        return _add(session)
    with get_session() as s:
        season = _add(s)
        s.expunge(season)
        return season


def get_seasons(goalie_id: int, session: Optional[Session] = None) -> List[Season]:
    """Get all seasons for a goalie.

    Args:
        goalie_id: Goalie primary key.
        session: Optional open session.

    Returns:
        List of :class:`Season` objects.
    """
    def _get(s: Session) -> List[Season]:
        return s.query(Season).filter(Season.goalie_id == goalie_id).all()

    if session is not None:
        return _get(session)
    with get_session() as s:
        seasons = _get(s)
        for season in seasons:
            s.expunge(season)
        return seasons


# ---------------------------------------------------------------------------
# GameLog CRUD
# ---------------------------------------------------------------------------


def add_game_log(
    goalie_id: int, data: Dict[str, Any], session: Optional[Session] = None
) -> GameLog:
    """Add a game log entry for a goalie.

    Args:
        goalie_id: Goalie primary key.
        data: GameLog field values.
        session: Optional open session.

    Returns:
        Persisted :class:`GameLog`.
    """
    def _add(s: Session) -> GameLog:
        log = GameLog(
            goalie_id=goalie_id,
            **{k: v for k, v in data.items() if hasattr(GameLog, k) and k != "goalie_id"},
        )
        s.add(log)
        s.flush()
        return log

    if session is not None:
        return _add(session)
    with get_session() as s:
        log = _add(s)
        s.expunge(log)
        return log


def get_game_logs(goalie_id: int, session: Optional[Session] = None) -> List[GameLog]:
    """Get all game logs for a goalie.

    Args:
        goalie_id: Goalie primary key.
        session: Optional open session.

    Returns:
        List of :class:`GameLog` objects ordered by date.
    """
    def _get(s: Session) -> List[GameLog]:
        return (
            s.query(GameLog)
            .filter(GameLog.goalie_id == goalie_id)
            .order_by(GameLog.date)
            .all()
        )

    if session is not None:
        return _get(session)
    with get_session() as s:
        logs = _get(s)
        for log in logs:
            s.expunge(log)
        return logs


# ---------------------------------------------------------------------------
# AdvancedMetrics CRUD
# ---------------------------------------------------------------------------


def upsert_advanced_metrics(
    game_log_id: int,
    data: Dict[str, Any],
    session: Optional[Session] = None,
) -> AdvancedMetrics:
    """Insert or update advanced metrics for a game log.

    Args:
        game_log_id: GameLog primary key.
        data: AdvancedMetrics field values.
        session: Optional open session.

    Returns:
        Persisted :class:`AdvancedMetrics`.
    """
    def _upsert(s: Session) -> AdvancedMetrics:
        metrics = (
            s.query(AdvancedMetrics)
            .filter(AdvancedMetrics.game_log_id == game_log_id)
            .first()
        )
        if metrics is None:
            metrics = AdvancedMetrics(
                game_log_id=game_log_id,
                **{
                    k: v
                    for k, v in data.items()
                    if hasattr(AdvancedMetrics, k) and k not in ("id", "game_log_id")
                },
            )
            s.add(metrics)
        else:
            for key, value in data.items():
                if hasattr(metrics, key) and key not in ("id", "game_log_id"):
                    setattr(metrics, key, value)
        s.flush()
        return metrics

    if session is not None:
        return _upsert(session)
    with get_session() as s:
        metrics = _upsert(s)
        s.expunge(metrics)
        return metrics


# ---------------------------------------------------------------------------
# ScoutingReport CRUD
# ---------------------------------------------------------------------------


def add_scouting_report(
    goalie_id: int, data: Dict[str, Any], session: Optional[Session] = None
) -> ScoutingReport:
    """Add a scouting report for a goalie.

    Args:
        goalie_id: Goalie primary key.
        data: ScoutingReport field values.
        session: Optional open session.

    Returns:
        Persisted :class:`ScoutingReport`.
    """
    def _add(s: Session) -> ScoutingReport:
        report = ScoutingReport(
            goalie_id=goalie_id,
            **{
                k: v
                for k, v in data.items()
                if hasattr(ScoutingReport, k) and k != "goalie_id"
            },
        )
        s.add(report)
        s.flush()
        return report

    if session is not None:
        return _add(session)
    with get_session() as s:
        report = _add(s)
        s.expunge(report)
        return report


def get_scouting_reports(
    goalie_id: int, session: Optional[Session] = None
) -> List[ScoutingReport]:
    """Get all scouting reports for a goalie.

    Args:
        goalie_id: Goalie primary key.
        session: Optional open session.

    Returns:
        List of :class:`ScoutingReport` objects.
    """
    def _get(s: Session) -> List[ScoutingReport]:
        return (
            s.query(ScoutingReport)
            .filter(ScoutingReport.goalie_id == goalie_id)
            .all()
        )

    if session is not None:
        return _get(session)
    with get_session() as s:
        reports = _get(s)
        for r in reports:
            s.expunge(r)
        return reports


# ---------------------------------------------------------------------------
# NHLComparison CRUD
# ---------------------------------------------------------------------------


def add_nhl_comparison(
    goalie_id: int, data: Dict[str, Any], session: Optional[Session] = None
) -> NHLComparison:
    """Add an NHL comparison entry for a goalie.

    Args:
        goalie_id: Goalie primary key.
        data: NHLComparison field values.
        session: Optional open session.

    Returns:
        Persisted :class:`NHLComparison`.
    """
    def _add(s: Session) -> NHLComparison:
        comp = NHLComparison(
            goalie_id=goalie_id,
            **{
                k: v
                for k, v in data.items()
                if hasattr(NHLComparison, k) and k != "goalie_id"
            },
        )
        s.add(comp)
        s.flush()
        return comp

    if session is not None:
        return _add(session)
    with get_session() as s:
        comp = _add(s)
        s.expunge(comp)
        return comp
