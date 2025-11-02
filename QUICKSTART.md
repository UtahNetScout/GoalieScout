# Quick Start Guide - GoalieScout Platform

## 🚀 Getting Started in 3 Steps

### Step 1: Choose Your AI Provider

#### Option A: Ollama (FREE - Recommended to start)
```bash
# Install Ollama from https://ollama.ai/
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2

# Configure
echo "AI_PROVIDER=ollama" >> .env
echo "OLLAMA_MODEL=llama2" >> .env
```

#### Option B: Anthropic Claude (Cost-Effective)
```bash
# Get API key from https://console.anthropic.com/
echo "AI_PROVIDER=anthropic" >> .env
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
```

#### Option C: OpenAI (Premium)
```bash
# Get API key from https://platform.openai.com/
echo "AI_PROVIDER=openai" >> .env
echo "OPENAI_API_KEY=your-key-here" >> .env
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Platform
```bash
python goalie_scout.py
```

## 📊 What Happens When You Run It?

1. **Scraping**: Collects new goalie data from league websites
2. **AI Analysis**: Generates professional scouting reports for each goalie
3. **Ranking**: Automatically ranks all goalies by AI score
4. **Blogging**: Creates blog posts about top prospects, sleepers, and leagues
5. **Social Media**: Posts updates to X (Twitter) - in dry-run mode by default
6. **Database**: Saves everything to `goalies_data.json`

## 🎯 Output Files

```
GoalieScout/
├── goalies_data.json          # Main database
├── blog_posts/                # Generated blog posts
│   ├── YYYYMMDD_Top_Prospects.md
│   ├── YYYYMMDD_Rising_Stars.md
│   └── YYYYMMDD_League_Spotlight.md
└── last_social_post.json      # Social media tracking
```

## ⚙️ Configuration Options

### Disable Blogging
```bash
echo "ENABLE_BLOGGING=false" >> .env
```

### Disable Social Media
```bash
echo "ENABLE_SOCIAL=false" >> .env
```

### Enable Live X Posting (after testing)
```bash
# First, set up X API credentials in .env
echo "SOCIAL_DRY_RUN=false" >> .env
```

## 🤖 AI Provider Costs

| Provider | Monthly Cost (100 reports) | Setup Time |
|----------|---------------------------|------------|
| Ollama | **$0** | 10 minutes |
| Anthropic | ~$5-10 | 5 minutes |
| OpenAI GPT-4 | ~$20-30 | 5 minutes |

## 📱 X (Twitter) Setup

1. Apply for API access: https://developer.twitter.com/
2. Create an app and get credentials
3. Add to `.env`:
```bash
X_BEARER_TOKEN=your-bearer-token
```

4. Test with dry run first:
```bash
python goalie_scout.py
# Check console output for what would be posted
```

5. Go live when ready:
```bash
echo "SOCIAL_DRY_RUN=false" >> .env
```

## 🔄 Automation Tips

### Run Daily with Cron (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 8 AM
0 8 * * * cd /path/to/GoalieScout && python goalie_scout.py
```

### Run Daily with Task Scheduler (Windows)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to Daily
4. Set action to run: `python C:\path\to\GoalieScout\goalie_scout.py`

## 🐛 Troubleshooting

### "AI provider not available"
- Check your API key is set in `.env`
- For Ollama, make sure it's running: `ollama serve`

### "X API error"
- Verify your Bearer Token is correct
- Check you're not rate-limited
- Try dry-run mode first: `SOCIAL_DRY_RUN=true`

### Web scraping errors
- Most league URLs in the code are placeholders
- Update them with real league roster pages
- Customize CSS selectors for each site

## 📈 Next Steps

1. **Customize Prompts**: Edit `ai_providers.py` to change scouting report style
2. **Add More Leagues**: Update `LEAGUES` dict in `goalie_scout.py`
3. **Customize Blog Posts**: Modify templates in `blog_generator.py`
4. **Schedule Automation**: Set up cron/Task Scheduler
5. **Monitor & Refine**: Check outputs and adjust as needed

## 💡 Pro Tips

- Start with Ollama (free) to test everything
- Use dry-run mode for social media until you're confident
- Run manually a few times before automating
- Check blog posts in `blog_posts/` folder
- The platform skips goalies that already have reports (saves API costs)

## 🆘 Need Help?

Check the main README.md for detailed documentation or open an issue on GitHub!
