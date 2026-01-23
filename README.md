# GoalieScout

An all-in-one **AI-automated** hockey scouting platform leveraging generative AI engineering for advanced scouting, ranking, and performance analysis.

## 🎉 NEW: Big Data Cup 2026 Edition

**GoalieScout-BDC-2026** is now available! This adaptation extends the original GoalieScout framework for the **Stathletes Big Data Cup 2026** competition, focusing on the "Player Movement" theme.

### 🆕 What's New in BDC-2026 Edition?

- **All Positions**: Expanded from goalies-only to forwards, defensemen, and goalies
- **Movement Analytics**: Advanced player movement metrics (speed, distance, positioning)
- **BDC 2026 Data**: Direct support for Big Data Cup 2026 tracking dataset
- **Enhanced Visualizations**: Trajectory plots, heatmaps, and comparison charts
- **Position-Specific Metrics**: 
  - Forwards: High-danger positioning, on-puck carrying
  - Defensemen: Gap control, zone transitions
  - Goalies: Crease depth, lateral movement

### 📚 Documentation

- **[README_BDC_2026.md](README_BDC_2026.md)** - Complete BDC 2026 edition documentation
- **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** - Practical usage examples and tutorials

### 🚀 Quick Start (BDC 2026)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure (uses Ollama by default - free!)
cp .env.example .env

# Run with sample data
python player_movement_scout.py

# Or test the system
python test_system.py
```

---

## ✨ Original GoalieScout Framework

## ✨ Key Features

### Generative AI-Powered Scouting
- **Multi-Model AI Integration**:
  - OpenAI GPT-4 for premium insights.
  - Anthropic Claude for cost-effective alternatives.
  - Ollama’s local LLM models for zero API costs.
- **Core AI-Driven Metrics**:
  - Real-time ranking using AI model inputs.
  - Dynamic data enrichment with automation features.

### In-Depth Automation Ecosystem
- **Fully Automated Scouting System**:
  - AI-generated scores and reports.
  - Database management through JSON file systems.
  - Seamless web scraping of performance metrics.
- **Blogging and Social Media Suite with AI Integration**:
  - Automated blogging templates in Markdown or HTML formats.
  - Twitter integrations (X) with spotlight posts.

### Detailed Data Architecture for Professional Analytics
#### **Scouting Data Attributes:**
A robust pipeline ensures capturing parameters such as:
- Demographics (Name, Country, League, Birth).
- Robust database objects validate daily updates.

## 🚀 Usage Best Practices
- See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for detailed usage examples
- For BDC 2026 specific usage, see [README_BDC_2026.md](README_BDC_2026.md)

## 🏗️ Project Structure

```
GoalieScout/
├── player_movement_scout.py    # Main BDC 2026 analysis script
├── test_system.py               # Test suite
├── requirements.txt             # Dependencies
├── .env.example                 # Configuration template
├── README.md                    # This file
├── README_BDC_2026.md          # BDC 2026 documentation
├── USAGE_EXAMPLES.md           # Usage examples
├── src/                         # Source code
│   ├── ai_providers/           # AI provider implementations
│   ├── data/                   # Data loading
│   ├── metrics/                # Movement metrics
│   ├── reports/                # Report generation
│   └── visualization/          # Plotting
├── sample_data/                 # Data directory
└── output/                      # Generated reports
```

## 🤝 Contributing

Contributions are welcome! This project is designed to be modular and extensible.

## 📝 License

See the repository for license information.

## 🏆 Big Data Cup 2026

This project includes an adaptation for the Stathletes Big Data Cup 2026 competition. Learn more at the [official BDC repository](https://github.com/bigdatacup/Big-Data-Cup-2026).
