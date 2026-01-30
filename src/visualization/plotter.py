"""
Visualization Module
Creates plots and heatmaps for player movement analysis.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional


class MovementVisualizer:
    """Create visualizations for player movement data."""
    
    def __init__(self, output_dir: str = './output/visualizations'):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory to save visualization files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Standard NHL rink dimensions (in feet)
        self.rink_length = 200
        self.rink_width = 85
    
    def plot_player_trajectory(self, tracking_df: pd.DataFrame, player_name: str, 
                               save_path: Optional[str] = None):
        """
        Plot a player's movement trajectory on a hockey rink.
        
        Args:
            tracking_df: DataFrame with x, y coordinates
            player_name: Name of the player
            save_path: Optional path to save the figure
        """
        if len(tracking_df) == 0:
            print(f"No tracking data available for {player_name}")
            return
        
        # Find coordinate columns
        x_col = self._find_column(tracking_df, ['x', 'x_coord', 'x_position'])
        y_col = self._find_column(tracking_df, ['y', 'y_coord', 'y_position'])
        
        if not x_col or not y_col:
            print(f"No coordinate columns found for {player_name}")
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Draw simplified rink outline
        self._draw_rink_outline(ax)
        
        # Plot trajectory
        x_coords = tracking_df[x_col].values
        y_coords = tracking_df[y_col].values
        
        # Plot as a line with gradient (earlier = blue, later = red)
        colors = np.linspace(0, 1, len(x_coords))
        for i in range(len(x_coords) - 1):
            ax.plot(x_coords[i:i+2], y_coords[i:i+2], 
                   color=plt.cm.coolwarm(colors[i]), alpha=0.6, linewidth=2)
        
        # Mark start and end
        ax.scatter(x_coords[0], y_coords[0], color='green', s=100, 
                  label='Start', zorder=5, edgecolors='black')
        ax.scatter(x_coords[-1], y_coords[-1], color='red', s=100, 
                  label='End', zorder=5, edgecolors='black')
        
        ax.set_title(f'Movement Trajectory: {player_name}', fontsize=14, fontweight='bold')
        ax.legend()
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Trajectory plot saved to: {save_path}")
        else:
            default_path = os.path.join(self.output_dir, f'{player_name}_trajectory.png')
            plt.savefig(default_path, dpi=300, bbox_inches='tight')
            print(f"Trajectory plot saved to: {default_path}")
        
        plt.close()
    
    def plot_position_heatmap(self, tracking_df: pd.DataFrame, player_name: str,
                             save_path: Optional[str] = None):
        """
        Create a heatmap of player positioning.
        
        Args:
            tracking_df: DataFrame with x, y coordinates
            player_name: Name of the player
            save_path: Optional path to save the figure
        """
        if len(tracking_df) == 0:
            print(f"No tracking data available for {player_name}")
            return
        
        # Find coordinate columns
        x_col = self._find_column(tracking_df, ['x', 'x_coord', 'x_position'])
        y_col = self._find_column(tracking_df, ['y', 'y_coord', 'y_position'])
        
        if not x_col or not y_col:
            print(f"No coordinate columns found for {player_name}")
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Draw simplified rink outline
        self._draw_rink_outline(ax)
        
        # Create 2D histogram (heatmap)
        x_coords = tracking_df[x_col].values
        y_coords = tracking_df[y_col].values
        
        # Create heatmap
        heatmap, xedges, yedges = np.histogram2d(x_coords, y_coords, bins=30)
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        
        im = ax.imshow(heatmap.T, extent=extent, origin='lower', 
                      cmap='YlOrRd', alpha=0.6, aspect='auto')
        
        plt.colorbar(im, ax=ax, label='Time Spent')
        
        ax.set_title(f'Position Heatmap: {player_name}', fontsize=14, fontweight='bold')
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Heatmap saved to: {save_path}")
        else:
            default_path = os.path.join(self.output_dir, f'{player_name}_heatmap.png')
            plt.savefig(default_path, dpi=300, bbox_inches='tight')
            print(f"Heatmap saved to: {default_path}")
        
        plt.close()
    
    def plot_top_players_comparison(self, reports: List[Dict[str, Any]], 
                                   metric: str = 'score',
                                   top_n: int = 10,
                                   save_path: Optional[str] = None):
        """
        Create a bar chart comparing top players.
        
        Args:
            reports: List of player reports
            metric: Metric to compare (default: 'score')
            top_n: Number of top players to show
            save_path: Optional path to save the figure
        """
        if len(reports) == 0:
            print("No reports available for comparison")
            return
        
        # Get top N players
        top_players = reports[:top_n]
        
        # Extract data
        names = [r['player_name'] for r in top_players]
        values = [r[metric] for r in top_players]
        colors = [self._tier_to_color(r['tier']) for r in top_players]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        y_pos = np.arange(len(names))
        bars = ax.barh(y_pos, values, color=colors, alpha=0.7, edgecolor='black')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names)
        ax.invert_yaxis()  # Top player at the top
        ax.set_xlabel(metric.replace('_', ' ').title(), fontsize=12)
        ax.set_title(f'Top {top_n} Players by {metric.replace("_", " ").title()}', 
                    fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, values)):
            ax.text(value, i, f' {value:.1f}', 
                   va='center', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Comparison plot saved to: {save_path}")
        else:
            default_path = os.path.join(self.output_dir, f'top_{top_n}_players_{metric}.png')
            plt.savefig(default_path, dpi=300, bbox_inches='tight')
            print(f"Comparison plot saved to: {default_path}")
        
        plt.close()
    
    def _draw_rink_outline(self, ax):
        """Draw a simplified hockey rink outline."""
        # For simplicity, just draw a rectangle
        # In a full implementation, this would include all rink markings
        rect = patches.Rectangle((0, 0), self.rink_length, self.rink_width,
                                linewidth=2, edgecolor='black', facecolor='lightblue', alpha=0.3)
        ax.add_patch(rect)
        
        # Center line
        ax.axvline(x=self.rink_length/2, color='red', linestyle='--', linewidth=2, alpha=0.5)
        
        # Blue lines
        ax.axvline(x=self.rink_length*0.25, color='blue', linewidth=2, alpha=0.5)
        ax.axvline(x=self.rink_length*0.75, color='blue', linewidth=2, alpha=0.5)
        
        ax.set_xlim(0, self.rink_length)
        ax.set_ylim(0, self.rink_width)
        ax.set_aspect('equal')
    
    @staticmethod
    def _find_column(df: pd.DataFrame, possible_names: List[str]) -> str:
        """Find which column name exists in the DataFrame."""
        for name in possible_names:
            if name in df.columns:
                return name
        return ""
    
    @staticmethod
    def _tier_to_color(tier: str) -> str:
        """Convert tier to a color for visualization."""
        color_map = {
            'S': '#FFD700',  # Gold
            'A': '#32CD32',  # Lime Green
            'B': '#4169E1',  # Royal Blue
            'C': '#FFA500',  # Orange
            'D': '#FF6347',  # Tomato
            'F': '#DC143C'   # Crimson
        }
        return color_map.get(tier, '#808080')  # Gray as default
