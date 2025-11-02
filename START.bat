@echo off
REM Black Ops Goalie Scouting Platform - Easy Start Script
REM No technical knowledge required - just double-click this file!

echo ============================================
echo Black Ops Goalie Scouting Platform
echo Easy Setup and Launch
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python first:
    echo 1. Go to: https://python.org/downloads
    echo 2. Download Python
    echo 3. Run installer and CHECK "Add Python to PATH"
    echo 4. After installation, run this file again
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if requirements are installed
if not exist ".setup_complete" (
    echo Installing required packages...
    echo This may take a few minutes...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install requirements
        pause
        exit /b 1
    )
    echo. > .setup_complete
    echo [OK] Requirements installed successfully
    echo.
)

REM Check if .env exists, if not create it
if not exist ".env" (
    echo Creating configuration file...
    echo.
    (
        echo AI_PROVIDER=ollama
        echo ENABLE_BLOGGING=false
        echo ENABLE_SOCIAL=false
        echo ENABLE_ENHANCED_DATA=true
        echo ENABLE_INJURY_TRACKING=true
        echo ENABLE_MAXPREPS=false
    ) > .env
    echo [OK] Configuration created
    echo.
    echo NOTE: Using FREE Ollama AI ^(no costs^)
    echo You'll need to install Ollama separately from: https://ollama.ai/download
    echo Then run: ollama pull llama2
    echo.
)

REM Ask user what they want to do
echo What would you like to do?
echo.
echo 1. Start the platform with live monitoring ^(RECOMMENDED^)
echo 2. Run platform once without monitoring
echo 3. View setup instructions
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting with live monitoring dashboard...
    echo Press Ctrl+C to stop
    echo.
    python monitor.py
) else if "%choice%"=="2" (
    echo.
    echo Running platform once...
    echo.
    python goalie_scout.py
    echo.
    echo Done! Results saved to goalies_data.json
    pause
) else if "%choice%"=="3" (
    echo.
    echo ============================================
    echo Setup Instructions
    echo ============================================
    echo.
    echo 1. Install Ollama for FREE AI:
    echo    - Download from: https://ollama.ai/download
    echo    - Install it
    echo    - Open Command Prompt and run: ollama pull llama2
    echo.
    echo 2. Run this START.bat file again
    echo.
    echo 3. Choose option 1 to start with monitoring
    echo.
    echo 4. Watch the live dashboard as it scouts goalies!
    echo.
    echo Results are saved in goalies_data.json
    echo.
    echo For blogging and social media:
    echo    - Edit the .env file
    echo    - Change ENABLE_BLOGGING=true
    echo    - Change ENABLE_SOCIAL=true
    echo.
    pause
) else (
    echo Exiting...
    exit /b 0
)
