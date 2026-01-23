"""
Data Loading Module
Handles loading and preprocessing of Big Data Cup 2026 dataset.
"""
import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


class BDCDataLoader:
    """Loads and preprocesses Big Data Cup 2026 dataset."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the data loader.
        
        Args:
            config: Configuration dictionary with data paths
        """
        self.config = config
        self.event_data_path = config.get('BDC_DATA_PATH')
        self.tracking_data_path = config.get('TRACKING_DATA_PATH')
        
        self.event_data = None
        self.tracking_data = None
    
    def load_data(self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Load event and tracking data from files.
        
        Returns:
            Tuple of (event_data, tracking_data) DataFrames
        """
        # Load event data
        if self.event_data_path and os.path.exists(self.event_data_path):
            try:
                if self.event_data_path.endswith('.csv'):
                    self.event_data = pd.read_csv(self.event_data_path)
                elif self.event_data_path.endswith('.parquet'):
                    self.event_data = pd.read_parquet(self.event_data_path)
                print(f"Loaded event data: {len(self.event_data)} rows")
            except Exception as e:
                print(f"Error loading event data: {e}")
        
        # Load tracking data
        if self.tracking_data_path and os.path.exists(self.tracking_data_path):
            try:
                if self.tracking_data_path.endswith('.csv'):
                    self.tracking_data = pd.read_csv(self.tracking_data_path)
                elif self.tracking_data_path.endswith('.parquet'):
                    self.tracking_data = pd.read_parquet(self.tracking_data_path)
                print(f"Loaded tracking data: {len(self.tracking_data)} rows")
            except Exception as e:
                print(f"Error loading tracking data: {e}")
        
        return self.event_data, self.tracking_data
    
    def get_players_list(self) -> pd.DataFrame:
        """
        Extract unique players from the dataset.
        
        Returns:
            DataFrame with player information (ID, name, position, team)
        """
        if self.event_data is None:
            return pd.DataFrame()
        
        # This is a placeholder - actual column names will depend on BDC dataset
        # Common column patterns: player_id, player_name, player, name, position, pos, team
        
        player_columns = []
        potential_id_cols = ['player_id', 'playerId', 'id']
        potential_name_cols = ['player_name', 'playerName', 'name', 'player']
        potential_pos_cols = ['position', 'pos', 'player_position']
        potential_team_cols = ['team', 'team_name', 'teamName']
        
        # Find which columns exist
        id_col = next((c for c in potential_id_cols if c in self.event_data.columns), None)
        name_col = next((c for c in potential_name_cols if c in self.event_data.columns), None)
        pos_col = next((c for c in potential_pos_cols if c in self.event_data.columns), None)
        team_col = next((c for c in potential_team_cols if c in self.event_data.columns), None)
        
        if id_col and name_col:
            player_data = self.event_data[[id_col, name_col]].drop_duplicates()
            player_data = player_data.rename(columns={
                id_col: 'player_id',
                name_col: 'player_name'
            })
            
            if pos_col:
                pos_data = self.event_data[[id_col, pos_col]].drop_duplicates()
                pos_data = pos_data.rename(columns={id_col: 'player_id', pos_col: 'position'})
                player_data = player_data.merge(pos_data, on='player_id', how='left')
            else:
                player_data['position'] = 'Unknown'
            
            if team_col:
                team_data = self.event_data[[id_col, team_col]].drop_duplicates()
                team_data = team_data.rename(columns={id_col: 'player_id', team_col: 'team'})
                player_data = player_data.merge(team_data, on='player_id', how='left')
            else:
                player_data['team'] = 'Unknown'
            
            return player_data
        
        # If no standard columns found, return empty DataFrame
        return pd.DataFrame(columns=['player_id', 'player_name', 'position', 'team'])
    
    def get_player_events(self, player_id: Any) -> pd.DataFrame:
        """
        Get all events for a specific player.
        
        Args:
            player_id: The player's ID
            
        Returns:
            DataFrame of events for this player
        """
        if self.event_data is None:
            return pd.DataFrame()
        
        # Find player ID column
        id_col = None
        for col in ['player_id', 'playerId', 'id']:
            if col in self.event_data.columns:
                id_col = col
                break
        
        if id_col:
            return self.event_data[self.event_data[id_col] == player_id].copy()
        return pd.DataFrame()
    
    def get_player_tracking(self, player_id: Any) -> pd.DataFrame:
        """
        Get tracking data for a specific player.
        
        Args:
            player_id: The player's ID
            
        Returns:
            DataFrame of tracking data for this player
        """
        if self.tracking_data is None:
            return pd.DataFrame()
        
        # Find player ID column
        id_col = None
        for col in ['player_id', 'playerId', 'id']:
            if col in self.tracking_data.columns:
                id_col = col
                break
        
        if id_col:
            return self.tracking_data[self.tracking_data[id_col] == player_id].copy()
        return pd.DataFrame()
