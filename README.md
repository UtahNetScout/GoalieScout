# GoalieScout
Hockey Goalie Scouting and Ranking System 

## 🏒 Black Ops Goalie Scouting Platform

An all-in-one automated goalie scouting platform featuring web scraping, AI-powered scouting reports, and automatic rankings across 20+ international hockey leagues.

## ✨ Features

- **50+ Pre-populated Goalies** across 20 leagues worldwide
- **Automatic Web Scraping** from multiple hockey league websites
- **AI Scouting Reports** powered by OpenAI GPT-4
- **Automatic Rankings** based on AI-generated scores
- **JSON Database** for easy data management and export
- **Multi-league Coverage**: USHL, NCAA D1, CHL/OHL, SHL, DEL, Liiga, Czech Extraliga, KHL, EIHL, and more

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key (for AI scouting reports)

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

3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

## 💻 Usage

Run the goalie scouting platform:

```bash
python goalie_scout.py
```

The script will:
1. Load existing goalie database (or create one with sample data)
2. Scrape all configured league websites for new goalies
3. Generate AI-powered scouting reports for each goalie
4. Rank goalies based on AI scores
5. Save everything to `goalies_data.json`

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

## 🔒 Security Notes

- Never commit your OpenAI API key to version control
- Use environment variables or `.env` files for sensitive data
- The `.gitignore` file is configured to exclude API keys and database files

## 📝 License

This project is open source and available for hockey scouting purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## ⚠️ Disclaimer

This tool is for scouting and research purposes. Ensure you comply with website terms of service when scraping data.
