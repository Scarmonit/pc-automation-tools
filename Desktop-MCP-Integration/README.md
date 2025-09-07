# MCP Integration for AI Platform

This directory contains Model Context Protocol (MCP) server implementations that integrate with your existing AI Platform and TidyAssistant.

## Components

### 1. Perplexity Web Search Server
- **File**: `perplexity_mcp.js`
- **Purpose**: Provides real-time web search through Perplexity API
- **Integration**: Uses your existing Perplexity API key

### 2. AI Platform MCP Server
- **File**: `ai_platform_mcp.py`
- **Purpose**: Exposes AI Platform capabilities through MCP
- **Features**: Multi-AI routing, health monitoring, request management

### 3. TidyAssistant MCP Server
- **File**: `tidy_assistant_mcp.py`
- **Purpose**: System monitoring and file organization through MCP
- **Features**: File cleanup, system stats, organization triggers

## Configuration

### Claude Desktop Configuration
Location: `%USERPROFILE%\.claude\claude_desktop_config.json`

### Usage
1. Install dependencies: `npm install` and `pip install -r requirements.txt`
2. Configure Claude Desktop with MCP servers
3. Restart Claude Desktop
4. Look for MCP indicator in conversation input

## Security
- All operations require explicit user approval
- File access is limited to specified directories
- API keys are securely managed through existing configuration