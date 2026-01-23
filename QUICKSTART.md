# GoalieScout-BDC-2026 Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Clone and Install (2 minutes)

```bash
git clone https://github.com/UtahNetScout/GoalieScout.git
cd GoalieScout
pip install -r requirements.txt
```

## Step 2: Configure (1 minute)

```bash
# Copy the example configuration
cp .env.example .env

# Default uses Ollama (free, local) - no changes needed!
# Or edit .env to use OpenAI/Anthropic with your API key
```

## Step 3: Run (2 minutes)

### Option A: Quick Test with Sample Data

```bash
python test_system.py
```

This will:
- ✓ Create sample data automatically
- ✓ Test all system components
- ✓ Generate example reports and visualizations
- ✓ Show you what the output looks like

### Option B: Full Analysis

```bash
python player_movement_scout.py
```

This runs the complete analysis pipeline.

## That's It! 🎉

Your results are in:
- `./output/test_player_reports.json` - Player reports with scores and rankings
- `./output/visualizations/*.png` - Movement trajectories and heatmaps

## What's Next?

### Use Real BDC 2026 Data

1. Download from: https://github.com/bigdatacup/Big-Data-Cup-2026/releases/tag/Data
2. Place files in `./sample_data/`
3. Update paths in `.env`
4. Run: `python player_movement_scout.py`

### Try Different AI Providers

**Ollama (Free, Local):**
```bash
# Install from https://ollama.ai
ollama pull llama2
ollama serve
# Already configured in .env by default!
```

**OpenAI:**
```bash
# Edit .env:
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

**Anthropic:**
```bash
# Edit .env:
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Need Help?

- 📖 Full docs: [README_BDC_2026.md](README_BDC_2026.md)
- 💡 Examples: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- 🐛 Issues: GitHub Issues

## Example Output

```json
{
  "summary": {
    "total_players": 5,
    "average_score": 91.6,
    "tier_distribution": {"S": 4, "A": 1}
  },
  "player_reports": [
    {
      "rank": 1,
      "player_name": "Connor McDavid",
      "score": 95,
      "tier": "S",
      "scouting_notes": "Elite skating ability..."
    }
  ]
}
```

Happy Scouting! 🏒
