"""SQLAlchemy ORM models for the GoalieScout database.

Designed for SQLite by default but compatible with any SQLAlchemy-
supported backend (e.g. PostgreSQL) by swapping the connection URL.
"""

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class Goalie(Base):
    """Goalie bio / demographic record."""

    __tablename__ = "goalies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    dob: Mapped[Optional[str]] = mapped_column(String(10))  # YYYY-MM-DD
    country: Mapped[Optional[str]] = mapped_column(String(60))
    height: Mapped[Optional[str]] = mapped_column(String(20))
    weight: Mapped[Optional[str]] = mapped_column(String(20))
    handedness: Mapped[Optional[str]] = mapped_column(String(10))  # L / R
    catches: Mapped[Optional[str]] = mapped_column(String(10))    # L / R
    # Original JSON player_id for backward compatibility
    legacy_player_id: Mapped[Optional[str]] = mapped_column(String(120), unique=True)

    # Relationships
    seasons: Mapped[List["Season"]] = relationship(
        "Season", back_populates="goalie", cascade="all, delete-orphan"
    )
    game_logs: Mapped[List["GameLog"]] = relationship(
        "GameLog", back_populates="goalie", cascade="all, delete-orphan"
    )
    injuries: Mapped[List["Injury"]] = relationship(
        "Injury", back_populates="goalie", cascade="all, delete-orphan"
    )
    scouting_reports: Mapped[List["ScoutingReport"]] = relationship(
        "ScoutingReport", back_populates="goalie", cascade="all, delete-orphan"
    )
    nhl_comparisons: Mapped[List["NHLComparison"]] = relationship(
        "NHLComparison", back_populates="goalie", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Goalie id={self.id} name={self.name!r}>"


class Season(Base):
    """Seasonal statistics for a goalie."""

    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    goalie_id: Mapped[int] = mapped_column(Integer, ForeignKey("goalies.id"), nullable=False)
    league: Mapped[Optional[str]] = mapped_column(String(60))
    team: Mapped[Optional[str]] = mapped_column(String(120))
    year: Mapped[Optional[str]] = mapped_column(String(10))  # e.g. "2023-24"
    games: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    otl: Mapped[int] = mapped_column(Integer, default=0)
    sv_pct: Mapped[Optional[float]] = mapped_column(Float)
    gaa: Mapped[Optional[float]] = mapped_column(Float)
    shutouts: Mapped[int] = mapped_column(Integer, default=0)
    shots_against: Mapped[int] = mapped_column(Integer, default=0)
    saves: Mapped[int] = mapped_column(Integer, default=0)
    goals_against: Mapped[int] = mapped_column(Integer, default=0)
    minutes_played: Mapped[Optional[float]] = mapped_column(Float)

    goalie: Mapped["Goalie"] = relationship("Goalie", back_populates="seasons")

    def __repr__(self) -> str:
        return f"<Season goalie_id={self.goalie_id} year={self.year}>"


class GameLog(Base):
    """Individual game log entry."""

    __tablename__ = "game_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    goalie_id: Mapped[int] = mapped_column(Integer, ForeignKey("goalies.id"), nullable=False)
    date: Mapped[Optional[str]] = mapped_column(String(10))  # YYYY-MM-DD
    opponent: Mapped[Optional[str]] = mapped_column(String(120))
    shots_against: Mapped[int] = mapped_column(Integer, default=0)
    saves: Mapped[int] = mapped_column(Integer, default=0)
    goals_against: Mapped[int] = mapped_column(Integer, default=0)
    result: Mapped[Optional[str]] = mapped_column(String(10))  # W / L / OTL
    toi: Mapped[Optional[float]] = mapped_column(Float)        # time on ice (minutes)

    goalie: Mapped["Goalie"] = relationship("Goalie", back_populates="game_logs")
    advanced_metrics: Mapped[Optional["AdvancedMetrics"]] = relationship(
        "AdvancedMetrics", back_populates="game_log", uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<GameLog goalie_id={self.goalie_id} date={self.date}>"


class AdvancedMetrics(Base):
    """Advanced analytics attached to a game log."""

    __tablename__ = "advanced_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_log_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("game_logs.id"), nullable=False, unique=True
    )
    gsax: Mapped[Optional[float]] = mapped_column(Float)
    xg_against: Mapped[Optional[float]] = mapped_column(Float)
    hd_sv_pct: Mapped[Optional[float]] = mapped_column(Float)
    md_sv_pct: Mapped[Optional[float]] = mapped_column(Float)
    ld_sv_pct: Mapped[Optional[float]] = mapped_column(Float)
    rebound_rate: Mapped[Optional[float]] = mapped_column(Float)
    controlled_rebound_rate: Mapped[Optional[float]] = mapped_column(Float)
    consistency_score: Mapped[Optional[float]] = mapped_column(Float)
    rush_sv_pct: Mapped[Optional[float]] = mapped_column(Float)
    movement_score: Mapped[Optional[float]] = mapped_column(Float)
    black_ops_score: Mapped[Optional[float]] = mapped_column(Float)

    game_log: Mapped["GameLog"] = relationship(
        "GameLog", back_populates="advanced_metrics"
    )

    def __repr__(self) -> str:
        return f"<AdvancedMetrics game_log_id={self.game_log_id} gsax={self.gsax}>"


class Injury(Base):
    """Injury record for a goalie."""

    __tablename__ = "injuries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    goalie_id: Mapped[int] = mapped_column(Integer, ForeignKey("goalies.id"), nullable=False)
    injury_type: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[Optional[str]] = mapped_column(String(30))  # Minor/Moderate/Severe
    start_date: Mapped[Optional[str]] = mapped_column(String(10))
    end_date: Mapped[Optional[str]] = mapped_column(String(10))
    games_missed: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="Active")
    notes: Mapped[Optional[str]] = mapped_column(Text)

    goalie: Mapped["Goalie"] = relationship("Goalie", back_populates="injuries")

    def __repr__(self) -> str:
        return f"<Injury goalie_id={self.goalie_id} type={self.injury_type!r}>"


class ScoutingReport(Base):
    """AI-generated or human scouting report."""

    __tablename__ = "scouting_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    goalie_id: Mapped[int] = mapped_column(Integer, ForeignKey("goalies.id"), nullable=False)
    date: Mapped[Optional[str]] = mapped_column(String(10))  # YYYY-MM-DD
    report_text: Mapped[Optional[str]] = mapped_column(Text)
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(60))
    black_ops_score: Mapped[Optional[float]] = mapped_column(Float)
    tier: Mapped[Optional[str]] = mapped_column(String(60))

    goalie: Mapped["Goalie"] = relationship("Goalie", back_populates="scouting_reports")

    def __repr__(self) -> str:
        return (
            f"<ScoutingReport goalie_id={self.goalie_id} "
            f"black_ops_score={self.black_ops_score}>"
        )


class NHLComparison(Base):
    """NHL player comparison for a goalie prospect."""

    __tablename__ = "nhl_comparisons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    goalie_id: Mapped[int] = mapped_column(Integer, ForeignKey("goalies.id"), nullable=False)
    nhl_comp_name: Mapped[str] = mapped_column(String(120), nullable=False)
    similarity_score: Mapped[Optional[float]] = mapped_column(Float)
    reasoning: Mapped[Optional[str]] = mapped_column(Text)

    goalie: Mapped["Goalie"] = relationship("Goalie", back_populates="nhl_comparisons")

    def __repr__(self) -> str:
        return (
            f"<NHLComparison goalie_id={self.goalie_id} "
            f"comp={self.nhl_comp_name!r} sim={self.similarity_score}>"
        )
