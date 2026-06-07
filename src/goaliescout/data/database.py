"""JSON-based database management for goalie scouting."""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from .models import Demographics, GoalieProfile, PerformanceMetrics

logger = logging.getLogger(__name__)


class GoalieDatabase:
    """JSON-based database for goalie profiles."""
    
    def __init__(self, database_path: str = "./data/goalie_database.json"):
        """Initialize the database.
        
        Args:
            database_path: Path to the JSON database file
        """
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database file if it doesn't exist."""
        if not self.database_path.exists():
            self._save_data({'goalies': [], 'metadata': {'version': '1.0'}})
            logger.info(f"Created new database at {self.database_path}")
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return {'goalies': [], 'metadata': {'version': '1.0'}}
    
    def _save_data(self, data: Dict[str, Any]):
        """Save data to JSON file."""
        try:
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Database saved to {self.database_path}")
        except Exception as e:
            logger.error(f"Error saving database: {e}")
            raise
    
    def add_goalie(self, profile: GoalieProfile) -> bool:
        """Add or update a goalie profile.
        
        Args:
            profile: GoalieProfile object
            
        Returns:
            True if successful
        """
        data = self._load_data()
        goalies = data.get('goalies', [])
        
        # Check if goalie already exists
        existing_index = None
        for i, goalie in enumerate(goalies):
            if goalie.get('player_id') == profile.player_id:
                existing_index = i
                break
        
        profile_dict = profile.to_dict()
        
        if existing_index is not None:
            goalies[existing_index] = profile_dict
            logger.info(f"Updated goalie profile: {profile.player_id}")
        else:
            goalies.append(profile_dict)
            logger.info(f"Added new goalie profile: {profile.player_id}")
        
        data['goalies'] = goalies
        self._save_data(data)
        return True

    def upsert_goalie_record(self, player_id: str, record: Dict[str, Any]) -> bool:
        """Create or update a profile from a normalized pipeline record."""
        existing = self.get_goalie(player_id)
        source = str(record.get("source", "")).strip()

        if existing is None:
            existing = GoalieProfile(
                player_id=player_id,
                demographics=Demographics(
                    name=str(record.get("name") or player_id.replace("_", " ").title()),
                    country=str(record.get("nationality") or record.get("country") or ""),
                    date_of_birth=str(record.get("dob") or record.get("date_of_birth") or ""),
                    height=_optional_string(record.get("height") or record.get("height_inches")),
                    weight=_optional_string(record.get("weight") or record.get("weight_lbs")),
                    catches=_optional_string(record.get("catches")),
                ),
                league=str(record.get("league") or "Unknown"),
                current_team=_optional_string(record.get("team") or record.get("current_team")),
            )
        else:
            existing.demographics.name = str(record.get("name") or existing.demographics.name)
            existing.league = str(record.get("league") or existing.league)
            existing.current_team = _optional_string(
                record.get("team") or record.get("current_team") or existing.current_team
            )

        season = _optional_string(record.get("season"))
        metrics = PerformanceMetrics(
            games_played=_as_int(record.get("games_played")),
            wins=_as_int(record.get("wins")),
            losses=_as_int(record.get("losses")),
            overtime_losses=_as_int(record.get("overtime_losses")),
            save_percentage=_as_float(record.get("save_percentage")),
            goals_against_average=_as_float(record.get("goals_against_average")),
            shutouts=_as_int(record.get("shutouts")),
            goals_against=_as_int(record.get("goals_against")),
            saves=_as_int(record.get("saves")),
            shots_against=_as_int(record.get("shots_against")),
            minutes_played=_as_float(record.get("minutes_played")),
            season=season,
        )

        if any(
            (
                metrics.games_played,
                metrics.wins,
                metrics.losses,
                metrics.save_percentage,
                metrics.goals_against_average,
                metrics.shots_against,
            )
        ):
            existing.performance_metrics = [
                item for item in existing.performance_metrics if item.season != season
            ]
            existing.performance_metrics.append(metrics)

        if source and source not in existing.data_sources:
            existing.data_sources.append(source)

        existing.last_updated = datetime.now().isoformat()
        return self.add_goalie(existing)
    
    def get_goalie(self, player_id: str) -> Optional[GoalieProfile]:
        """Get a goalie profile by player ID.
        
        Args:
            player_id: Player's unique identifier
            
        Returns:
            GoalieProfile object or None
        """
        data = self._load_data()
        goalies = data.get('goalies', [])
        
        for goalie_data in goalies:
            if goalie_data.get('player_id') == player_id:
                return GoalieProfile.from_dict(goalie_data)
        
        return None
    
    def get_all_goalies(self) -> List[GoalieProfile]:
        """Get all goalie profiles.
        
        Returns:
            List of GoalieProfile objects
        """
        data = self._load_data()
        goalies = data.get('goalies', [])
        return [GoalieProfile.from_dict(g) for g in goalies]
    
    def search_goalies(self, **filters) -> List[GoalieProfile]:
        """Search for goalies matching criteria.
        
        Args:
            **filters: Search criteria (e.g., league='NHL', country='Canada')
            
        Returns:
            List of matching GoalieProfile objects
        """
        all_goalies = self.get_all_goalies()
        results = []
        
        for goalie in all_goalies:
            match = True
            for key, value in filters.items():
                if key == 'league' and goalie.league != value:
                    match = False
                    break
                elif key == 'country' and goalie.demographics.country != value:
                    match = False
                    break
                elif key == 'name' and value.lower() not in goalie.demographics.name.lower():
                    match = False
                    break
            
            if match:
                results.append(goalie)
        
        return results
    
    def delete_goalie(self, player_id: str) -> bool:
        """Delete a goalie profile.
        
        Args:
            player_id: Player's unique identifier
            
        Returns:
            True if deleted, False if not found
        """
        data = self._load_data()
        goalies = data.get('goalies', [])
        
        initial_count = len(goalies)
        goalies = [g for g in goalies if g.get('player_id') != player_id]
        
        if len(goalies) < initial_count:
            data['goalies'] = goalies
            self._save_data(data)
            logger.info(f"Deleted goalie profile: {player_id}")
            return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        goalies = self.get_all_goalies()
        leagues = {}
        countries = {}
        
        for goalie in goalies:
            # Count by league
            league = goalie.league
            leagues[league] = leagues.get(league, 0) + 1
            
            # Count by country
            country = goalie.demographics.country
            countries[country] = countries.get(country, 0) + 1
        
        return {
            'total_goalies': len(goalies),
            'leagues': leagues,
            'countries': countries
        }


def _as_int(value: Any) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def _as_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _optional_string(value: Any) -> Optional[str]:
    if value is None or value == "":
        return None
    return str(value)
