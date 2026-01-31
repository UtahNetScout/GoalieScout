# Quick Start Guide

This guide will help you get started with the Black Ops Goalie Scouting Platform in 5 minutes.

## Step 1: Installation (2 minutes)

```bash
# Clone the repository
git clone https://github.com/UtahNetScout/GoalieScout.git
cd GoalieScout

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## Step 2: Basic Setup (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Initialize database
goaliescout init
```

## Step 3: Add Your First Goalie (1 minute)

```bash
# Add a goalie interactively
goaliescout add-goalie
```

Or add programmatically:

```python
from goaliescout.data import GoalieDatabase, GoalieProfile, Demographics

db = GoalieDatabase()

demographics = Demographics(
    name="Your Goalie",
    country="USA",
    date_of_birth="2004-01-15"
)

profile = GoalieProfile(
    player_id="your_goalie",
    demographics=demographics,
    league="NCAA"
)

db.add_goalie(profile)
```

## Step 4: View and Analyze (1 minute)

```bash
# List all goalies
goaliescout list-goalies

# View statistics
goaliescout stats

# Rank goalies
goaliescout rank --metric save_percentage

# Generate a report (without AI)
goaliescout generate-report your_goalie --format markdown
```

## Step 5: Set Up AI (Optional)

To use AI-powered analysis:

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
3. Analyze:
   ```bash
   goaliescout analyze your_goalie --ai-model openai
   ```

## Common Commands

```bash
# Help
goaliescout --help

# List goalies
goaliescout list-goalies

# Filter by league
goaliescout list-goalies --league NCAA

# Generate report
goaliescout generate-report PLAYER_ID --format markdown

# Create blog post
goaliescout create-blog PLAYER_ID

# Create tweet
goaliescout tweet PLAYER_ID

# Rank goalies
goaliescout rank --metric save_percentage
```

## Example Workflow

```bash
# 1. Initialize
goaliescout init

# 2. Add goalie
goaliescout add-goalie --name "John Doe" --country "Canada" --dob "2003-05-15" --league "OHL"

# 3. View in database
goaliescout list-goalies

# 4. Generate report
goaliescout generate-report john_doe --format markdown

# 5. Create blog post
goaliescout create-blog john_doe

# 6. View rankings
goaliescout rank --metric save_percentage
```

## Using Python API

```python
from goaliescout.data import GoalieDatabase, GoalieProfile, Demographics
from goaliescout.analytics import GoalieAnalytics
from goaliescout.content import ReportGenerator

# Initialize
db = GoalieDatabase()

# Create profile
demographics = Demographics(name="Test", country="USA", date_of_birth="2004-01-01")
profile = GoalieProfile(player_id="test", demographics=demographics, league="NCAA")

# Add to database
db.add_goalie(profile)

# Analyze
stats = GoalieAnalytics.calculate_career_stats(profile)

# Generate report
report_gen = ReportGenerator()
report = report_gen.generate_markdown_report(profile.to_dict(), "Analysis...")
```

## Run Examples

```bash
# Run the example script
python example_usage.py

# Run tests
python run_tests.py
```

## Next Steps

1. Read the full [README.md](README.md)
2. Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
3. Set up AI API keys for full functionality
4. Explore the data models in `src/goaliescout/data/models.py`

## Need Help?

- Check the [README.md](README.md) for detailed documentation
- View available commands: `goaliescout --help`
- Run example: `python example_usage.py`
- Run tests: `python run_tests.py`

## Tips

- Use `--help` with any command for more details
- The platform works without API keys (uses fallback analysis)
- Add API keys in `.env` for AI-powered features
- All data is stored in JSON format in `./data/`
- Reports are saved to `./reports/`
- Blog posts are saved to `./content/blog/`

Enjoy scouting! 🏒🥅
