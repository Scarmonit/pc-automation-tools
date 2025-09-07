@echo off
title Dolphin Security Assistant
echo Starting Dolphin Security Assistant...
echo.

if exist DolphinSecurityAssistant.exe (
    DolphinSecurityAssistant.exe
) else (
    echo [ERROR] DolphinSecurityAssistant.exe not found!
    echo Please run build_dolphin_exe.py first
    pause
)
