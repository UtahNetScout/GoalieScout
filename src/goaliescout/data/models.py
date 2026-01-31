"""Data models for goalie scouting."""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class League(Enum):
    """Hockey league classifications."""
    NHL = "NHL"
    AHL = "AHL"
    NCAA = "NCAA"
    CHL = "CHL"
    OHL = "OHL"
    WHL = "WHL"
    QMJHL = "QMJHL"
    USHL = "USHL"
    KHL = "KHL"
    SHL = "SHL"
    LIIGA = "Liiga"
    HIGH_SCHOOL = "High School"
    SEMI_PRO = "Semi-Professional"
    OTHER = "Other"


class Position(Enum):
    """Player position."""
    GOALIE = "Goalie"


@dataclass
class Demographics:
    """Player demographic information."""
    name: str
    country: str
    date_of_birth: str
    height: Optional[str] = None
    weight: Optional[str] = None
    catches: Optional[str] = None  # L or R
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class PerformanceMetrics:
    """Goalie performance statistics."""
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    overtime_losses: int = 0
    save_percentage: float = 0.0
    goals_against_average: float = 0.0
    shutouts: int = 0
    goals_against: int = 0
    saves: int = 0
    shots_against: int = 0
    minutes_played: float = 0.0
    season: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class InjuryRecord:
    """Injury tracking information."""
    date: str
    injury_type: str
    severity: str  # Minor, Moderate, Severe
    recovery_time: Optional[int] = None  # Days
    status: str = "Active"  # Active, Recovered, Ongoing
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class NHLComparison:
    """Comparison to NHL goalies."""
    comparable_player: str
    similarity_score: float
    comparison_notes: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AIAnalysis:
    """AI-generated analysis and insights."""
    overall_rating: float  # 0-100
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    potential_rating: float = 0.0  # 0-100
    nhl_readiness: str = "Not Ready"  # Not Ready, Developing, Ready, NHL Caliber
    scouting_notes: str = ""
    analysis_date: str = field(default_factory=lambda: datetime.now().isoformat())
    model_used: str = "openai"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class GoalieProfile:
    """Complete goalie profile with all scouting data."""
    player_id: str
    demographics: Demographics
    league: str
    position: str = "Goalie"
    current_team: Optional[str] = None
    performance_metrics: List[PerformanceMetrics] = field(default_factory=list)
    injury_history: List[InjuryRecord] = field(default_factory=list)
    nhl_comparisons: List[NHLComparison] = field(default_factory=list)
    ai_analysis: Optional[AIAnalysis] = None
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    data_sources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            'player_id': self.player_id,
            'demographics': self.demographics.to_dict(),
            'league': self.league,
            'position': self.position,
            'current_team': self.current_team,
            'performance_metrics': [m.to_dict() for m in self.performance_metrics],
            'injury_history': [i.to_dict() for i in self.injury_history],
            'nhl_comparisons': [c.to_dict() for c in self.nhl_comparisons],
            'ai_analysis': self.ai_analysis.to_dict() if self.ai_analysis else None,
            'last_updated': self.last_updated,
            'data_sources': self.data_sources
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GoalieProfile':
        """Create GoalieProfile from dictionary."""
        demographics = Demographics(**data['demographics'])
        performance_metrics = [PerformanceMetrics(**m) for m in data.get('performance_metrics', [])]
        injury_history = [InjuryRecord(**i) for i in data.get('injury_history', [])]
        nhl_comparisons = [NHLComparison(**c) for c in data.get('nhl_comparisons', [])]
        ai_analysis = AIAnalysis(**data['ai_analysis']) if data.get('ai_analysis') else None
        
        return cls(
            player_id=data['player_id'],
            demographics=demographics,
            league=data['league'],
            position=data.get('position', 'Goalie'),
            current_team=data.get('current_team'),
            performance_metrics=performance_metrics,
            injury_history=injury_history,
            nhl_comparisons=nhl_comparisons,
            ai_analysis=ai_analysis,
            last_updated=data.get('last_updated', datetime.now().isoformat()),
            data_sources=data.get('data_sources', [])
        )
