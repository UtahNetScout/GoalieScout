# Black Ops Goalie Scouting Platform

The Black Ops Goalie Scouting Platform is a cutting-edge, AI-driven solution designed to revolutionize the way hockey goalies are scouted, analyzed, and ranked. Leveraging powerful generative AI models, this platform provides unparalleled insights into goalie performance across a wide range of leagues and competition levels.

## ✨ Key Features

### Generative AI-Powered Scouting

- **Multi-Model AI Integration:**
  - OpenAI GPT-4 for premium, high-accuracy data analysis and insights.
  - Anthropic Claude for cost-effective AI model alternatives.
  - Ollama's local LLM models for zero API costs, enabling offline AI capabilities.
- **Core AI-Driven Metrics:**
  - Real-time player ranking dynamically updated using AI-generated data inputs.
  - Automated data enrichment to ensure up-to-date and comprehensive reports.

### Fully Automated Scouting Ecosystem

- **Scouting and Ranking Automation:**
  - End-to-end automation of scouting workflows using advanced AI tools.
  - AI-generated scouting reports and scores based on dynamic data inputs.
  - JSON-based database management for structured and reliable data storage.
  - Web scraping capabilities to gather performance metrics from multiple online sources.
- **Automated Content Creation:**
  - AI-driven blogging templates available in Markdown and HTML formats.
  - Integration with Twitter (X) for automated spotlight posts, enhancing visibility.

### Comprehensive Data Architecture for In-Depth Analytics

- **Scouting Data Attributes:**
  - Captures key parameters such as player demographics (Name, Country, League, Date of Birth) and performance metrics.
  - Ensures daily updates through a robust pipeline with validated database objects.
- **Professional Analytics Suite:**
  - Structured data pipelines for seamless data analysis and visualization.
  - Customizable data outputs for tailored scouting insights.

### Advanced Tracking Features

- **Injury Tracking:**
  - Monitor player health and injury history for risk assessment.
- **NHL Comparisons:**
  - Compare performance metrics to current NHL goalies for benchmarking.
- **International and Multi-Level Scouting:**
  - Coverage of international leagues, semi-professional leagues, NCAA, high schools, and more.

### Real-Time Monitoring

- Provides real-time updates on player performance and rankings.
- Tracks key game statistics as they happen, delivering instant insights for analysts.

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
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
goaliescout analyze player_id --ai-model openai

# Generate report
goaliescout generate-report player_id --format markdown

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

# Twitter Configuration
TWITTER_API_KEY=your_key_here
# ... (see .env.example for full configuration)
```

## 📖 Usage Guide

### CLI Commands

- `goaliescout init` - Initialize database
- `goaliescout add-goalie` - Add new goalie
- `goaliescout list-goalies` - List all goalies
- `goaliescout analyze PLAYER_ID` - Analyze with AI
- `goaliescout generate-report PLAYER_ID` - Generate report
- `goaliescout rank` - Rank goalies
- `goaliescout create-blog PLAYER_ID` - Create blog post
- `goaliescout tweet PLAYER_ID` - Create tweet
- `goaliescout stats` - View database statistics

### Python API

```python
from goaliescout.data import GoalieDatabase, GoalieProfile, Demographics
from goaliescout.ai import get_ai_service

# Initialize database
db = GoalieDatabase()

# Create profile
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

# Add to database
db.add_goalie(profile)

# Analyze with AI
ai_service = get_ai_service('openai')
analysis = ai_service.analyze_goalie(profile.to_dict())
```

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
- `data/sample_database.json` - Sample goalie profiles
- `reports/` - Generated scouting reports
- `content/blog/` - Blog post examples

## 🔧 API Reference

### Core Modules

- `goaliescout.data` - Database and models
- `goaliescout.ai` - AI integrations
- `goaliescout.analytics` - Analytics engine
- `goaliescout.scraping` - Web scraping
- `goaliescout.content` - Report generation
- `goaliescout.cli` - Command-line interface

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
- Hockey scouting community

---

**Note:** Always verify AI-generated insights through official sources.

*Built with ❤️ for the hockey community*
