@echo off
echo ========================================
echo OpenHands AI Development Environment Setup
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% NEQ 0 (
    echo ERROR: Docker is not running.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Docker is running. Proceeding with OpenHands setup...
echo.

REM Pull the latest OpenHands image
echo [1/4] Pulling OpenHands Docker image...
docker pull ghcr.io/all-hands-ai/openhands:latest

echo.
echo [2/4] Creating workspace directory...
if not exist "C:\Users\scarm\openhands-workspace" (
    mkdir "C:\Users\scarm\openhands-workspace"
    echo Created workspace at C:\Users\scarm\openhands-workspace
) else (
    echo Workspace already exists at C:\Users\scarm\openhands-workspace
)

echo.
echo [3/4] Stopping any existing OpenHands containers...
docker stop openhands 2>nul
docker rm openhands 2>nul

echo.
echo [4/4] Starting OpenHands...
echo.
echo ========================================
echo OpenHands will be available at:
echo   http://localhost:3000
echo.
echo Default credentials:
echo   No authentication required for local setup
echo.
echo API Keys Configuration:
echo   You'll be prompted to enter API keys on first login
echo ========================================
echo.

REM Start OpenHands with proper configuration
docker run -d ^
    --name openhands ^
    -p 3000:3000 ^
    -v C:\Users\scarm\openhands-workspace:/workspace ^
    -e WORKSPACE_MOUNT_PATH=/workspace ^
    -e SANDBOX_TYPE=local ^
    -e SANDBOX_USER_ID=1000 ^
    --add-host host.docker.internal:host-gateway ^
    ghcr.io/all-hands-ai/openhands:latest

if %errorlevel% EQU 0 (
    echo.
    echo OpenHands started successfully!
    echo.
    echo Waiting for OpenHands to initialize (15 seconds)...
    timeout /t 15 /nobreak >nul
    
    echo.
    echo Opening OpenHands in your browser...
    start http://localhost:3000
    
    echo.
    echo ========================================
    echo SETUP COMPLETE!
    echo.
    echo Next steps:
    echo 1. Browser should open automatically to http://localhost:3000
    echo 2. On first login, you'll see the setup wizard
    echo 3. Configure your preferred LLM provider:
    echo    - OpenAI API key
    echo    - Anthropic API key  
    echo    - Or connect to LocalAI at http://localhost:8080
    echo 4. Start building your AI agents!
    echo.
    echo To view logs: docker logs -f openhands
    echo To stop: docker stop openhands
    echo To restart: docker start openhands
    echo ========================================
) else (
    echo.
    echo ERROR: Failed to start OpenHands.
    echo Please check Docker logs for more information.
    docker logs openhands
)

pause