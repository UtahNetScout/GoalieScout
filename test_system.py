#!/usr/bin/env python3
"""
Test script to verify GoalieScout-BDC-2026 functionality
This creates sample data and runs the analysis with a mock AI provider.
"""

import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data.loader import BDCDataLoader
from src.metrics.movement import MovementMetrics
from src.visualization.plotter import MovementVisualizer
import pandas as pd
import numpy as np


class MockAIProvider:
    """Mock AI provider for testing without API keys."""
    
    def generate_report(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate a mock scouting report."""
        if "McDavid" in prompt:
            return "Elite skating ability with exceptional speed and agility. Creates space effectively and shows strong puck-carrying skills. Demonstrates excellent positional awareness and quick direction changes. Key strength is dynamic movement in all zones."
        elif "Matthews" in prompt:
            return "Strong two-way forward with efficient movement patterns. Excellent positioning in high-danger areas. Shows good speed and effective use of space. Reliable in both offensive and defensive zones with smart movement decisions."
        elif "Makar" in prompt:
            return "Outstanding mobility for a defenseman with excellent gap control. Quick transitions and strong positioning. Creates plays through intelligent movement. Elite skating ability allows for effective zone coverage."
        elif "Shesterkin" in prompt:
            return "Excellent crease management with strong lateral movement. Positioning is elite with quick adjustments. Demonstrates excellent depth control and spatial awareness. Movement efficiency is a key strength."
        elif "MacKinnon" in prompt:
            return "Dynamic skating with explosive speed. Creates space through intelligent off-puck movement. Strong in transitions with quick directional changes. High-energy player with excellent positioning awareness."
        else:
            return "Good movement patterns with solid positional awareness. Shows adequate speed and effective space usage. Demonstrates reliable skating fundamentals and good decision-making."
    
    def generate_score(self, prompt: str) -> int:
        """Generate a mock score."""
        if "McDavid" in prompt:
            return 95
        elif "Matthews" in prompt:
            return 88
        elif "Makar" in prompt:
            return 92
        elif "Shesterkin" in prompt:
            return 90
        elif "MacKinnon" in prompt:
            return 93
        else:
            return 75


def create_sample_data():
    """Create sample data for testing."""
    print("\n=== Creating Sample Data ===")
    
    os.makedirs('./sample_data', exist_ok=True)
    
    # Create sample event data
    sample_events = {
        'player_id': [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5],
        'player_name': ['Connor McDavid'] * 5 + ['Auston Matthews'] * 5 + ['Cale Makar'] * 5 + 
                       ['Igor Shesterkin'] * 5 + ['Nathan MacKinnon'] * 5,
        'position': ['F'] * 5 + ['F'] * 5 + ['D'] * 5 + ['G'] * 5 + ['F'] * 5,
        'team': ['EDM'] * 5 + ['TOR'] * 5 + ['COL'] * 5 + ['NYR'] * 5 + ['COL'] * 5,
        'event': ['shot', 'pass', 'carry', 'goal', 'pass'] * 5,
        'time': list(range(0, 125, 5))
    }
    
    event_df = pd.DataFrame(sample_events)
    event_df.to_csv('./sample_data/bdc_2026_data.csv', index=False)
    print(f"✓ Created event data: {len(event_df)} events")
    
    # Create sample tracking data with more realistic movement
    tracking_data = []
    player_configs = [
        (1, 'Connor McDavid', 100, 42, 15, 8),  # Center ice, high variance
        (2, 'Auston Matthews', 120, 35, 12, 7),  # Offensive zone
        (3, 'Cale Makar', 80, 42, 10, 6),       # Defensive zone
        (4, 'Igor Shesterkin', 20, 42, 3, 2),   # Near goal, low variance
        (5, 'Nathan MacKinnon', 110, 50, 14, 7) # Offensive zone, wing
    ]
    
    for player_id, name, base_x, base_y, x_var, y_var in player_configs:
        # Generate realistic movement with some patterns
        for i in range(100):
            # Add some realistic patterns (back and forth, curves)
            t = i * 0.5
            x = base_x + np.sin(t / 10) * x_var + np.random.normal(0, 3)
            y = base_y + np.cos(t / 8) * y_var + np.random.normal(0, 2)
            
            tracking_data.append({
                'player_id': player_id,
                'frame': i,
                'time': t,
                'x': max(0, min(200, x)),
                'y': max(0, min(85, y))
            })
    
    tracking_df = pd.DataFrame(tracking_data)
    tracking_df.to_parquet('./sample_data/bdc_2026_tracking.parquet', index=False)
    print(f"✓ Created tracking data: {len(tracking_df)} frames")
    print("Sample data created successfully!\n")


def test_data_loading():
    """Test data loading functionality."""
    print("=== Testing Data Loading ===")
    
    config = {
        'BDC_DATA_PATH': './sample_data/bdc_2026_data.csv',
        'TRACKING_DATA_PATH': './sample_data/bdc_2026_tracking.parquet'
    }
    
    loader = BDCDataLoader(config)
    event_data, tracking_data = loader.load_data()
    
    assert event_data is not None, "Event data should be loaded"
    assert tracking_data is not None, "Tracking data should be loaded"
    print(f"✓ Event data: {len(event_data)} rows")
    print(f"✓ Tracking data: {len(tracking_data)} rows")
    
    players = loader.get_players_list()
    print(f"✓ Found {len(players)} players")
    
    return loader


def test_metrics_calculation(loader):
    """Test metrics calculation."""
    print("\n=== Testing Metrics Calculation ===")
    
    metrics_calc = MovementMetrics()
    players = loader.get_players_list()
    
    for idx, player_row in players.iterrows():
        player_id = player_row['player_id']
        player_name = player_row['player_name']
        position = player_row['position']
        
        player_events = loader.get_player_events(player_id)
        player_tracking = loader.get_player_tracking(player_id)
        
        metrics = metrics_calc.calculate_all_metrics(player_tracking, player_events, position)
        
        print(f"\n{player_name} ({position}):")
        print(f"  - Total Distance: {metrics['total_distance']:.2f}")
        print(f"  - Avg Speed: {metrics['average_speed']:.2f}")
        print(f"  - Max Speed: {metrics['max_speed']:.2f}")
        print(f"  - Direction Changes: {metrics['direction_changes']}")
    
    print("\n✓ Metrics calculation working")


def test_visualization(loader):
    """Test visualization creation."""
    print("\n=== Testing Visualizations ===")
    
    os.makedirs('./output/visualizations', exist_ok=True)
    visualizer = MovementVisualizer('./output/visualizations')
    
    players = loader.get_players_list()
    
    # Create visualizations for first two players
    for idx, player_row in players.head(2).iterrows():
        player_id = player_row['player_id']
        player_name = player_row['player_name']
        player_tracking = loader.get_player_tracking(player_id)
        
        print(f"\nCreating visualizations for {player_name}...")
        visualizer.plot_player_trajectory(player_tracking, player_name)
        visualizer.plot_position_heatmap(player_tracking, player_name)
    
    print("\n✓ Visualizations created")


def test_report_generation(loader):
    """Test report generation with mock AI."""
    print("\n=== Testing Report Generation ===")
    
    from src.reports.generator import ReportGenerator
    
    mock_ai = MockAIProvider()
    report_gen = ReportGenerator(mock_ai)
    
    metrics_calc = MovementMetrics()
    players = loader.get_players_list()
    
    all_reports = []
    
    for idx, player_row in players.iterrows():
        player_id = player_row['player_id']
        player_name = player_row['player_name']
        position = player_row['position']
        
        player_events = loader.get_player_events(player_id)
        player_tracking = loader.get_player_tracking(player_id)
        
        metrics = metrics_calc.calculate_all_metrics(player_tracking, player_events, position)
        report = report_gen.generate_player_report(player_name, position, metrics)
        all_reports.append(report)
        
        print(f"\n{player_name} ({position}):")
        print(f"  Score: {report['score']}/100 | Tier: {report['tier']}")
        print(f"  Report: {report['scouting_notes'][:80]}...")
    
    # Rank players
    ranked_reports = report_gen.rank_players(all_reports)
    
    print("\n=== Rankings ===")
    for report in ranked_reports:
        print(f"  {report['rank']}. {report['player_name']} - {report['score']}/100 ({report['tier']})")
    
    # Generate summary
    summary = report_gen.generate_summary(ranked_reports)
    print(f"\n=== Summary ===")
    print(f"  Total Players: {summary['total_players']}")
    print(f"  Average Score: {summary['average_score']:.2f}")
    print(f"  Tier Distribution: {summary['tier_distribution']}")
    
    # Save to JSON
    os.makedirs('./output', exist_ok=True)
    output_path = './output/test_player_reports.json'
    report_gen.save_reports_json(ranked_reports, summary, output_path)
    
    print(f"\n✓ Reports saved to {output_path}")
    
    # Create comparison visualization
    visualizer = MovementVisualizer('./output/visualizations')
    visualizer.plot_top_players_comparison(ranked_reports, metric='score', top_n=5)
    
    print("✓ Report generation working")
    
    return ranked_reports


def main():
    """Run all tests."""
    print("=" * 70)
    print("GoalieScout-BDC-2026 Test Suite")
    print("=" * 70)
    
    # Create sample data
    create_sample_data()
    
    # Test data loading
    loader = test_data_loading()
    
    # Test metrics
    test_metrics_calculation(loader)
    
    # Test visualizations
    test_visualization(loader)
    
    # Test report generation
    reports = test_report_generation(loader)
    
    print("\n" + "=" * 70)
    print("✓ All Tests Passed!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - ./sample_data/bdc_2026_data.csv")
    print("  - ./sample_data/bdc_2026_tracking.parquet")
    print("  - ./output/test_player_reports.json")
    print("  - ./output/visualizations/*.png")
    print("\nThe system is ready to use with real BDC 2026 data!")
    print("=" * 70)


if __name__ == '__main__':
    main()
