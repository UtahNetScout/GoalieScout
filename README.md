# Black Ops Goalie Scouting Platform

The Black Ops Goalie Scouting Platform is a cutting-edge, AI-driven solution designed to revolutionize the way hockey goalies are scouted, analyzed, and ranked. Leveraging powerful generative AI models and NHL-grade advanced analytics, this platform provides unparalleled insights into goalie performance across a wide range of leagues and competition levels.

## ✨ Key Features

### 🏒 Black Ops Score — The Signature Metric

The **Black Ops Score** (0–100) is the platform's proprietary composite rating system that aggregates multiple advanced metrics into a single, interpretable number:

| Score | Tier | Description |
|-------|------|-------------|
| 90–100 | **Elite** | NHL Starter potential |
| 80–89 | **Above Average** | NHL/AHL calibre |
| 70–79 | **Average** | AHL/Top College |
| 60–69 | **Below Average** | Developmental |
| < 60 | **Needs Improvement** | Development League |

Weight breakdown: GSAx (25%) · High-Danger SV% (20%) · Rebound Control (15%) · Consistency (15%) · Movement (10%) · Puck Handling (10%) · Development (5%)

### 📊 NHL-Grade Advanced Analytics

- **GSAx (Goals Saved Above Expected)** — Measures goalie value vs. an average netminder given identical shot quality
- **Expected Goals (xG) Model** — Evaluates each shot's danger using distance, angle, shot type, rebounds, rush situation, and screen/traffic
- **High-Danger Save %** — Separate HD/MD/LD zone save percentages (slot area, mid-range, perimeter)
- **Rebound Control Rate** — Tracks controlled vs. uncontrolled rebounds and average rebound danger score
- **Odd-Man Rush Save %** — Dedicated metrics for breakaways, 2-on-1, and 3-on-2 situations
- **Game-State Splits** — All metrics broken down by even strength, power play, penalty kill, score effects
- **Consistency Index** — Standard deviation of per-game SV% converted to a 0-100 stability score with hot/cold streak tracking
- **Development Trajectory** — Age-curve modelling projecting future performance windows with peak age prediction

### Generative AI-Powered Scouting

- **Multi-Model AI Integration:**
  - OpenAI GPT-4 for premium, high-accuracy analysis
  - Anthropic Claude for cost-effective AI alternatives
  - Ollama local LLM for zero API cost, offline capability
- AI prompts now include advanced metrics (GSAx, HD SV%, Black Ops Score) for richer, context-aware reports

### 🗃️ Database Backend (SQLite → PostgreSQL Ready)

- Full SQLAlchemy ORM with models for Goalies, Seasons, Game Logs, Advanced Metrics, Injuries, Scouting Reports, and NHL Comparisons
- SQLite by default for zero-configuration local setup
- Swap to PostgreSQL by setting `DATABASE_URL` — no code changes required
- JSON migration utility to import existing goalie data with one command

### Fully Automated Scouting Ecosystem

- End-to-end automation of scouting workflows
- AI-generated scouting reports enhanced with advanced analytics context
- JSON-based database (backward compatible) and new SQLite backend
- Web scraping capabilities from multiple sources

### Automated Content Creation

