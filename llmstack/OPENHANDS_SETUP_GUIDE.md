# OpenHands Setup Guide

## Quick Start

OpenHands is now starting up! Here's how to complete the setup:

## 1. Access OpenHands

Open your browser and navigate to:
**http://localhost:3000**

## 2. Initial Configuration

When you first access OpenHands, you'll see the configuration screen. Configure the following:

### LLM Provider Options:

#### Option A: Use OpenAI
- Enter your OpenAI API key
- Select model: `gpt-4` or `gpt-3.5-turbo`
- Base URL: Leave default

#### Option B: Use Anthropic Claude
- Enter your Anthropic API key  
- Select model: `claude-3-opus-20240229` or `claude-3-sonnet-20240229`

#### Option C: Use LocalAI (Recommended for local development)
- API Key: `sk-localai` (or any dummy key)
- Base URL: `http://host.docker.internal:8080/v1`
- Model: `gpt-3.5-turbo`

### Advanced Settings:
- **Max iterations**: 100 (default)
- **Security**: Enable sandbox for safe code execution
- **Workspace**: `/workspace` (mounted to `C:\Users\scarm\openhands-workspace`)

## 3. Start Building

Once configured, you can:

1. **Create a new agent** - Click "New Agent" to start
2. **Define your task** - Describe what you want to build
3. **Watch it work** - OpenHands will write, test, and debug code
4. **Iterate** - Provide feedback and refine

## Common Tasks

### Building a Web App
```
"Create a React todo list app with the following features:
- Add/remove tasks
- Mark tasks as complete
- Filter by status
- Persist to localStorage"
```

### Data Analysis
```
"Analyze the CSV file in /workspace/data.csv and create:
- Summary statistics
- Visualizations using matplotlib
- Insights report"
```

### API Development
```
"Build a REST API using FastAPI with:
- CRUD operations for a blog
- SQLite database
- Authentication with JWT
- Auto-generated documentation"
```

## Connecting to Your AI Stack

### Use with LocalAI
If LocalAI is running (`setup_localai.bat`), configure:
- Base URL: `http://host.docker.internal:8080/v1`
- Model: Any model you have in LocalAI

### Use with Ollama
If Ollama is running:
- Base URL: `http://host.docker.internal:11434/v1`
- Model: Any Ollama model (e.g., `llama3.1`, `deepseek-r1`)

## Workspace Management

Your workspace is at: `C:\Users\scarm\openhands-workspace`

- All files created by OpenHands appear here
- You can add existing projects to this folder
- OpenHands can read/write any files in this directory

## Docker Commands

### View logs
```bash
docker logs -f openhands
```

### Stop OpenHands
```bash
docker stop openhands
```

### Restart OpenHands
```bash
docker start openhands
```

### Remove and reinstall
```bash
docker rm openhands
docker pull ghcr.io/all-hands-ai/openhands:latest
# Then run setup_openhands.bat again
```

## Troubleshooting

### Port 3000 is already in use
Stop the conflicting service or change the port:
```bash
docker run -p 3001:3000 ... (rest of command)
```

### Can't connect to LocalAI
Ensure LocalAI is running:
```bash
cd C:\Users\scarm\llmstack
setup_localai.bat
```

### Container won't start
Check Docker Desktop is running and try:
```bash
docker system prune -a
# Then run setup again
```

## Integration with AI Frameworks

OpenHands can work with your installed frameworks:

1. **MemGPT** - For memory-persistent development sessions
2. **AutoGen** - For multi-agent code reviews
3. **CAMEL-AI** - For collaborative development
4. **LocalAI** - For local LLM inference

Use the Unified Orchestrator (`python unified_orchestrator.py`) to coordinate between all systems.

## Next Steps

1. **Open browser**: http://localhost:3000
2. **Configure API keys** or use LocalAI
3. **Start with a simple task** to test
4. **Scale up** to complex projects

Happy building with OpenHands! 🚀