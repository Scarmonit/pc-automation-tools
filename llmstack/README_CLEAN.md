# 🚀 AI Development Stack - Complete Setup

## Overview
A comprehensive AI development environment integrating multiple frameworks and tools for building intelligent applications.

## 🎯 Quick Start

Run the master control panel:
```bash
MASTER_CONTROL.bat
```

Or start everything at once:
```bash
START_AI_SYSTEM.bat
```

## 📦 Installed Components

### Core AI Frameworks
- **MemGPT** - Memory-enhanced conversations
- **AutoGen** - Multi-agent orchestration  
- **CAMEL-AI** - Collaborative agents
- **LocalAI** - Local model serving

### Development Tools
- **OpenHands** (http://localhost:3000) - AI coding assistant
- **Flowise** (http://localhost:3001) - Visual agent builder
- **Unified Orchestrator** (http://localhost:5000) - Central control

## 🌐 Service URLs

| Service | URL | Default Auth |
|---------|-----|--------------|
| OpenHands | http://localhost:3000 | None |
| Flowise | http://localhost:3001 | admin / flowise123 |
| LocalAI | http://localhost:8080 | None |
| Orchestrator | http://localhost:5000 | None |

## 📁 Project Structure

```
llmstack/
├── Core Systems/
│   ├── ai_frameworks_integration.py - Framework integration
│   ├── unified_orchestrator.py - Web-based orchestrator
│   └── orchestrator.py - Simple request router
│
├── Setup Scripts/
│   ├── MASTER_CONTROL.bat - Main control panel
│   ├── START_AI_SYSTEM.bat - Quick launcher
│   ├── setup_localai.bat - LocalAI installer
│   ├── setup_flowise.bat - Flowise installer
│   └── setup_openhands.bat - OpenHands installer
│
├── Test & Validation/
│   ├── test_installations.py - Check framework installs
│   ├── test_flowise.py - Test Flowise connection
│   └── verify_connections.py - Verify all services
│
├── Configuration/
│   ├── localai_config.yaml - LocalAI settings
│   ├── flowise_agent_flow.json - Pre-built agent
│   └── .claude/settings.json - Claude Code settings
│
└── Documentation/
    ├── README_CLEAN.md - This file
    ├── OPENHANDS_SETUP_GUIDE.md - OpenHands guide
    ├── FLOWISE_AGENT_SETUP.md - Flowise guide
    └── FLOWISE_QUICKSTART.md - Flowise quick start
```

## 🔧 Common Tasks

### Start Individual Services
```bash
# LocalAI
setup_localai.bat

# Flowise
docker start flowise

# OpenHands
docker start openhands

# Orchestrator
python unified_orchestrator.py
```

### Test Installation
```bash
python test_installations.py
```

### Check Service Status
```bash
python verify_connections.py
```

## 🐳 Docker Commands

```bash
# List running containers
docker ps

# View logs
docker logs -f flowise
docker logs -f openhands

# Restart services
docker restart flowise openhands

# Stop all
docker stop flowise openhands
```

## 🔌 API Integration

### Flowise API
```python
import requests

response = requests.post(
    "http://localhost:3001/api/v1/prediction/<chatflow-id>",
    json={"question": "Your prompt"}
)
```

### Unified Orchestrator API
```python
import requests

response = requests.post(
    "http://localhost:5000/execute",
    json={"task": "Your task", "framework": "auto"}
)
```

## 🛠️ Configuration

### LocalAI with Flowise
1. In Flowise ChatOpenAI node:
   - Base URL: `http://host.docker.internal:8080/v1`
   - API Key: `sk-localai`

### OpenHands LLM Setup
1. Access http://localhost:3000
2. Configure:
   - For LocalAI: Use base URL above
   - For OpenAI: Add your API key

## 📝 Environment Variables

Create `.env` file if needed:
```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
LOCALAI_ENDPOINT=http://localhost:8080/v1
```

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Find process using port
netstat -ano | findstr :3000

# Kill process
taskkill /PID <process_id> /F
```

### Docker Issues
```bash
# Reset Docker
docker system prune -a

# Rebuild containers
setup_flowise.bat
setup_openhands.bat
```

### Python Module Not Found
```bash
pip install memgpt pyautogen camel-ai openai requests flask
```

## 📊 System Requirements

- Python 3.9+ (3.11 recommended)
- Docker Desktop
- 8GB+ RAM
- 10GB+ free disk space
- Windows 10/11 or WSL2

## 🎯 Next Steps

1. Run `MASTER_CONTROL.bat`
2. Start all services (Option 1)
3. Open Flowise and import agent flow
4. Configure LocalAI or API keys
5. Test with sample prompts
6. Build your AI applications!

## 📚 Additional Resources

- [OpenHands Documentation](http://localhost:3000)
- [Flowise Documentation](http://localhost:3001)
- [LocalAI API Docs](http://localhost:8080/swagger)

---

**Ready to build with AI! 🚀**