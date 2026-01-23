# GoalieScout-BDC-2026 Usage Examples

This document provides practical examples of using the GoalieScout-BDC-2026 system.

## Quick Start

### 1. Basic Setup

```bash
# Clone the repository
git clone https://github.com/UtahNetScout/GoalieScout.git
cd GoalieScout

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp .env.example .env
# Edit .env with your preferred AI provider
```

### 2. Using with Sample Data

The system automatically creates sample data if BDC 2026 dataset is not available:

```bash
python player_movement_scout.py
```

This will:
- Create sample event and tracking data
- Analyze 5 sample players
- Generate reports and visualizations
- Output JSON with rankings

### 3. Testing the System

Run the test suite to verify everything works:

```bash
python test_system.py
```

## Configuration Examples

### Using Ollama (Free, Local)

**Step 1**: Install and start Ollama
```bash
# Install from https://ollama.ai
ollama pull llama2
ollama serve
```

**Step 2**: Configure `.env`
```bash
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

**Step 3**: Run
```bash
python player_movement_scout.py
```

### Using OpenAI GPT-4

**Configure `.env`:**
```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
```

### Using Anthropic Claude

**Configure `.env`:**
```bash
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

## Working with Real BDC 2026 Data

### Download the Dataset

1. Go to: https://github.com/bigdatacup/Big-Data-Cup-2026/releases/tag/Data
2. Download the event and tracking data files
3. Place them in `./sample_data/` directory

### Configure Data Paths

Update `.env` with actual file paths:
```bash
BDC_DATA_PATH=./sample_data/bdc_2026_events.csv
TRACKING_DATA_PATH=./sample_data/bdc_2026_tracking.parquet
```

### Run Analysis

```bash
python player_movement_scout.py
```

## Output Examples

### JSON Report Structure

The system generates `./output/player_reports.json` with this structure:

```json
{
  "summary": {
    "total_players": 5,
    "tier_distribution": {
      "S": 4,
      "A": 1
    },
    "top_3_players": [
      {
        "rank": 1,
        "name": "Connor McDavid",
        "position": "F",
        "score": 95,
        "tier": "S"
      }
    ],
    "average_score": 91.6
  },
  "player_reports": [
    {
      "rank": 1,
      "player_name": "Connor McDavid",
      "position": "F",
      "metrics": {
        "total_distance": 420.94,
        "average_speed": 8.50,
        "max_speed": 21.89,
        "direction_changes": 85,
        "on_puck_distance": 10.0,
        "space_creation": 15.0,
        "events_count": 5,
        "high_danger_positioning": 0.3
      },
      "scouting_notes": "Elite skating ability with exceptional speed...",
      "score": 95,
      "tier": "S"
    }
  ]
}
```

### Console Output Example

```
======================================================================
GoalieScout-BDC-2026: Player Movement Scout
Adapted for Stathletes Big Data Cup 2026 - Player Movement Theme
======================================================================

AI Provider: ollama

=== Loading Data ===
Loaded event data: 25 rows
Loaded tracking data: 500 rows
✓ Found 5 players in dataset

=== Processing Players ===

Processing: Connor McDavid (F)
  - Calculating metrics...
  - Generating AI report...
  ✓ Score: 95/100 | Tier: S

Processing: Auston Matthews (F)
  - Calculating metrics...
  - Generating AI report...
  ✓ Score: 88/100 | Tier: A

=== Ranking Players ===

Top 5 Players:
  1. Connor McDavid (F) - Score: 95/100 | Tier: S
  2. Nathan MacKinnon (F) - Score: 93/100 | Tier: S
  3. Cale Makar (D) - Score: 92/100 | Tier: S
  4. Igor Shesterkin (G) - Score: 90/100 | Tier: S
  5. Auston Matthews (F) - Score: 88/100 | Tier: A

=== Summary Statistics ===
Total Players Analyzed: 5
Average Score: 91.60
Tier Distribution: {'S': 4, 'A': 1}

=== Creating Visualizations ===
Trajectory plot saved to: ./output/visualizations/Connor McDavid_trajectory.png
Heatmap saved to: ./output/visualizations/Connor McDavid_heatmap.png
...

======================================================================
Analysis Complete!
Reports saved to: ./output/player_reports.json
Visualizations saved to: ./output/visualizations
======================================================================
```

### Generated Visualizations

The system creates several types of visualizations:

1. **Player Trajectories** (`{player_name}_trajectory.png`)
   - Shows movement path on hockey rink
   - Color gradient from start (blue) to end (red)
   - Includes simplified rink markings

2. **Position Heatmaps** (`{player_name}_heatmap.png`)
   - Shows where players spend most time
   - Red = high frequency, Yellow = low frequency
   - Overlaid on rink diagram

3. **Top Players Comparison** (`top_10_players_score.png`)
   - Horizontal bar chart
   - Color-coded by tier
   - Shows relative scores

## Advanced Usage

### Customizing Thresholds

Edit `.env` to change minimum events threshold:
```bash
MIN_EVENTS_THRESHOLD=20  # Only analyze players with 20+ events
```

### Filtering by Position

Modify `player_movement_scout.py` to filter positions:

```python
# After loading players
players = players[players['position'] == 'F']  # Only forwards
# or
players = players[players['position'].isin(['F', 'D'])]  # Forwards and defense
```

### Custom Output Directory

```bash
OUTPUT_DIR=./my_analysis
VISUALIZATIONS_DIR=./my_analysis/viz
```

## Performance Tips

1. **Start with small datasets** - Test with 5-10 players first
2. **Use Ollama for development** - No API costs, unlimited usage
3. **Enable visualization selectively** - Generate viz only for top N players
4. **Batch processing** - Process players in groups if dataset is large

## Troubleshooting

### "Could not connect to Ollama"

```bash
# Start Ollama service
ollama serve

# In another terminal
python player_movement_scout.py
```

### "API key not found"

Check your `.env` file has the correct key:
```bash
cat .env | grep API_KEY
```

### "No data loaded"

Verify data files exist:
```bash
ls -lh sample_data/
```

### Import errors

Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. Download real BDC 2026 dataset
2. Experiment with different AI providers
3. Customize metrics calculations
4. Add more visualization types
5. Export results for further analysis

For more information, see:
- [README_BDC_2026.md](README_BDC_2026.md) - Full documentation
- [Big Data Cup 2026](https://github.com/bigdatacup/Big-Data-Cup-2026) - Official competition
