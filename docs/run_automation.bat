@echo off
echo ====================================
echo      GPU PLATFORM AUTOMATION
echo ====================================
echo.

echo Installing required packages...
pip install selenium undetected-chromedriver fake-useragent requests

echo.
echo Choose automation option:
echo 1. Full setup automation (signups + tests)
echo 2. Advanced web scraper signup bot
echo 3. Lightning AI quest automation only
echo 4. Run GPU performance tests
echo 5. Monitor GPU usage dashboard
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    echo Running full automation...
    python automate_gpu_setup.py
) else if "%choice%"=="2" (
    echo Running advanced signup bot...
    python web_scraper_signup.py
) else if "%choice%"=="3" (
    echo Running Lightning AI quest automation...
    python lightning_quest_automator.py
) else if "%choice%"=="4" (
    echo Running GPU performance tests...
    python gpu_performance_test.py
) else if "%choice%"=="5" (
    echo Showing GPU usage dashboard...
    python gpu_monitor.py
) else (
    echo Invalid choice!
)

echo.
pause