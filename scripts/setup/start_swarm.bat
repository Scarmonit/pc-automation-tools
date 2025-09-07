@echo off
REM ================================================
REM AI Swarm Intelligence Launcher
REM Enhanced startup script with error handling
REM ================================================

echo.
echo ========================================
echo    AI SWARM INTELLIGENCE SYSTEM
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

REM Check if swarm directory exists
if not exist "%USERPROFILE%\.claude\swarm-intelligence" (
    echo [ERROR] Swarm intelligence directory not found
    echo Expected location: %USERPROFILE%\.claude\swarm-intelligence
    pause
    exit /b 1
)

REM Change to swarm directory
cd /d "%USERPROFILE%\.claude\swarm-intelligence"

REM Check for required files
if not exist "ai_platform_mcp_swarm.py" (
    echo [ERROR] Swarm intelligence files not found
    echo Please ensure all swarm files are properly installed
    pause
    exit /b 1
)

REM Check if AI Platform is running
netstat -an | findstr ":8000" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] AI Platform not detected on port 8000
    echo Swarm may have limited functionality
    echo.
)

REM Set environment variables if .env exists
if exist ".env" (
    echo Loading environment variables from .env...
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%b"=="" (
            set "%%a=%%b"
        )
    )
) else (
    echo [INFO] No .env file found, using system environment variables
    echo [TIP] Copy .env.template to .env and add your API keys
    echo.
)

REM Display swarm configuration
echo Configuration:
echo - Swarm Directory: %CD%
echo - Max Agents: %MAX_AGENTS%
echo - AI Platform: %AI_PLATFORM_URL%
echo - Memory DB: swarm_memory.db
echo.

REM Launch options
echo Select launch mode:
echo [1] Standard Swarm (Recommended)
echo [2] MCP Server Mode (For Claude Desktop integration)
echo [3] Debug Mode (Verbose logging)
echo [4] Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting AI Swarm Intelligence...
    echo Press Ctrl+C to stop
    echo ========================================
    python launch_global_swarm.py
) else if "%choice%"=="2" (
    echo.
    echo Starting Swarm MCP Server...
    echo Configure Claude Desktop to connect to this server
    echo Press Ctrl+C to stop
    echo ========================================
    python ai_platform_mcp_swarm.py
) else if "%choice%"=="3" (
    echo.
    echo Starting in Debug Mode...
    echo All debug output will be displayed
    echo Press Ctrl+C to stop
    echo ========================================
    set SWARM_DEBUG=true
    python -u launch_global_swarm.py
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

pause