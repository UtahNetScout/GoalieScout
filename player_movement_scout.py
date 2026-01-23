#!/usr/bin/env python3
"""
GoalieScout-BDC-2026: Player Movement Scout
Main script for analyzing player movement data from Big Data Cup 2026.

This script:
1. Loads BDC 2026 dataset
2. Calculates movement metrics for all players
3. Generates AI-powered scouting reports
4. Assigns scores, tiers, and rankings
5. Creates visualizations
6. Outputs JSON reports
"""

import os
import sys
from dotenv import load_dotenv
import pandas as pd
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai_providers.factory import get_ai_provider
from src.data.loader import BDCDataLoader
from src.metrics.movement import MovementMetrics
from src.reports.generator import ReportGenerator
from src.visualization.plotter import MovementVisualizer


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        Configuration dictionary
    """
    load_dotenv()
    
    config = {
        'AI_PROVIDER': os.getenv('AI_PROVIDER', 'ollama'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'OPENAI_MODEL': os.getenv('OPENAI_MODEL', 'gpt-4'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'ANTHROPIC_MODEL': os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229'),
        'OLLAMA_BASE_URL': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
        'OLLAMA_MODEL': os.getenv('OLLAMA_MODEL', 'llama2'),
        'BDC_DATA_PATH': os.getenv('BDC_DATA_PATH', './sample_data/bdc_2026_data.csv'),
        'TRACKING_DATA_PATH': os.getenv('TRACKING_DATA_PATH', './sample_data/bdc_2026_tracking.parquet'),
        'OUTPUT_DIR': os.getenv('OUTPUT_DIR', './output'),
        'VISUALIZATIONS_DIR': os.getenv('VISUALIZATIONS_DIR', './output/visualizations'),
        'MIN_EVENTS_THRESHOLD': int(os.getenv('MIN_EVENTS_THRESHOLD', '10'))
    }
    
    return config


def create_sample_data():
    """
    Create sample data for demonstration purposes.
    This simulates what the BDC 2026 dataset might look like.
    """
    print("\n=== Creating Sample Data ===")
    
    os.makedirs('./sample_data', exist_ok=True)
    
    # Create sample event data
    sample_events = {
        'player_id': [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5],
        'player_name': ['Connor McDavid', 'Connor McDavid', 'Connor McDavid',
                       'Auston Matthews', 'Auston Matthews', 'Auston Matthews',
                       'Cale Makar', 'Cale Makar', 'Cale Makar',
                       'Igor Shesterkin', 'Igor Shesterkin', 'Igor Shesterkin',
                       'Nathan MacKinnon', 'Nathan MacKinnon', 'Nathan MacKinnon'],
        'position': ['F', 'F', 'F', 'F', 'F', 'F', 'D', 'D', 'D', 'G', 'G', 'G', 'F', 'F', 'F'],
        'team': ['EDM', 'EDM', 'EDM', 'TOR', 'TOR', 'TOR', 'COL', 'COL', 'COL', 'NYR', 'NYR', 'NYR', 'COL', 'COL', 'COL'],
        'event': ['shot', 'pass', 'carry', 'goal', 'shot', 'pass', 'pass', 'shot', 'block', 
                 'save', 'save', 'save', 'shot', 'goal', 'carry'],
        'time': [10.5, 25.3, 40.2, 55.1, 70.8, 85.5, 100.2, 115.7, 130.4, 145.9, 160.3, 175.8, 190.5, 205.2, 220.1]
    }
    
    event_df = pd.DataFrame(sample_events)
    event_df.to_csv('./sample_data/bdc_2026_data.csv', index=False)
    print(f"Created sample event data: ./sample_data/bdc_2026_data.csv")
    
    # Create sample tracking data
    import numpy as np
    
    tracking_data = []
    for player_id in [1, 2, 3, 4, 5]:
        # Generate 50 tracking points per player with realistic movement
        base_x = np.random.uniform(50, 150, 1)[0]
        base_y = np.random.uniform(20, 65, 1)[0]
        
        for i in range(50):
            x = base_x + np.random.normal(0, 10)
            y = base_y + np.random.normal(0, 5)
            tracking_data.append({
                'player_id': player_id,
                'frame': i,
                'time': i * 0.5,
                'x': max(0, min(200, x)),
                'y': max(0, min(85, y))
            })
    
    tracking_df = pd.DataFrame(tracking_data)
    tracking_df.to_parquet('./sample_data/bdc_2026_tracking.parquet', index=False)
    print(f"Created sample tracking data: ./sample_data/bdc_2026_tracking.parquet")
    print("Sample data created successfully!\n")


def main():
    """Main execution function."""
    print("=" * 70)
    print("GoalieScout-BDC-2026: Player Movement Scout")
    print("Adapted for Stathletes Big Data Cup 2026 - Player Movement Theme")
    print("=" * 70)
    
    # Load configuration
    config = load_config()
    print(f"\nAI Provider: {config['AI_PROVIDER']}")
    
    # Create sample data if files don't exist
    if not os.path.exists(config['BDC_DATA_PATH']) or not os.path.exists(config['TRACKING_DATA_PATH']):
        print("\nDataset files not found. Creating sample data for demonstration...")
        create_sample_data()
    
    # Create output directories
    os.makedirs(config['OUTPUT_DIR'], exist_ok=True)
    os.makedirs(config['VISUALIZATIONS_DIR'], exist_ok=True)
    
    # Initialize AI provider
    print("\n=== Initializing AI Provider ===")
    try:
        ai_provider = get_ai_provider(config['AI_PROVIDER'], config)
        print(f"✓ {config['AI_PROVIDER'].upper()} provider initialized")
    except Exception as e:
        print(f"✗ Error initializing AI provider: {e}")
        print("\nNote: If using Ollama, make sure it's running locally.")
        print("If using OpenAI/Anthropic, check your API keys in .env file.")
        return
    
    # Load data
    print("\n=== Loading Data ===")
    data_loader = BDCDataLoader(config)
    event_data, tracking_data = data_loader.load_data()
    
    if event_data is None or len(event_data) == 0:
        print("✗ No event data loaded. Cannot proceed.")
        return
    
    # Get players list
    players = data_loader.get_players_list()
    print(f"✓ Found {len(players)} players in dataset")
    
    # Initialize metrics calculator
    metrics_calc = MovementMetrics()
    
    # Initialize report generator
    report_gen = ReportGenerator(ai_provider)
    
    # Initialize visualizer
    visualizer = MovementVisualizer(config['VISUALIZATIONS_DIR'])
    
    # Process each player
    print("\n=== Processing Players ===")
    all_reports = []
    
    for idx, player_row in players.iterrows():
        player_id = player_row['player_id']
        player_name = player_row['player_name']
        position = player_row.get('position', 'Unknown')
        
        print(f"\nProcessing: {player_name} ({position})")
        
        # Get player data
        player_events = data_loader.get_player_events(player_id)
        player_tracking = data_loader.get_player_tracking(player_id)
        
        # Skip if insufficient data
        if len(player_events) < config['MIN_EVENTS_THRESHOLD']:
            print(f"  ⚠ Skipping (insufficient events: {len(player_events)})")
            continue
        
        # Calculate metrics
        print(f"  - Calculating metrics...")
        metrics = metrics_calc.calculate_all_metrics(player_tracking, player_events, position)
        
        # Generate report
        print(f"  - Generating AI report...")
        report = report_gen.generate_player_report(player_name, position, metrics)
        all_reports.append(report)
        
        print(f"  ✓ Score: {report['score']}/100 | Tier: {report['tier']}")
        
        # Create visualizations for top players (first 3 only for demo)
        if len(all_reports) <= 3 and len(player_tracking) > 0:
            print(f"  - Creating visualizations...")
            visualizer.plot_player_trajectory(player_tracking, player_name)
            visualizer.plot_position_heatmap(player_tracking, player_name)
    
    if len(all_reports) == 0:
        print("\n✗ No reports generated. Check data and thresholds.")
        return
    
    # Rank players
    print("\n=== Ranking Players ===")
    ranked_reports = report_gen.rank_players(all_reports)
    
    print(f"\nTop 5 Players:")
    for i, report in enumerate(ranked_reports[:5], 1):
        print(f"  {i}. {report['player_name']} ({report['position']}) - "
              f"Score: {report['score']}/100 | Tier: {report['tier']}")
    
    # Generate summary
    summary = report_gen.generate_summary(ranked_reports)
    
    print(f"\n=== Summary Statistics ===")
    print(f"Total Players Analyzed: {summary['total_players']}")
    print(f"Average Score: {summary['average_score']:.2f}")
    print(f"Tier Distribution: {summary['tier_distribution']}")
    
    # Save reports to JSON
    output_json = os.path.join(config['OUTPUT_DIR'], 'player_reports.json')
    report_gen.save_reports_json(ranked_reports, summary, output_json)
    
    # Create comparison visualization
    print("\n=== Creating Visualizations ===")
    visualizer.plot_top_players_comparison(ranked_reports, metric='score', top_n=min(10, len(ranked_reports)))
    
    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print(f"Reports saved to: {output_json}")
    print(f"Visualizations saved to: {config['VISUALIZATIONS_DIR']}")
    print("=" * 70)


if __name__ == '__main__':
    main()
