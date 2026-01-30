# GoalieScout-BDC-2026: Player Movement Scout

> **Note:** This project is now maintained in a dedicated repository at: **[GoalieScout-BDC-2026](https://github.com/UtahNetScout/GoalieScout-BDC-2026)**

**An AI-powered hockey player movement analysis platform adapted for the Stathletes Big Data Cup 2026.**

This project extends the GoalieScout framework to analyze player movement across **all positions** (goalies, forwards, defensemen) using advanced tracking data from the Big Data Cup 2026 competition, with a focus on the "Player Movement" theme.

## 🔗 Repository Information

- **New Dedicated Repository:** [github.com/UtahNetScout/GoalieScout-BDC-2026](https://github.com/UtahNetScout/GoalieScout-BDC-2026)
- **Clone Command:** `git clone https://github.com/UtahNetScout/GoalieScout-BDC-2026.git`
- **Migration Guide:** See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for transfer instructions

## 🎯 Overview

GoalieScout-BDC-2026 is a comprehensive scouting platform that:
- Analyzes player movement patterns from frame-by-frame tracking data
- Calculates advanced movement metrics (speed, distance, positioning, space creation)
- Generates AI-powered scouting reports using multiple LLM providers
- Assigns scores (0-100), tiers (S/A/B/C/D/F), and rankings
- Creates visualizations (trajectories, heatmaps, comparisons)
- Outputs structured JSON reports for further analysis

## ✨ Key Features

### Multi-Position Support
- **Forwards**: On-puck carrying, high-danger positioning, offensive zone movement
- **Defensemen**: Gap control, zone transitions, defensive positioning
- **Goalies**: Crease depth/lateral movement, positioning efficiency

### Advanced Movement Metrics
- Total distance traveled and average/max speed
- On-puck carrying distance and efficiency
- Off-puck space creation (Voronoi-based)
- Direction changes and agility
- Position-specific metrics (gap control, crease movement, etc.)
- Zone transition speed and efficiency

### Multi-LLM Provider Support
- **Ollama** (default): Free, local LLM models - zero API costs
- **OpenAI GPT-4**: Premium AI insights
- **Anthropic Claude**: Cost-effective alternative

### Automated Output
- AI-generated scouting reports (3-5 sentences per player)
- Numeric scores (0-100 scale)
- Tier ratings (S/A/B/C/D/F)
- Player rankings
- JSON export for further analysis

### Visualizations
- Player movement trajectories on rink
- Position heatmaps
- Top player comparison charts

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- (Optional) Ollama installed locally for free LLM support

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/UtahNetScout/GoalieScout-BDC-2026.git
   cd GoalieScout-BDC-2026
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Download BDC 2026 Dataset** (Optional)
   
   Download the official Big Data Cup 2026 dataset from:
   https://github.com/bigdatacup/Big-Data-Cup-2026/releases/tag/Data
   
   Place the files in `./sample_data/` directory:
   - Event data (CSV/Parquet): `bdc_2026_data.csv`
   - Tracking data (CSV/Parquet): `bdc_2026_tracking.parquet`
   
   *Note: If you don't have the dataset, the script will create sample data for demonstration.*

## 📖 Usage

### Basic Usage

Run the main script with default settings (Ollama):
```bash
python player_movement_scout.py
```

### Configuration

Edit `.env` file to customize:

```bash
# AI Provider (ollama, openai, or anthropic)
AI_PROVIDER=ollama

# For OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4

# For Anthropic
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# For Ollama (local, free)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Data paths
BDC_DATA_PATH=./sample_data/bdc_2026_data.csv
TRACKING_DATA_PATH=./sample_data/bdc_2026_tracking.parquet

# Output directory
OUTPUT_DIR=./output
VISUALIZATIONS_DIR=./output/visualizations

# Minimum events threshold (filter low-activity players)
MIN_EVENTS_THRESHOLD=10
```

### Using Different AI Providers

**Ollama (Free, Local):**
```bash
# Install Ollama: https://ollama.ai
ollama pull llama2
# Set AI_PROVIDER=ollama in .env
python player_movement_scout.py
```

**OpenAI:**
```bash
# Set AI_PROVIDER=openai in .env
# Add your OPENAI_API_KEY to .env
python player_movement_scout.py
```

**Anthropic:**
```bash
# Set AI_PROVIDER=anthropic in .env
# Add your ANTHROPIC_API_KEY to .env
python player_movement_scout.py
```

## 📊 Output

### JSON Report Structure

The script generates `./output/player_reports.json`:

```json
{
  "summary": {
    "total_players": 5,
    "tier_distribution": {"S": 1, "A": 2, "B": 1, "C": 1},
    "top_3_players": [...],
    "average_score": 78.4
  },
  "player_reports": [
    {
      "rank": 1,
      "player_name": "Connor McDavid",
      "position": "F",
      "score": 95,
      "tier": "S",
      "metrics": {
        "total_distance": 1250.5,
        "average_speed": 5.2,
        "max_speed": 12.8,
        "direction_changes": 45,
        "on_puck_distance": 320.0,
        "space_creation": 15.0,
        "events_count": 87
      },
      "scouting_notes": "Elite movement player with exceptional speed..."
    }
  ]
}
```

### Visualizations

Generated in `./output/visualizations/`:
- `{player_name}_trajectory.png` - Movement path on rink
- `{player_name}_heatmap.png` - Position frequency heatmap
- `top_10_players_score.png` - Ranked comparison chart

## 🏗️ Project Structure

```
GoalieScout-BDC-2026/
├── player_movement_scout.py    # Main script
├── requirements.txt             # Python dependencies
├── .env.example                 # Configuration template
├── README.md                    # This file
├── config/                      # Configuration files
├── sample_data/                 # Sample/downloaded BDC data
│   ├── bdc_2026_data.csv
│   └── bdc_2026_tracking.parquet
├── src/
│   ├── ai_providers/           # AI provider implementations
│   │   ├── __init__.py
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── ollama_provider.py
│   │   └── factory.py
│   ├── data/                   # Data loading and preprocessing
│   │   ├── __init__.py
│   │   └── loader.py
│   ├── metrics/                # Movement metrics calculations
│   │   ├── __init__.py
│   │   └── movement.py
│   ├── reports/                # Report generation
│   │   ├── __init__.py
│   │   └── generator.py
│   └── visualization/          # Plotting and visualization
│       ├── __init__.py
│       └── plotter.py
└── output/                     # Generated reports and plots
    ├── player_reports.json
    └── visualizations/
```

## 🔬 Movement Metrics Explained

### Universal Metrics (All Positions)
- **Total Distance**: Total distance traveled during tracked periods
- **Average Speed**: Mean speed across all movements
- **Max Speed**: Peak speed achieved
- **Direction Changes**: Number of significant directional shifts (>45°)
- **On-Puck Distance**: Distance traveled while controlling the puck
- **Space Creation**: Average distance to nearest opponent (off-puck positioning)

### Position-Specific Metrics

**Forwards:**
- High-Danger Positioning: Time spent in scoring areas
- Offensive zone movement patterns

**Defensemen:**
- Gap Control: Distance management to opposing forwards
- Zone transition efficiency

**Goalies:**
- Crease Depth Movement: Forward/back positioning
- Lateral Movement: Side-to-side agility

## 🤝 Contributing

This project is adapted from the original GoalieScout platform for the Big Data Cup 2026 competition. Contributions, suggestions, and improvements are welcome!

## 📝 License

This project extends the GoalieScout framework. Please refer to the original project for licensing information.

## 🏆 Big Data Cup 2026

This project is designed for the Stathletes Big Data Cup 2026 competition:
- **Theme**: Player Movement
- **Dataset**: Official BDC 2026 tracking and event data
- **Goal**: Demonstrate innovative player movement analysis

## 📚 References

- [Big Data Cup 2026](https://github.com/bigdatacup/Big-Data-Cup-2026)
- [Original GoalieScout Project](https://github.com/UtahNetScout/GoalieScout)
- [Ollama - Free Local LLMs](https://ollama.ai)

## 🆘 Troubleshooting

**Problem**: "Could not connect to Ollama"
- **Solution**: Make sure Ollama is installed and running: `ollama serve`

**Problem**: "OpenAI API key not found"
- **Solution**: Add your API key to `.env` file: `OPENAI_API_KEY=your_key_here`

**Problem**: "No data loaded"
- **Solution**: Ensure data files exist in `./sample_data/` or run with sample data generation

**Problem**: "ModuleNotFoundError"
- **Solution**: Install all dependencies: `pip install -r requirements.txt`

---

**Created for the Stathletes Big Data Cup 2026 - Player Movement Theme**

*Leveraging AI and advanced analytics to revolutionize hockey scouting.*
