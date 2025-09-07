@echo off
echo ========================================
echo AI FRAMEWORKS INTEGRATION SYSTEM
echo ========================================
echo.
echo Integrating:
echo   - MemGPT (Memory-enhanced GPT)
echo   - AutoGen (Multi-agent framework)
echo   - CAMEL-AI (Collaborative agents)
echo   - LocalAI (Local model serving)
echo.
echo ========================================

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo [1/4] Checking LocalAI status...
curl -s http://localhost:8080/models >nul 2>&1
if %errorlevel% NEQ 0 (
    echo LocalAI is not running. Starting LocalAI server...
    start "LocalAI Server" cmd /k "setup_localai.bat"
    echo Waiting for LocalAI to start (10 seconds)...
    timeout /t 10 /nobreak >nul
) else (
    echo LocalAI is already running at http://localhost:8080
)

echo.
echo [2/4] Verifying Python packages...
python -c "import memgpt" 2>nul
if %errorlevel% NEQ 0 (
    echo Installing MemGPT...
    pip install memgpt --no-deps --quiet
)

python -c "import autogen" 2>nul
if %errorlevel% NEQ 0 (
    echo Installing AutoGen...
    pip install pyautogen --quiet
)

python -c "import camel" 2>nul
if %errorlevel% NEQ 0 (
    echo Installing CAMEL-AI...
    pip install camel-ai --quiet
)

echo.
echo [3/4] Starting AI Orchestrator...
echo.

REM Check if orchestrator is already running
tasklist /FI "WINDOWTITLE eq AI Orchestrator" 2>NUL | find /I /N "python.exe" >NUL
if %errorlevel% EQU 0 (
    echo AI Orchestrator is already running
) else (
    start "AI Orchestrator" cmd /k "python orchestrator.py"
)

echo.
echo [4/4] Launching Interactive Interface...
echo.
echo ========================================
echo System is ready!
echo.
echo Available endpoints:
echo   - LocalAI API: http://localhost:8080/v1
echo   - Orchestrator: http://localhost:5000
echo   - LLMStack: http://localhost:3000
echo.
echo To test the system, run:
echo   python ai_frameworks_integration.py
echo.
echo ========================================
echo.

REM Launch the integration demo
choice /C YN /M "Do you want to start the interactive demo?"
if %errorlevel% EQU 1 (
    echo.
    echo Starting AI Frameworks Integration Demo...
    python ai_frameworks_integration.py
) else (
    echo.
    echo System is ready. You can run 'python ai_frameworks_integration.py' to start.
)

pause