@echo off
:: Description: Automation script for master control

cls
echo ========================================
echo    AI DEVELOPMENT STACK - MASTER CONTROL
echo ========================================
echo.
echo Select an option:
echo.
echo [1] Start All Services
echo [2] Start LocalAI
echo [3] Start Flowise
echo [4] Start OpenHands
echo [5] Run Unified Orchestrator
echo [6] Test Installations
echo [7] Check Service Status
echo [8] Stop All Services
echo [0] Exit
echo.
echo ========================================
choice /C 12345678 /N /M "Enter your choice: "

set choice=%errorlevel%

if %choice%==1 goto start_all
if %choice%==2 goto start_localai
if %choice%==3 goto start_flowise
if %choice%==4 goto start_openhands
if %choice%==5 goto start_orchestrator
if %choice%==6 goto test_install
if %choice%==7 goto check_status
if %choice%==8 goto stop_all
if %choice%==9 goto end

:start_all
echo.
echo Starting all services...
call setup_localai.bat
timeout /t 5 /nobreak >nul
start "Flowise" docker start flowise
start "OpenHands" docker start openhands
timeout /t 10 /nobreak >nul
start "Orchestrator" cmd /k "python unified_orchestrator.py"
echo.
echo All services starting...
echo   LocalAI:     http://localhost:8080
echo   Flowise:     http://localhost:3001
echo   OpenHands:   http://localhost:3000
echo   Orchestrator: http://localhost:5000
pause
goto menu

:start_localai
echo.
echo Starting LocalAI...
call setup_localai.bat
pause
goto menu

:start_flowise
echo.
echo Starting Flowise...
docker start flowise 2>nul || call setup_flowise.bat
echo Flowise available at: http://localhost:3001
start http://localhost:3001
pause
goto menu

:start_openhands
echo.
echo Starting OpenHands...
docker start openhands 2>nul || call setup_openhands.bat
echo OpenHands available at: http://localhost:3000
start http://localhost:3000
pause
goto menu

:start_orchestrator
echo.
echo Starting Unified Orchestrator...
start "Unified Orchestrator" cmd /k "python unified_orchestrator.py"
timeout /t 3 /nobreak >nul
start http://localhost:5000
pause
goto menu

:test_install
echo.
echo Testing installations...
python test_installations.py
echo.
pause
goto menu

:check_status
echo.
echo Checking service status...
echo.
echo === Docker Services ===
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
echo === Python Services ===
python -c "import requests; print('LocalAI:', 'ONLINE' if requests.get('http://localhost:8080', timeout=1).status_code==200 else 'OFFLINE')" 2>nul || echo LocalAI: OFFLINE
python -c "import requests; print('Flowise:', 'ONLINE' if requests.get('http://localhost:3001', timeout=1).status_code==200 else 'OFFLINE')" 2>nul || echo Flowise: OFFLINE
python -c "import requests; print('OpenHands:', 'ONLINE' if requests.get('http://localhost:3000', timeout=1).status_code==200 else 'OFFLINE')" 2>nul || echo OpenHands: OFFLINE
python -c "import requests; print('Orchestrator:', 'ONLINE' if requests.get('http://localhost:5000', timeout=1).status_code==200 else 'OFFLINE')" 2>nul || echo Orchestrator: OFFLINE
echo.
pause
goto menu

:stop_all
echo.
echo Stopping all services...
docker stop flowise openhands 2>nul
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq Unified Orchestrator*" 2>nul
taskkill /F /IM "localai.exe" 2>nul
echo All services stopped.
pause
goto menu

:menu
cls
goto :start

:end
echo.
echo Goodbye!
exit /b 0

:start
@echo off
cls
echo ========================================
echo    AI DEVELOPMENT STACK - MASTER CONTROL
echo ========================================
echo.
echo Select an option:
echo.
echo [1] Start All Services
echo [2] Start LocalAI
echo [3] Start Flowise
echo [4] Start OpenHands
echo [5] Run Unified Orchestrator
echo [6] Test Installations
echo [7] Check Service Status
echo [8] Stop All Services
echo [0] Exit
echo.
echo ========================================
choice /C 123456780 /N /M "Enter your choice: "

set choice=%errorlevel%

if %choice%==1 goto start_all
if %choice%==2 goto start_localai
if %choice%==3 goto start_flowise
if %choice%==4 goto start_openhands
if %choice%==5 goto start_orchestrator
if %choice%==6 goto test_install
if %choice%==7 goto check_status
if %choice%==8 goto stop_all
if %choice%==9 goto end