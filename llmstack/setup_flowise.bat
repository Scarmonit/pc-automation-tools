@echo off
echo ========================================
echo Flowise AI Agent Builder Setup
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

REM Check if Flowise is already running
docker ps | findstr -i flowise >nul 2>&1
if %errorlevel% EQU 0 (
    echo Flowise is already running!
    echo.
    echo Opening Flowise in your browser...
    start http://localhost:3001
    echo.
    echo ========================================
    echo Flowise is available at: http://localhost:3001
    echo ========================================
    pause
    exit /b 0
)

echo Docker is running. Setting up Flowise...
echo.

REM Create necessary directories
echo [1/5] Creating Flowise directories...
if not exist "C:\Users\scarm\flowise-data" (
    mkdir "C:\Users\scarm\flowise-data"
    echo Created data directory at C:\Users\scarm\flowise-data
)

if not exist "C:\Users\scarm\flowise-data\uploads" (
    mkdir "C:\Users\scarm\flowise-data\uploads"
)

if not exist "C:\Users\scarm\flowise-data\database" (
    mkdir "C:\Users\scarm\flowise-data\database"
)

echo.
echo [2/5] Pulling Flowise Docker image...
docker pull flowiseai/flowise:latest

echo.
echo [3/5] Stopping any existing Flowise containers...
docker stop flowise 2>nul
docker rm flowise 2>nul

echo.
echo [4/5] Creating Flowise configuration...
(
echo # Flowise Environment Configuration
echo PORT=3000
echo DATABASE_TYPE=sqlite
echo DATABASE_PATH=/root/.flowise
echo APIKEY_PATH=/root/.flowise
echo SECRETKEY_PATH=/root/.flowise
echo LOG_PATH=/root/.flowise/logs
echo BLOB_STORAGE_PATH=/root/.flowise/storage
echo 
echo # LLM Configurations
echo OPENAI_API_KEY=%OPENAI_API_KEY%
echo ANTHROPIC_API_KEY=%ANTHROPIC_API_KEY%
echo 
echo # LocalAI Configuration
echo LOCALAI_API_BASE=http://host.docker.internal:8080/v1
echo LOCALAI_API_KEY=sk-localai
echo 
echo # Security
echo FLOWISE_USERNAME=admin
echo FLOWISE_PASSWORD=flowise123
echo 
echo # Features
echo DISABLE_CHATFLOW_REUSE=false
echo TOOL_FUNCTION_BUILTIN_DEP=true
echo TOOL_FUNCTION_EXTERNAL_DEP=true
) > "C:\Users\scarm\flowise-data\.env"

echo.
echo [5/5] Starting Flowise...
docker run -d ^
    --name flowise ^
    -p 3001:3000 ^
    -v "C:\Users\scarm\flowise-data:/root/.flowise" ^
    --env-file "C:\Users\scarm\flowise-data\.env" ^
    --add-host host.docker.internal:host-gateway ^
    flowiseai/flowise:latest

if %errorlevel% EQU 0 (
    echo.
    echo Flowise started successfully!
    echo.
    echo Waiting for Flowise to initialize (10 seconds)...
    timeout /t 10 /nobreak >nul
    
    echo.
    echo Opening Flowise in your browser...
    start http://localhost:3001
    
    echo.
    echo ========================================
    echo FLOWISE SETUP COMPLETE!
    echo.
    echo Access Flowise at: http://localhost:3001
    echo.
    echo Default Credentials:
    echo   Username: admin
    echo   Password: flowise123
    echo.
    echo Quick Start:
    echo 1. Login with credentials above
    echo 2. Click "Chatflows" to create a new flow
    echo 3. Drag and drop nodes to build your agent
    echo 4. Connect to LocalAI or OpenAI
    echo 5. Test your agent in the chat interface
    echo.
    echo To view logs: docker logs -f flowise
    echo To stop: docker stop flowise
    echo To restart: docker start flowise
    echo ========================================
) else (
    echo.
    echo ERROR: Failed to start Flowise.
    echo Please check Docker logs for more information.
    docker logs flowise
)

pause