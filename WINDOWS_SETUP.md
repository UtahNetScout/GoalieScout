# Windows Setup Guide - Super Simple!

**No technical knowledge needed. Just follow these steps:**

---

## Step 1: Install Python (10 minutes)

1. Go to: **https://python.org/downloads**
2. Click the big **yellow "Download Python"** button
3. Run the installer you just downloaded
4. **⚠️ IMPORTANT:** Check the box that says **"Add Python to PATH"** at the bottom
5. Click **"Install Now"**
6. Wait for installation to complete
7. Click **"Close"**

✅ **Done!** Python is installed.

---

## Step 2: Download This Project (2 minutes)

1. Use this direct link to download: 
   **https://github.com/UtahNetScout/GoalieScout/archive/refs/heads/copilot/check-past-projects.zip**
2. The file will download to your Downloads folder
3. **Right-click** the ZIP file → **"Extract All"**
4. Click **"Extract"**
5. **Move the extracted folder** to your Desktop for easy access

✅ **Done!** Project is ready.

---

## Step 3: Install Ollama - FREE AI (10 minutes)

1. Go to: **https://ollama.ai/download**
2. Click **"Download for Windows"**
3. Run the installer
4. After installation, **press Windows key**
5. Type: **`cmd`**
6. Press **Enter** (a black window opens)
7. Type: **`ollama pull llama2`**
8. Press **Enter**
9. Wait for download to complete (about 4GB)

✅ **Done!** FREE AI is ready.

---

## Step 4: Start the Platform (1 minute)

1. Open the project folder on your Desktop
2. Find the file called **`START.bat`**
3. **Double-click it**
4. Choose **option 1** when asked
5. **Press Enter**

🎉 **That's it!** You'll see a colorful live dashboard showing:
- Goalies being discovered
- AI reports being generated
- Your database growing in real-time

---

## What You'll See

A live dashboard that looks like this:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BLACK OPS GOALIE SCOUTING PLATFORM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Statistics:
   Total Goalies: 4
   AI Reports: 4
   Blog Posts: 0
   Social Posts: 0

⚙️ Configuration:
   AI Provider: ollama ✓
   Blogging: disabled
   Social Media: disabled

📈 Processing: 1.2 goalies/minute
⏱️ Running for: 2 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Results Are Saved

All scouting data is saved in: **`goalies_data.json`**

You can open this file with Notepad to see all the goalies and their AI scouting reports!

---

## To Stop

Press **Ctrl + C** in the black window

---

## Troubleshooting

### "Python is not recognized"
- You forgot to check "Add Python to PATH" during installation
- **Fix:** Uninstall Python, reinstall it, and CHECK the PATH box this time

### "pip is not recognized"
- Python wasn't installed correctly
- **Fix:** Reinstall Python and make sure to check "Add Python to PATH"

### "ollama is not recognized"
- Ollama didn't install correctly
- **Fix:** Reinstall Ollama from https://ollama.ai/download

### The window closes immediately
- **Fix:** Right-click START.bat → "Edit" → Make sure the file looks correct
- Or just open Command Prompt manually and type: `python monitor.py`

---

## Need Help?

Check **BEGINNER_GUIDE.md** for more detailed instructions!

---

## What's Next?

Once you have goalie data:
- Edit `.env` file to enable blogging: `ENABLE_BLOGGING=true`
- Edit `.env` file to enable social media: `ENABLE_SOCIAL=true`
- Set up your X (Twitter) API keys in `.env`
- Run START.bat again to post to social media!
