@echo off
REM ================================================
REM Swarm Intelligence Environment Setup Script
REM Sets up API keys and environment variables
REM ================================================

echo.
echo ========================================
echo   SWARM INTELLIGENCE ENVIRONMENT SETUP
echo ========================================
echo.

REM Create .env file from template if it doesn't exist
if not exist "%USERPROFILE%\.claude\swarm-intelligence\.env" (
    if exist "%USERPROFILE%\.claude\swarm-intelligence\.env.template" (
        echo Creating .env file from template...
        copy "%USERPROFILE%\.claude\swarm-intelligence\.env.template" "%USERPROFILE%\.claude\swarm-intelligence\.env"
        echo.
        echo IMPORTANT: Edit .env file with your API keys:
        echo Location: %USERPROFILE%\.claude\swarm-intelligence\.env
        echo.
    )
)

echo Setting environment variables for current session...
echo.

REM Core Swarm Configuration
set AI_PLATFORM_URL=http://localhost:8000
set TIDY_ASSISTANT_URL=http://localhost:8001
set DEMO_TOKEN=demo-token
set ENABLE_SWARM_INTELLIGENCE=true
set ENABLE_DISTRIBUTED_MEMORY=true
set ENABLE_COLLABORATION=true
set MAX_AGENTS=10
set WORKSPACE_ROOT=%USERPROFILE%

REM Swarm File Paths
set SWARM_MEMORY_DB=%USERPROFILE%\.claude\swarm-intelligence\swarm_memory.db
set SWARM_CONFIG=%USERPROFILE%\.claude\swarm-intelligence\swarm_config.json
set PROMPTS_CONFIG=%USERPROFILE%\.claude\swarm-intelligence\prompts_config.json

echo Environment variables set:
echo - AI_PLATFORM_URL: %AI_PLATFORM_URL%
echo - MAX_AGENTS: %MAX_AGENTS%
echo - WORKSPACE_ROOT: %WORKSPACE_ROOT%
echo - SWARM_MEMORY_DB: %SWARM_MEMORY_DB%
echo.

REM Check for API keys
echo Checking for API keys...
if "%ANTHROPIC_API_KEY%"=="" (
    echo [WARNING] ANTHROPIC_API_KEY not set
    echo Please set your Anthropic API key:
    echo   set ANTHROPIC_API_KEY=your_anthropic_api_key_here
    echo.
)

if "%OPENAI_API_KEY%"=="" (
    echo [INFO] OPENAI_API_KEY not set (optional)
)

if "%PERPLEXITY_API_KEY%"=="" (
    echo [INFO] PERPLEXITY_API_KEY not set (optional - needed for research features)
)

echo.
echo To permanently set API keys, either:
echo 1. Edit the .env file at: %USERPROFILE%\.claude\swarm-intelligence\.env
echo 2. Set them as system environment variables in Windows
echo.

REM Install required Python packages
echo Checking Python dependencies...
python -c "import mcp" 2>nul
if %errorlevel% neq 0 (
    echo Installing MCP SDK...
    pip install mcp
)

python -c "import aiohttp" 2>nul
if %errorlevel% neq 0 (
    echo Installing aiohttp...
    pip install aiohttp
)

python -c "import anthropic" 2>nul
if %errorlevel% neq 0 (
    echo Installing Anthropic SDK...
    pip install anthropic
)

echo.
echo ========================================
echo Setup complete!
echo.
echo Next steps:
echo 1. Add your API keys to the .env file or set them as environment variables
echo 2. Run 'start_swarm.bat' to launch the swarm intelligence
echo 3. For Claude Desktop integration, restart Claude Desktop after configuration
echo.
pause