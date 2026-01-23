"""
Player Movement Metrics Calculator
Calculates various movement-based metrics for player analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from scipy.spatial import distance


class MovementMetrics:
    """Calculate player movement metrics from tracking data."""
    
    def __init__(self):
        """Initialize the metrics calculator."""
        pass
    
    @staticmethod
    def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """
        Calculate Euclidean distance between two points.
        
        Args:
            x1, y1: First point coordinates
            x2, y2: Second point coordinates
            
        Returns:
            Distance in the same units as input
        """
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    @staticmethod
    def calculate_speed(distance: float, time_delta: float) -> float:
        """
        Calculate speed from distance and time.
        
        Args:
            distance: Distance traveled
            time_delta: Time elapsed (in seconds)
            
        Returns:
            Speed (distance per second)
        """
        if time_delta > 0:
            return distance / time_delta
        return 0.0
    
    def calculate_total_distance(self, tracking_df: pd.DataFrame) -> float:
        """
        Calculate total distance traveled by a player.
        
        Args:
            tracking_df: DataFrame with x, y coordinates and timestamps
            
        Returns:
            Total distance traveled
        """
        if len(tracking_df) < 2:
            return 0.0
        
        # Find coordinate columns
        x_col = self._find_column(tracking_df, ['x', 'x_coord', 'x_position'])
        y_col = self._find_column(tracking_df, ['y', 'y_coord', 'y_position'])
        
        if not x_col or not y_col:
            return 0.0
        
        # Sort by time if available
        time_col = self._find_column(tracking_df, ['time', 'timestamp', 'frame', 'game_time'])
        if time_col:
            tracking_df = tracking_df.sort_values(time_col)
        
        # Calculate distances between consecutive positions
        x_coords = tracking_df[x_col].values
        y_coords = tracking_df[y_col].values
        
        distances = []
        for i in range(1, len(x_coords)):
            dist = self.calculate_distance(
                x_coords[i-1], y_coords[i-1],
                x_coords[i], y_coords[i]
            )
            distances.append(dist)
        
        return sum(distances)
    
    def calculate_average_speed(self, tracking_df: pd.DataFrame) -> float:
        """
        Calculate average speed of a player.
        
        Args:
            tracking_df: DataFrame with x, y coordinates and timestamps
            
        Returns:
            Average speed
        """
        if len(tracking_df) < 2:
            return 0.0
        
        total_distance = self.calculate_total_distance(tracking_df)
        
        # Find time column
        time_col = self._find_column(tracking_df, ['time', 'timestamp', 'frame', 'game_time'])
        if time_col:
            tracking_df_sorted = tracking_df.sort_values(time_col)
            time_values = tracking_df_sorted[time_col].values
            total_time = time_values[-1] - time_values[0]
            
            if total_time > 0:
                return total_distance / total_time
        
        return 0.0
    
    def calculate_max_speed(self, tracking_df: pd.DataFrame) -> float:
        """
        Calculate maximum speed achieved by a player.
        
        Args:
            tracking_df: DataFrame with x, y coordinates and timestamps
            
        Returns:
            Maximum speed
        """
        if len(tracking_df) < 2:
            return 0.0
        
        x_col = self._find_column(tracking_df, ['x', 'x_coord', 'x_position'])
        y_col = self._find_column(tracking_df, ['y', 'y_coord', 'y_position'])
        time_col = self._find_column(tracking_df, ['time', 'timestamp', 'frame', 'game_time'])
        
        if not x_col or not y_col or not time_col:
            return 0.0
        
        tracking_df = tracking_df.sort_values(time_col)
        x_coords = tracking_df[x_col].values
        y_coords = tracking_df[y_col].values
        time_values = tracking_df[time_col].values
        
        speeds = []
        for i in range(1, len(x_coords)):
            dist = self.calculate_distance(
                x_coords[i-1], y_coords[i-1],
                x_coords[i], y_coords[i]
            )
            time_delta = time_values[i] - time_values[i-1]
            if time_delta > 0:
                speeds.append(dist / time_delta)
        
        return max(speeds) if speeds else 0.0
    
    def calculate_direction_changes(self, tracking_df: pd.DataFrame, threshold: float = 45.0) -> int:
        """
        Calculate number of significant direction changes.
        
        Args:
            tracking_df: DataFrame with x, y coordinates
            threshold: Minimum angle change (degrees) to count as direction change
            
        Returns:
            Number of direction changes
        """
        if len(tracking_df) < 3:
            return 0
        
        x_col = self._find_column(tracking_df, ['x', 'x_coord', 'x_position'])
        y_col = self._find_column(tracking_df, ['y', 'y_coord', 'y_position'])
        
        if not x_col or not y_col:
            return 0
        
        time_col = self._find_column(tracking_df, ['time', 'timestamp', 'frame', 'game_time'])
        if time_col:
            tracking_df = tracking_df.sort_values(time_col)
        
        x_coords = tracking_df[x_col].values
        y_coords = tracking_df[y_col].values
        
        direction_changes = 0
        for i in range(2, len(x_coords)):
            # Calculate vectors
            v1 = np.array([x_coords[i-1] - x_coords[i-2], y_coords[i-1] - y_coords[i-2]])
            v2 = np.array([x_coords[i] - x_coords[i-1], y_coords[i] - y_coords[i-1]])
            
            # Calculate angle between vectors
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_angle = np.clip(cos_angle, -1.0, 1.0)
                angle = np.degrees(np.arccos(cos_angle))
                
                if angle >= threshold:
                    direction_changes += 1
        
        return direction_changes
    
    def calculate_on_puck_distance(self, tracking_df: pd.DataFrame, event_df: pd.DataFrame) -> float:
        """
        Calculate distance traveled while controlling the puck.
        
        Args:
            tracking_df: Player tracking data
            event_df: Event data for the player
            
        Returns:
            Distance traveled with puck control
        """
        # This is a simplified version - actual implementation would need to
        # identify puck possession periods and calculate distance during those periods
        
        # Look for puck possession events
        puck_events = ['carry', 'possession', 'puck_carry', 'controlled']
        
        if len(event_df) == 0:
            return 0.0
        
        event_type_col = self._find_column(event_df, ['event', 'event_type', 'type'])
        if not event_type_col:
            return 0.0
        
        # Filter for puck control events
        puck_df = event_df[event_df[event_type_col].str.lower().str.contains('|'.join(puck_events), na=False)]
        
        # This is simplified - would need to correlate with tracking data
        return len(puck_df) * 10.0  # Placeholder
    
    def calculate_space_creation(self, tracking_df: pd.DataFrame, all_tracking: pd.DataFrame) -> float:
        """
        Calculate average space created (distance to nearest opponent).
        
        Args:
            tracking_df: Player tracking data
            all_tracking: Tracking data for all players
            
        Returns:
            Average distance to nearest opponent
        """
        # This is a simplified placeholder
        # Full implementation would calculate Voronoi regions or nearest opponent distances
        return 15.0  # Placeholder value
    
    @staticmethod
    def _find_column(df: pd.DataFrame, possible_names: List[str]) -> str:
        """
        Find which column name exists in the DataFrame.
        
        Args:
            df: DataFrame to search
            possible_names: List of possible column names
            
        Returns:
            Column name if found, empty string otherwise
        """
        for name in possible_names:
            if name in df.columns:
                return name
        return ""
    
    def calculate_all_metrics(self, tracking_df: pd.DataFrame, event_df: pd.DataFrame, 
                            position: str) -> Dict[str, Any]:
        """
        Calculate all relevant metrics for a player.
        
        Args:
            tracking_df: Player tracking data
            event_df: Player event data
            position: Player position (G, D, F)
            
        Returns:
            Dictionary of calculated metrics
        """
        metrics = {
            'total_distance': self.calculate_total_distance(tracking_df),
            'average_speed': self.calculate_average_speed(tracking_df),
            'max_speed': self.calculate_max_speed(tracking_df),
            'direction_changes': self.calculate_direction_changes(tracking_df),
            'on_puck_distance': self.calculate_on_puck_distance(tracking_df, event_df),
            'space_creation': self.calculate_space_creation(tracking_df, pd.DataFrame()),
            'events_count': len(event_df)
        }
        
        # Position-specific metrics
        if position.upper() in ['G', 'GOALIE', 'GOALKEEPER']:
            metrics['crease_movement'] = self._calculate_goalie_crease_movement(tracking_df)
            metrics['lateral_movement'] = self._calculate_lateral_movement(tracking_df)
        elif position.upper() in ['D', 'DEFENSE', 'DEFENSEMAN']:
            metrics['gap_control'] = self._calculate_gap_control(tracking_df)
        elif position.upper() in ['F', 'FORWARD']:
            metrics['high_danger_positioning'] = self._calculate_high_danger_positioning(tracking_df)
        
        return metrics
    
    def _calculate_goalie_crease_movement(self, tracking_df: pd.DataFrame) -> float:
        """Calculate goalie crease depth movement."""
        # Placeholder - would calculate depth from goal line
        return 5.0
    
    def _calculate_lateral_movement(self, tracking_df: pd.DataFrame) -> float:
        """Calculate lateral (side-to-side) movement."""
        if len(tracking_df) < 2:
            return 0.0
        
        x_col = self._find_column(tracking_df, ['x', 'x_coord', 'x_position'])
        if not x_col:
            return 0.0
        
        x_coords = tracking_df[x_col].values
        # Calculate total lateral distance
        lateral_dist = sum(abs(x_coords[i] - x_coords[i-1]) for i in range(1, len(x_coords)))
        return lateral_dist
    
    def _calculate_gap_control(self, tracking_df: pd.DataFrame) -> float:
        """Calculate defenseman gap control."""
        # Placeholder - would calculate distance to forwards
        return 8.0
    
    def _calculate_high_danger_positioning(self, tracking_df: pd.DataFrame) -> float:
        """Calculate time spent in high-danger areas."""
        # Placeholder - would identify high-danger zones
        return 0.3
