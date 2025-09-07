# Enhanced AI Platform MCP Server

## Overview

This enhanced MCP server incorporates best practices from leading AI tools like Cursor, Claude Code, Cline, and others. It provides intelligent prompt management, security validation, and advanced AI capabilities through the Model Context Protocol (MCP).

## Key Features

### 🧠 Intelligent Prompt Management
- **8 specialized prompt categories** optimized for different use cases
- **Automatic model selection** based on task requirements
- **Context-aware prompt enhancement** for better AI responses
- **Dynamic prompt optimization** based on analysis of 20,000+ lines of system prompts

### 🛡️ Security & Validation
- **Real-time security scanning** for dangerous code patterns
- **Automatic prompt sanitization** to prevent injection attacks
- **Content validation** before processing
- **Safe execution environment** with comprehensive logging

### 🚀 Advanced Tools
1. **smart_ai_chat** - Intelligent AI chat with automatic prompt optimization
2. **batch_ai_analysis** - Compare responses from multiple AI models
3. **prompt_optimization** - Analyze and improve prompts for better results
4. **security_check** - Validate content for security concerns
5. **platform_health** - Monitor system status and health

### 📝 Prompt Categories

| Category | Best For | Preferred Models |
|----------|----------|-----------------|
| `coding_assistant` | General programming help | Claude, GPT-4 |
| `code_review` | Bug detection, security analysis | Claude, GPT-4 |
| `documentation` | Technical writing, guides | GPT-4, Claude |
| `creative_problem_solving` | Innovation, brainstorming | GPT-4, Sonar |
| `research_analysis` | Information research | Sonar, GPT-4 |
| `debugging` | Systematic problem solving | Claude, GPT-4 |
| `architecture_design` | System design patterns | Claude, GPT-4 |
| `performance_optimization` | Speed and efficiency | Claude, GPT-4 |

## Installation & Setup

### Prerequisites
- Python 3.8+
- MCP SDK (`pip install mcp`)
- aiohttp (`pip install aiohttp`)

### Quick Setup
```bash
cd Desktop/MCP-Integration
python setup_enhanced_mcp.py
```

This automatically:
- Configures Claude Desktop integration
- Sets up Cursor IDE integration
- Creates launch scripts
- Validates system components

### Manual Testing
```bash
python launch_enhanced_mcp.py
```

## Usage Examples

### Basic AI Chat with Smart Prompting
```json
{
  "tool": "smart_ai_chat",
  "arguments": {
    "prompt": "Help me debug this Python function that's causing memory leaks",
    "category": "debugging",
    "context": "Python web application with Flask"
  }
}
```

### Batch Analysis Comparison
```json
{
  "tool": "batch_ai_analysis", 
  "arguments": {
    "prompt": "Design a microservices architecture for an e-commerce platform",
    "models": ["claude-3-haiku-20240307", "gpt-4o"]
  }
}
```

### Prompt Optimization
```json
{
  "tool": "prompt_optimization",
  "arguments": {
    "prompt": "make code better",
    "target_category": "code_review"
  }
}
```

### Security Validation
```json
{
  "tool": "security_check",
  "arguments": {
    "content": "import os; os.system('rm -rf /')"
  }
}
```

## Architecture

### Core Components

1. **PromptManager** - Manages specialized prompts and model selection
2. **SecurityManager** - Validates and sanitizes content for security
3. **EnhancedAIPlatformMCPServer** - Main server with advanced capabilities

### Security Features

- Pattern detection for dangerous code
- Input sanitization and validation
- Secure content processing
- Comprehensive audit logging

### Model Integration

Supports multiple AI models with intelligent routing:
- **Claude 3 Haiku** - Code analysis, debugging, accuracy
- **GPT-4** - Creative problem solving, documentation
- **GPT-4 Mini** - Quick tasks, cost efficiency
- **Sonar Pro/Small** - Research, current information

## Configuration Files

### prompts_config.json
Contains detailed configurations for:
- Prompt categories and templates
- Security patterns and rules  
- Model capabilities and preferences
- Optimization guidelines

### claude_desktop_config.json
MCP server configuration for Claude Desktop integration.

### .cursor/mcp.json
MCP server configuration for Cursor IDE integration.

## Best Practices Integration

This server incorporates proven practices from:

- **Cursor Agent** - Tool usage patterns and code generation
- **Claude Code** - Concise responses and security focus
- **Cline** - Systematic problem solving approach
- **Replit** - Interactive development workflows
- **VSCode Agent** - IDE integration patterns

## Performance & Monitoring

- Response time tracking
- Token usage monitoring
- Error rate analysis
- Security incident logging
- Model performance comparison

## Security Considerations

### Validated Patterns
The system detects and blocks potentially dangerous patterns:
- Code execution functions (`eval`, `exec`, `os.system`)
- File system operations (`rm -rf`, `del /`)
- Script injections (`<script>`, `javascript:`)
- System imports and subprocess calls

### Safe Processing
- All user input is sanitized before processing
- System prompts are isolated from user content
- Security warnings are provided for risky content
- Comprehensive logging for audit trails

## Contributing

The enhanced MCP server is designed to be extensible:

1. **Add new prompt categories** in `prompts_config.json`
2. **Extend security patterns** for new threat detection
3. **Integrate additional models** with capability definitions
4. **Enhance tools** with new functionality

## Future Enhancements

- **Machine learning-based** prompt optimization
- **Advanced security** with AI-powered threat detection
- **Performance analytics** dashboard
- **Custom model** integration support
- **Multi-language** prompt templates

---

**Powered by insights from 20,000+ lines of AI system prompts**

This enhanced MCP server represents the culmination of best practices from the world's leading AI development tools, providing a secure, intelligent, and highly capable platform for AI-assisted development.