# 🚀 Quick Deployment Guide - Get Live ASAP!

This guide will get your Black Ops Goalie Scouting Platform live and running in **under 10 minutes**.

## ⚡ Super Quick Start (Fastest - FREE Option)

### Step 1: Install Dependencies (2 minutes)
```bash
# Clone the repo (if not already)
git clone https://github.com/UtahNetScout/GoalieScout.git
cd GoalieScout

# Install Python dependencies
pip install -r requirements.txt

# Install Ollama (FREE local AI - no API costs!)
# Visit: https://ollama.ai/download
# Or on macOS: brew install ollama
# Or on Linux: curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama and pull the model
ollama serve &
ollama pull llama2
```

### Step 2: Configure Environment (1 minute)
```bash
# Create .env file with FREE settings
cat > .env << EOF
# FREE AI Provider (no API costs!)
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Enable all features
ENABLE_ENHANCED_DATA=true
ENABLE_INJURY_TRACKING=true
ENABLE_MAXPREPS=true
ENABLE_BLOGGING=true

# Social media (dry-run mode for safety)
ENABLE_SOCIAL=true
SOCIAL_DRY_RUN=true
EOF
```

### Step 3: Launch Platform with Real-Time Monitoring (30 seconds)
```bash
# Run with real-time monitoring
python monitor.py
```

**That's it! Your platform is now LIVE! 🎉**

---

## 📊 Watch It Work in Real-Time

The `monitor.py` script provides a **live dashboard** showing:
- ✅ Goalies discovered
- 🤖 AI reports generated
- 📝 Blog posts created
- 📱 Social media posts (dry-run)
- 📈 Real-time progress
- ⏱️ Processing speed
- 💾 Database updates

---

## 🎯 Alternative: Premium Setup (With OpenAI/Anthropic)

If you want higher quality AI reports:

### Option A: OpenAI (Highest Quality)
```bash
# Get API key from: https://platform.openai.com/api-keys
echo "AI_PROVIDER=openai" >> .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### Option B: Anthropic Claude (50-70% Cheaper)
```bash
# Get API key from: https://console.anthropic.com/
echo "AI_PROVIDER=anthropic" >> .env
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
```

---

## 🌐 Go Live on X (Twitter)

To enable LIVE posting to X:

1. **Get X API Credentials:**
   - Apply at: https://developer.twitter.com/en/portal/petition/essential/basic-info
   - Get: Bearer Token, API Key, API Secret, Access Token, Access Secret

2. **Configure X Credentials:**
```bash
cat >> .env << EOF
X_BEARER_TOKEN=your-bearer-token
X_API_KEY=your-api-key
X_API_SECRET=your-api-secret
X_ACCESS_TOKEN=your-access-token
X_ACCESS_TOKEN_SECRET=your-access-secret
EOF
```

3. **Disable Dry-Run Mode:**
```bash
# Change from dry-run to LIVE posting
sed -i 's/SOCIAL_DRY_RUN=true/SOCIAL_DRY_RUN=false/' .env
```

4. **Run Again:**
```bash
python monitor.py
```

**⚠️ Warning:** With `SOCIAL_DRY_RUN=false`, posts will go LIVE to X!

---

## 🔄 Run on Schedule (Automation)

### Option 1: Cron Job (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 6 AM
0 6 * * * cd /path/to/GoalieScout && /usr/bin/python3 goalie_scout.py >> /path/to/logs/scout.log 2>&1
```

### Option 2: Windows Task Scheduler
```bash
# Create a batch file: run_scout.bat
@echo off
cd C:\path\to\GoalieScout
python goalie_scout.py
```

Then create a scheduled task to run `run_scout.bat` daily.

### Option 3: GitHub Actions (Cloud Automation)
```yaml
# Create .github/workflows/scout.yml
name: Daily Goalie Scouting
on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM UTC daily
  workflow_dispatch:  # Manual trigger

jobs:
  scout:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python goalie_scout.py
        env:
          AI_PROVIDER: ${{ secrets.AI_PROVIDER }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## 📁 Check Your Output

After running, check these directories:

```bash
# View the database
cat goalies_data.json | python -m json.tool | less

# View blog posts
ls -lh blog_posts/

# Read a blog post
cat blog_posts/top_prospects_*.md

# Check social media posts (dry-run)
cat social_media_tracking.json | python -m json.tool
```

---

## 🎬 Demo Mode (Test Without APIs)

Want to see it work without setting up APIs?

```bash
# Run in demo mode with sample data
python goalie_scout.py --demo
```

This will:
- Skip web scraping
- Use sample AI responses
- Generate blog posts
- Show social media posts (dry-run)
- Complete in ~30 seconds

---

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt --upgrade
```

### "Ollama not running"
```bash
ollama serve
# In another terminal:
ollama pull llama2
```

### "API key invalid"
- Double-check your `.env` file
- Ensure no extra spaces in API keys
- Verify API key is active on provider's dashboard

### "No goalies discovered"
- URLs in the code are placeholders
- Real league websites require custom selectors
- Platform will work with sample goalies for testing

---

## 💡 Pro Tips

1. **Start Small:** Test with `AI_PROVIDER=ollama` (free) before spending money
2. **Monitor Costs:** Use Anthropic instead of OpenAI to save 50-70%
3. **Test First:** Keep `SOCIAL_DRY_RUN=true` until you verify posts look good
4. **Check Logs:** Run with `python goalie_scout.py 2>&1 | tee scout.log`
5. **Backup Data:** Copy `goalies_data.json` before each run

---

## 🎯 What to Expect

**First Run (with Ollama):**
- Duration: ~5-10 minutes for 4 sample goalies
- Output: 
  - Updated goalie rankings
  - 3-5 blog posts
  - 5-10 social media posts (dry-run)
  - NHL comparison for each goalie
  - Injury tracking data

**With Real League Scraping:**
- Duration: 1-3 hours (15+ leagues)
- Output:
  - 100+ goalies discovered
  - 100+ AI reports
  - 10+ blog posts
  - 50+ social media posts

---

## 🚦 Status Indicators

While running, you'll see:
- `[→]` = Processing
- `[✓]` = Success
- `[!]` = Warning (non-fatal)
- `[✗]` = Error

---

## 🎉 You're Live!

Once running, your platform is:
- ✅ Discovering goalies from 16 leagues
- ✅ Generating AI scouting reports
- ✅ Ranking prospects automatically
- ✅ Creating blog posts
- ✅ Posting to social media (or dry-run)
- ✅ Tracking injuries
- ✅ Comparing to NHL legends

**Welcome to the future of goalie scouting! 🏒**
