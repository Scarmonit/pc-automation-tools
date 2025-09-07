@echo off
echo ========================================
echo LocalAI Setup and Installation Script
echo ========================================
echo.

REM Check if LocalAI is already installed
where localai >nul 2>&1
if %errorlevel% == 0 (
    echo LocalAI is already installed.
    goto :start_server
)

echo Installing LocalAI...
echo.

REM Download LocalAI using PowerShell
echo Downloading LocalAI binary...
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/mudler/LocalAI/releases/latest/download/local-ai-avx2-Windows-x86_64.exe' -OutFile 'localai.exe'}"

if exist localai.exe (
    echo LocalAI downloaded successfully!
    
    REM Create models directory
    if not exist models mkdir models
    
    REM Download a sample model (Llama 2 7B)
    echo.
    echo Downloading Llama 2 7B model (this may take a while)...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf' -OutFile 'models\llama-2-7b-chat.gguf'}"
    
    echo Model downloaded successfully!
) else (
    echo Failed to download LocalAI. Please check your internet connection.
    pause
    exit /b 1
)

:start_server
echo.
echo Starting LocalAI server...
echo Server will be available at: http://localhost:8080
echo API endpoint: http://localhost:8080/v1
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start LocalAI with the configuration
if exist localai_config.yaml (
    localai.exe --config localai_config.yaml --models-path ./models
) else (
    localai.exe --models-path ./models --address 0.0.0.0:8080
)

pause