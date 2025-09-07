@echo off
cls
echo ============================================================
echo           DOLPHIN-MISTRAL LAUNCHER
echo ============================================================
echo.
echo Select how to use Dolphin-Mistral:
echo.
echo   1. Command Line Chat (Terminal)
echo   2. GUI Interface (Graphical)
echo   3. Python Script Mode
echo   4. Direct Quick Question
echo   5. Exit
echo.
echo ============================================================
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto terminal
if "%choice%"=="2" goto gui
if "%choice%"=="3" goto python
if "%choice%"=="4" goto quick
if "%choice%"=="5" goto end

:terminal
echo.
echo Starting terminal chat...
ollama run dolphin-mistral
pause
goto end

:gui
echo.
echo Starting GUI interface...
python dolphin_gui.py
pause
goto end

:python
echo.
echo Starting Python assistant...
python ollama_security_assistant.py
pause
goto end

:quick
echo.
set /p question="Enter your question: "
echo.
echo Processing...
echo.
ollama run dolphin-mistral "%question%"
echo.
pause
goto end

:end
exit