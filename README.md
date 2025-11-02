# GoalieScout
Hockey Goalie Scouting and Ranking System 

## 🏒 Black Ops Goalie Scouting Platform

An all-in-one **100% AI-automated** goalie scouting platform featuring web scraping, AI-powered scouting reports, automatic rankings, blogging, and social media posting across 20+ international hockey leagues.

## ✨ Features

### Core Features
- **50+ Pre-populated Goalies** across 20 leagues worldwide
- **Automatic Web Scraping** from multiple hockey league websites
- **Multiple AI Provider Options**:
  - OpenAI GPT-4 (premium quality)
  - Anthropic Claude (cost-effective alternative)
  - Ollama (FREE local LLM - no API costs!)
- **Automatic Rankings** based on AI-generated scores
- **JSON Database** for easy data management and export

### NEW: 100% Automation Features 🤖
- **Automated Blogging**: Generates professional blog posts about prospects
  - Top Prospects posts
  - League Spotlight articles
  - Rising Stars / Sleeper prospects
  - Markdown and HTML formats
- **X (Twitter) Integration**: Automated social media posting
  - Daily prospect updates
  - Weekly summaries
  - Individual prospect spotlights
  - Dry-run mode for testing
- **Multi-league Coverage**: USHL, NCAA D1, CHL/OHL, SHL, DEL, Liiga, Czech Extraliga, KHL, EIHL, and more

## 📋 Prerequisites

- Python 3.8 or higher
- **AI Provider** (choose one):
  - OpenAI API key (premium option)
  - Anthropic API key (cost-effective)
  - Ollama installed locally (FREE!)
- Optional: X (Twitter) API access for social media posting

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/UtahNetScout/GoalieScout.git
cd GoalieScout
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your AI provider (copy and edit `.env.example`):
```bash
cp .env.example .env
# Edit .env with your preferred configuration
```

### AI Provider Setup

#### Option 1: OpenAI (Premium)
```bash
export OPENAI_API_KEY="your-api-key-here"
export AI_PROVIDER="openai"
```

#### Option 2: Anthropic Claude (Cost-Effective)
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
export AI_PROVIDER="anthropic"
```

#### Option 3: Ollama (FREE & Local!)
```bash
# Install Ollama from https://ollama.ai/
# Pull a model: ollama pull llama2
export AI_PROVIDER="ollama"
export OLLAMA_MODEL="llama2"
```

## 💻 Usage

Run the fully automated platform:

```bash
python goalie_scout.py
```

The script will:
1. Load existing goalie database (or create one with sample data)
2. Scrape all configured league websites for new goalies
3. Generate AI-powered scouting reports for each goalie
4. Rank goalies based on AI scores
5. **Generate blog posts** about top prospects, sleepers, and league spotlights
6. **Post updates to X (Twitter)** with daily summaries
7. Save everything to `goalies_data.json`

## 📊 Data Structure

Each goalie entry contains:
- **name**: Player name
- **country**: Country of origin
- **league**: Current league
- **team**: Current team
- **dob**: Date of birth
- **height**: Height in cm
- **weight**: Weight in kg
- **status**: Active/Inactive
- **ai_score**: AI-generated score (0-100)
- **tier**: Top Prospect / Sleeper / Watch / Red Flag
- **rank**: Overall ranking
- **notes**: AI-generated scouting report
- **video_links**: Links to highlight videos

## ⚙️ Configuration

### Environment Variables

```bash
# AI Provider (openai, anthropic, or ollama)
AI_PROVIDER=ollama

# Blogging (true/false)
ENABLE_BLOGGING=true

# Social Media (true/false)
ENABLE_SOCIAL=true
SOCIAL_DRY_RUN=true  # Set to false for live posting

# X (Twitter) API
X_BEARER_TOKEN=your-token-here
```

### Adding New Leagues

Edit the `LEAGUES` dictionary in `goalie_scout.py`:

```python
LEAGUES = {
    "Your League": "https://league-website.com/roster",
    # Add more leagues here
}
```

### Customizing Scraper Selectors

Each league website has different HTML structure. Update the CSS selectors in the `scrape_league()` function to match the target website's structure.

## 🤖 AI Provider Comparison

| Provider | Cost | Speed | Quality | Setup |
|----------|------|-------|---------|-------|
| **OpenAI GPT-4** | $$$ | Fast | Excellent | Easy - API key |
| **Anthropic Claude** | $$ | Fast | Excellent | Easy - API key |
| **Ollama (Local)** | FREE | Medium | Good | Medium - Install required |

**Recommendation**: Start with Ollama for FREE unlimited usage, upgrade to Anthropic Claude for better quality at lower cost than OpenAI.

## 📝 Blog Output

Blog posts are automatically generated in `blog_posts/` directory:
- `YYYYMMDD_HHMMSS_Top_10_Goalie_Prospects.md`
- `YYYYMMDD_HHMMSS_Rising_Stars_Sleeper_Prospects.md`
- `YYYYMMDD_HHMMSS_[League]_Spotlight.md`

Formats supported: Markdown (.md), HTML (.html), Plain text (.txt)

## 📱 Social Media Automation

The platform can automatically post to X (Twitter):
- **Daily Updates**: Top 3 prospects with scores
- **Weekly Summaries**: Total goalies, top prospects, sleepers
- **Prospect Spotlights**: Individual goalie highlights
- **League Updates**: Coverage statistics

**Dry Run Mode** (default): Posts are printed to console, not actually published. Set `SOCIAL_DRY_RUN=false` when ready to go live.

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables or `.env` files for sensitive data
- The `.gitignore` file is configured to exclude API keys and database files
- X API credentials should be kept secure

## 💡 Pro Tips

1. **Save Money**: Use Ollama for FREE AI reports (runs locally on your machine)
2. **Test First**: Keep `SOCIAL_DRY_RUN=true` until you're ready to post live
3. **Schedule It**: Use cron (Linux/Mac) or Task Scheduler (Windows) to run automatically
4. **Customize Prompts**: Edit prompts in `ai_providers.py` for different report styles

## 📝 License

This project is open source and available for hockey scouting purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## ⚠️ Disclaimer

This tool is for scouting and research purposes. Ensure you comply with:
- Website terms of service when scraping data
- X (Twitter) API terms of service
- AI provider terms of service

