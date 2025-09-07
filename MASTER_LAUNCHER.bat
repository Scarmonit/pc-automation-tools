@echo off
title AI Platform & PC Automation Master Launcher
color 0E
cls

echo ============================================
echo    AI PLATFORM MASTER LAUNCHER
echo ============================================
echo.
echo === PC AUTOMATION TOOLS ===
echo 1. Screenshot Tools
echo 2. System Automation
echo 3. Cloud Management (RunPod)
echo 4. DeepSeek AI Setup
echo.
echo === AI PLATFORM MODULES ===
echo 5. Core AI Platform
echo 6. Security Scanner
echo 7. Dolphin Models
echo 8. Automation Swarm
echo.
echo === QUICK ACTIONS ===
echo 9. Take Screenshot for Claude
echo 10. View All Documentation
echo 11. Run System Tests
echo 12. Exit
echo.
set /p choice="Select [1-12]: "

if "%choice%"=="1" (
    echo.
    echo Screenshot Tools:
    echo - Press Windows + Print Screen for instant capture
    echo - Screenshots save to: %USERPROFILE%\Pictures\Screenshots\
    start explorer screenshot-tools
    pause
    goto :eof
)

if "%choice%"=="2" (
    cd system-tools
    if exist MASTER_CONTROL.bat (
        call MASTER_CONTROL.bat
    ) else (
        echo Running workspace control...
        powershell -ExecutionPolicy Bypass -File WORKSPACE_CONTROL.ps1
    )
    goto :eof
)

if "%choice%"=="3" (
    cd cloud-tools
    if exist runpod_helper.bat (
        call runpod_helper.bat
    ) else (
        echo RunPod helper not found
        pause
    )
    goto :eof
)

if "%choice%"=="4" (
    cd ai-tools\deepseek_setup
    if exist DEEPSEEK_QUICK.bat (
        call DEEPSEEK_QUICK.bat
    ) else (
        echo Running DeepSeek setup...
        python deepseek_setup.py
    )
    goto :eof
)

if "%choice%"=="5" (
    echo Starting Core AI Platform...
    python main.py core
    pause
    goto :eof
)

if "%choice%"=="6" (
    echo Starting Security Scanner...
    python main.py security --action webscan
    pause
    goto :eof
)

if "%choice%"=="7" (
    echo Starting Dolphin Models...
    python main.py dolphin --action gui
    pause
    goto :eof
)

if "%choice%"=="8" (
    echo Starting Automation Swarm...
    python main.py automation --action swarm
    pause
    goto :eof
)

if "%choice%"=="9" (
    echo Taking screenshot...
    powershell -ExecutionPolicy Bypass -File screenshot-tools\screenshot.ps1
    pause
    goto :eof
)

if "%choice%"=="10" (
    echo Opening documentation...
    start notepad README.md
    start explorer docs
    goto :eof
)

if "%choice%"=="11" (
    echo Running tests...
    python -m pytest src/tests/ -v
    pause
    goto :eof
)

if "%choice%"=="12" exit

echo Invalid choice
pause