- AI-driven scouting reports in Markdown and HTML
- Blog post spotlight generator
- Twitter (X) integration for automated posts

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Advanced Analytics](#advanced-analytics)
- [Black Ops Score Methodology](#black-ops-score-methodology)
- [Data Specifications](#data-specifications)
- [Sample Outputs](#sample-outputs)
- [API Reference](#api-reference)
- [Contributing](#contributing)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/UtahNetScout/GoalieScout.git
cd GoalieScout

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## ⚡ Quick Start

```bash
# Initialize database
goaliescout init

# Add a goalie
goaliescout add-goalie

# Analyze with AI
goaliescout analyze john_doe --ai-model openai

# View advanced analytics
goaliescout advanced-stats john_doe

# Get the Black Ops Score
goaliescout black-ops-score john_doe

# Compare two goalies
goaliescout compare john_doe jane_smith

# Generate report
goaliescout generate-report john_doe --format markdown

# View rankings
goaliescout rank --metric save_percentage
```

## ⚙️ Configuration

Configure the platform by editing `.env`:

```bash
# AI Configuration
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Database (optional — defaults to SQLite)
DATABASE_URL=sqlite:///./data/goaliescout.db
# For PostgreSQL: DATABASE_URL=postgresql+psycopg2://user:pass@localhost/goaliescout

# Twitter Configuration
TWITTER_API_KEY=your_key_here
# ... (see .env.example for full configuration)
```

## 📖 Usage Guide

### CLI Commands

**Standard commands:**
- `goaliescout init` — Initialize database
- `goaliescout add-goalie` — Add new goalie
- `goaliescout list-goalies` — List all goalies
- `goaliescout analyze PLAYER_ID` — AI analysis
- `goaliescout generate-report PLAYER_ID` — Generate report
- `goaliescout rank` — Rank goalies by metric
- `goaliescout create-blog PLAYER_ID` — Create blog post
- `goaliescout tweet PLAYER_ID` — Create tweet
- `goaliescout stats` — Database statistics

**Advanced analytics commands:**
- `goaliescout advanced-stats PLAYER_ID` — Show all advanced metrics
- `goaliescout black-ops-score PLAYER_ID` — Show Black Ops Score with full breakdown
- `goaliescout compare PLAYER_ID_1 PLAYER_ID_2` — Side-by-side advanced comparison

### Python API

```python
from goaliescout.data import GoalieDatabase, GoalieProfile, Demographics
from goaliescout.ai import get_ai_service
from goaliescout.analytics import (
    calculate_black_ops_score,
    calculate_gsax,
    calculate_zone_save_pct,
    calculate_consistency,
)

# Initialize database
db = GoalieDatabase()

# Create and store a goalie profile
demographics = Demographics(
    name="John Doe",
    country="USA",
    date_of_birth="2004-05-20"
)
profile = GoalieProfile(
    player_id="john_doe",
    demographics=demographics,
    league="NCAA"
)
db.add_goalie(profile)

# Calculate advanced metrics from shot-level data
shots = [
    {"distance": 18.0, "angle": 5.0, "shot_type": "wrist", "goal": False},
    {"distance": 12.0, "angle": 0.0, "shot_type": "tip", "is_rebound": True, "goal": True},
]
gsax = calculate_gsax(shots, actual_goals_against=1)
zone_sv = calculate_zone_save_pct(shots)

# Calculate the Black Ops Score
bos = calculate_black_ops_score(
    gsax_per_game=gsax["gsax"],
    hd_sv_pct=zone_sv["hd_sv_pct"],
    games_played=50,
)
print(f"Black Ops Score: {bos['black_ops_score']} — {bos['tier']}")

# AI analysis enriched with advanced metrics
ai_service = get_ai_service('openai')
profile_dict = profile.to_dict()
profile_dict['advanced_metrics'] = {
    'black_ops_score': bos['black_ops_score'],
    'gsax': gsax['gsax'],
    'hd_sv_pct': zone_sv['hd_sv_pct'],
}
analysis = ai_service.analyze_goalie(profile_dict)
```

### SQLite Database

```python
from goaliescout.database import create_schema, get_session, create_goalie, add_season

# Initialize schema
create_schema()

# Create a goalie record
with get_session() as session:
    goalie = create_goalie({"name": "John Doe", "country": "USA"}, session=session)
    add_season(goalie.id, {"year": "2023-24", "games": 40, "sv_pct": 0.915}, session=session)

# Migrate existing JSON data
from goaliescout.database.import_json import import_json_database
summary = import_json_database("./data/goalie_database.json")
print(summary)  # {"imported": N, "skipped": 0, "errors": 0}
```

## 📊 Advanced Analytics

### GSAx (Goals Saved Above Expected)

GSAx measures how many goals a goalie saved *above* what an average goalie would be expected to save given the same shots. Positive GSAx = outperformed expectations.

```
GSAx = xGA (expected goals against) - Actual GA
```

### Expected Goals (xG) Model

The xG model evaluates each shot based on:
- **Distance** from net (exponential decay)
- **Angle** (cosine decay from slot centre-line)
- **Shot type** (tip/deflection highest; slap shot lowest)
- **Situation** (rebound ×1.85, rush ×1.50, power play ×1.20, screen ×1.25)

### Zone Save Percentages

| Zone | Definition |
|------|-----------|
| **High-Danger (HD)** | ≤ 30 ft *and* ≤ 35° from centre |
| **Medium-Danger (MD)** | ≤ 50 ft *or* ≤ 55° — but not HD |
| **Low-Danger (LD)** | All other shots |

### Consistency Index

Converts the standard deviation of per-game SV% into a 0-100 stability score using exponential decay:

```
Consistency = 100 × e^(−40 × σ)
```

A std dev of 0 = 100/100 (perfectly consistent); 5 percentage-point swings game-to-game ≈ 0/100.

## 🎯 Black Ops Score Methodology

The Black Ops Score is a normalised, weighted composite of seven advanced dimensions:

| Component | Weight | Normalisation Range |
|-----------|--------|-------------------|
| GSAx per game | 25% | −0.5 to +0.5 |
| High-Danger SV% | 20% | .820 to .960 |
| Rebound Control Rate | 15% | 40% to 90% |
| Consistency Index | 15% | 0 to 100 |
| Movement Efficiency | 10% | 0 to 100 |
| Puck Handling | 10% | 0 to 100 |
| Development Trajectory | 5% | 0 to 100 |

Missing data is imputed at the neutral value of 50 (unknown). A confidence interval (±95%) is computed based on sample size — wider with fewer games played.

## 📊 Data Specifications

### Supported Leagues

- NHL, AHL, NCAA, CHL (OHL/WHL/QMJHL)
- USHL, KHL, SHL, Liiga
- High School, Semi-Professional

### Data Structure

See `data/sample_database.json` for complete profile examples with:
- Demographics (name, country, DOB, height, weight)
- Performance metrics (games, wins, save %, GAA)
- Injury history
- NHL comparisons
- AI analysis and ratings

## 📸 Sample Outputs

Example reports and content available in:
- `data/sample_database.json` — Sample goalie profiles
- `reports/` — Generated scouting reports
- `content/blog/` — Blog post examples

## 🔧 API Reference

### Core Modules

- `goaliescout.data` — JSON database and data models
- `goaliescout.database` — SQLAlchemy ORM, SQLite/PostgreSQL backend
- `goaliescout.ai` — AI service integrations (OpenAI, Anthropic, Ollama)
- `goaliescout.analytics` — Full advanced analytics suite
  - `goaliescout.analytics.gsax` — Goals Saved Above Expected
  - `goaliescout.analytics.shot_quality` — xG model
  - `goaliescout.analytics.slot_save_pct` — HD/MD/LD save percentages
  - `goaliescout.analytics.rebound_control` — Rebound control rate
  - `goaliescout.analytics.rush_defense` — Odd-man rush save %
  - `goaliescout.analytics.game_state` — Game-state splits
  - `goaliescout.analytics.consistency` — Performance volatility index
  - `goaliescout.analytics.age_curves` — Development trajectory prediction
  - `goaliescout.analytics.movement_analysis` — Lateral movement efficiency
  - `goaliescout.analytics.composite_score` — Black Ops Score
- `goaliescout.scraping` — Web scraping
- `goaliescout.content` — Report and content generation
- `goaliescout.cli` — Command-line interface

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Coding standards
- Testing guidelines
- Pull request process

## 📝 License

Open source - MIT License

## 🙏 Acknowledgments

- OpenAI GPT-4 API
- Anthropic Claude API
- Ollama local LLM
- Hockey analytics community

---

**Note:** Always verify AI-generated insights through official sources.

*Built with ❤️ for the hockey community*
