# 🏒 BEGINNER'S GUIDE - GoalieScout Platform Setup

**Complete step-by-step guide for non-technical users**

---

## 📋 What You'll Need

1. **A Windows, Mac, or Linux computer** (desktop or laptop)
2. **30 minutes of your time**
3. **Internet connection**
4. **That's it!** No coding experience needed

---

## 🎯 Step 1: Install Python (10 minutes)

Python is the language this platform runs on. It's free and easy to install.

### For Windows:
1. Go to: https://www.python.org/downloads/
2. Click the big yellow button "Download Python 3.12.x"
3. **IMPORTANT**: When installer opens, CHECK the box "Add Python to PATH"
4. Click "Install Now"
5. Wait for installation to complete
6. Click "Close"

### For Mac:
1. Go to: https://www.python.org/downloads/
2. Click "Download Python 3.12.x"
3. Open the downloaded file
4. Follow the installer prompts
5. Click "Install"

### Verify Python is installed:
1. **Windows**: Press `Windows Key + R`, type `cmd`, press Enter
2. **Mac**: Press `Command + Space`, type `terminal`, press Enter
3. Type: `python --version` and press Enter
4. You should see something like "Python 3.12.1"

✅ **Success!** Python is installed.

---

## 🎯 Step 2: Download This Project (5 minutes)

### Option A: Download ZIP (Easier)
1. Go to: https://github.com/UtahNetScout/GoalieScout
2. Click the green "Code" button
3. Click "Download ZIP"
4. Save the file to your Desktop
5. Right-click the ZIP file → "Extract All"
6. Extract to Desktop → You'll see a folder called "GoalieScout-main"

### Option B: Use Git (If you have it)
1. Open Terminal/Command Prompt
2. Type: `cd Desktop`
3. Type: `git clone https://github.com/UtahNetScout/GoalieScout.git`

✅ **Success!** You have the project files.

---

## 🎯 Step 3: Install Required Software (5 minutes)

### Open Terminal in Project Folder:

**Windows:**
1. Open the "GoalieScout-main" folder on your Desktop
2. Hold `Shift` + Right-click in the folder (not on a file)
3. Click "Open PowerShell window here" or "Open Command window here"

**Mac:**
1. Open the "GoalieScout-main" folder on your Desktop
2. Right-click the folder
3. Services → "New Terminal at Folder"

### Install Dependencies:
In the terminal window that opened, type:
```bash
pip install -r requirements.txt
```
Press Enter and wait (1-2 minutes). You'll see lots of text scroll by.

✅ **Success!** Required software is installed.

---

## 🎯 Step 4: Get FREE AI (Ollama) - No API Keys Needed! (10 minutes)

### Download Ollama:
1. Go to: https://ollama.ai/download
2. Click download for your operating system (Windows/Mac/Linux)
3. Install it like any other program

### Start Ollama:
**Windows:**
1. Click Start Menu
2. Type "cmd" and press Enter
3. Type: `ollama serve`
4. Leave this window open (minimize it)

**Mac:**
1. Ollama runs automatically after installation
2. You'll see it in your menu bar (top right)

### Download AI Model:
Open a NEW terminal/command window:
1. Type: `ollama pull llama2`
2. Wait 2-3 minutes (downloads AI model)

✅ **Success!** You have FREE AI ready to use.

---

## 🎯 Step 5: Configure the Platform (2 minutes)

### Create Configuration File:

**Windows - PowerShell:**
In your GoalieScout folder terminal, copy and paste this (all at once):
```powershell
@"
AI_PROVIDER=ollama
ENABLE_BLOGGING=false
ENABLE_SOCIAL=false
SOCIAL_DRY_RUN=true
ENABLE_ENHANCED_DATA=true
ENABLE_INJURY_TRACKING=true
ENABLE_MAXPREPS=true
"@ | Out-File -FilePath .env -Encoding ASCII
```

**Windows - Command Prompt or Mac/Linux:**
Copy and paste this (all at once):
```bash
cat > .env << 'EOF'
AI_PROVIDER=ollama
ENABLE_BLOGGING=false
ENABLE_SOCIAL=false
SOCIAL_DRY_RUN=true
ENABLE_ENHANCED_DATA=true
ENABLE_INJURY_TRACKING=true
ENABLE_MAXPREPS=true
EOF
```

✅ **Success!** Platform is configured (blogging/social media OFF for now).

---

## 🎯 Step 6: START THE PLATFORM! (Right Now!)

### Launch the Platform:
In your terminal, type:
```bash
python monitor.py
```

Press Enter.

### 🎉 What You'll See:
A colorful dashboard will appear showing:
- ✅ Goalies being discovered
- 🤖 AI reports being generated
- 📊 Real-time statistics
- 📈 Processing speed
- 🎯 Recent activity

**Let it run!** Watch it work in real-time.

### To Stop:
Press `Ctrl + C` (hold Control and press C)

✅ **Success!** Your platform is LIVE and working!

---

## 📂 Where Are My Results?

After running the platform, you'll find:

### Your Goalie Database:
- **File**: `goalies_data.json`
- **Location**: Same folder as the project
- **What it contains**: All scouted goalies with AI reports, rankings, stats, NHL comparisons

### Open it:
1. Right-click `goalies_data.json`
2. Open with Notepad (Windows) or TextEdit (Mac)
3. You'll see all your goalie data!

---

## 🔧 Common Issues & Solutions

### "Python not found"
- **Solution**: Make sure you checked "Add Python to PATH" during installation
- **Fix**: Reinstall Python and check that box

### "pip not found"
- **Solution**: Type `python -m pip install -r requirements.txt` instead

### "Ollama not found"
- **Solution**: Make sure Ollama is running (`ollama serve` on Windows)
- **Mac**: Should run automatically

### Platform runs but no goalies appear
- **Solution**: The URLs in the code are placeholders. You'll need to update them with real league roster pages later. For now, it works with sample data.

---

## 🚀 Next Steps (When You're Ready)

### 1. Set Up Social Media Accounts (Later)
When ready, create accounts for:
- X (Twitter)
- Instagram
- Facebook

Then update your `.env` file to enable posting.

### 2. Set Up Blogging (Later)
When ready, enable blogging:
- Edit `.env` file
- Change `ENABLE_BLOGGING=false` to `ENABLE_BLOGGING=true`
- Blog posts will appear in `blog_posts/` folder

### 3. Run Automatically (Later)
Set it to run automatically:
- **Windows**: Use Task Scheduler
- **Mac**: Use cron or Automator
- **Cloud**: Deploy to AWS, DigitalOcean, etc.

See `DEPLOYMENT.md` for detailed instructions.

---

## 📞 Need Help?

If you get stuck:
1. Check the "Common Issues" section above
2. Read `DEPLOYMENT.md` for more details
3. Open an issue on GitHub
4. Ask in the discussions

---

## 🎊 Congratulations!

You've successfully deployed the GoalieScout platform! 

You now have:
✅ AI-powered goalie scouting
✅ 16 leagues being monitored
✅ Automatic rankings
✅ NHL comparisons
✅ Injury tracking
✅ High school prospects
✅ Real-time monitoring

**Your database is growing with every run!** 🏒
