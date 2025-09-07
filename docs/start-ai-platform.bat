@echo off
title AI Platform - Windows Edition
echo.
echo ========================================
echo  AI Platform - Windows Edition
echo ========================================
echo.

cd /d "%~dp0"

echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [INFO] Installing Python dependencies...
pip install -r requirements.txt --quiet

if not exist ".env" (
    echo [WARNING] .env file not found. Creating from template...
    copy ".env.example" ".env"
    echo [INFO] Please edit .env file with your API keys
    pause
)

echo [INFO] Starting AI Platform server...
echo [INFO] Server will be available at: http://localhost:8000
echo [INFO] API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python ai_platform.py

echo.
echo [INFO] AI Platform stopped
pause