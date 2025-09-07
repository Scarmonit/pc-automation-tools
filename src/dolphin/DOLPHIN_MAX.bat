@echo off
cls
color 0A
echo.
echo  ====================================================================
echo   ___   ___  _    ___ _  _ ___ _  _     __  __   ___  __  __
echo  ^|   \ / _ \^| ^|  ^| _ \ ^|^| ^|_ _^| \^| ^|   ^|  \/  ^| / _ \ \ \/ /
echo  ^| ^|) ^| (_) ^| ^|_ ^|  _/ __ ^|^| ^| .` ^|___^| ^|\/^| ^|^| (_) ^| )  ( 
echo  ^|___/ \___/^|____^|_^| ^|_^|^|_^|___^|_^|\_^|   ^|_^|  ^|_^| \___/ /_/\_\
echo.
echo            MAXIMUM INTELLIGENCE SECURITY AI
echo  ====================================================================
echo.
echo  [!] This is DOLPHIN-MAX - The most intelligent version possible
echo  [!] Optimized for maximum capability and performance
echo  [!] Use responsibly for authorized testing only
echo.
echo  ====================================================================
echo.

:: Set optimization variables
set OLLAMA_NUM_PARALLEL=4
set OLLAMA_MAX_LOADED_MODELS=1
set OLLAMA_KEEP_ALIVE=24h
set OLLAMA_FLASH_ATTENTION=1

echo  Starting DOLPHIN-MAX...
echo.

ollama run dolphin-max

pause
