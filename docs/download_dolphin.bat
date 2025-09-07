@echo off
echo ============================================================
echo DOWNLOADING DOLPHIN-MISTRAL (UNCENSORED MODEL)
echo ============================================================
echo.
echo [!] This will download a 4.3GB model
echo [!] Estimated time: 5-15 minutes depending on connection
echo.
echo Starting download...
echo.

ollama pull dolphin-mistral

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo DOWNLOAD COMPLETE!
    echo ============================================================
    echo.
    echo Dolphin-Mistral is now ready to use.
    echo.
    echo Quick test:
    echo   ollama run dolphin-mistral "What is SQL injection?"
    echo.
    echo Interactive chat:
    echo   ollama run dolphin-mistral
    echo.
    echo [!] This is an uncensored model - use responsibly
    echo [!] You are responsible for how you use this tool
    echo.
) else (
    echo.
    echo [ERROR] Download failed. Please try again or check your connection.
    echo.
)

pause