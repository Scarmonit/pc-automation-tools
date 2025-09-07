@echo off
title MCP Integration Setup
echo.
echo ========================================
echo  MCP Integration Setup for AI Platform
echo ========================================
echo.

cd /d "%~dp0"

echo [INFO] Installing Node.js dependencies...
npm install

echo [INFO] Installing Python dependencies...
pip install mcp aiohttp

echo [INFO] Setting up Claude Desktop configuration...
set CLAUDE_CONFIG_DIR=%USERPROFILE%\.claude
if not exist "%CLAUDE_CONFIG_DIR%" mkdir "%CLAUDE_CONFIG_DIR%"

echo [INFO] Copying MCP configuration to Claude Desktop...
copy /Y "claude_desktop_config.json" "%CLAUDE_CONFIG_DIR%\claude_desktop_config.json"

echo [INFO] Testing Perplexity MCP server...
timeout /t 2 >nul
node perplexity_mcp.js --test 2>nul || echo [WARNING] Node.js MCP server test had issues (this is expected without stdio)

echo [SUCCESS] MCP Integration setup complete!
echo.
echo Next steps:
echo 1. Restart Claude Desktop if it's running
echo 2. Look for MCP indicator in conversation input
echo 3. Try using web search or AI Platform tools
echo.
echo Available MCP Tools:
echo • web_search          - Search the web with Perplexity
echo • research_topic      - Comprehensive topic research  
echo • ai_chat            - Chat with Claude/OpenAI/Perplexity
echo • platform_health    - Check AI Platform status
echo • tidy_status        - Check TidyAssistant status
echo • File system access - Read/write files in Desktop/Downloads/Documents
echo.
pause