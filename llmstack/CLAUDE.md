# Claude Code Project Context - LLMStack AI Integration

## Project Overview
Complete local AI stack with zero API costs running on Windows system with:
- 32 CPU cores, 64GB RAM, 787GB disk space
- 7 AI models via Ollama (41.6 GB total)
- Docker-based services for visual workflows and monitoring

## Quick Commands

### AI Chat & Generation
```bash
ollama run deepseek-r1:8b        # Advanced reasoning
ollama run llama3.1:8b           # General purpose
ollama run dolphin-mistral:latest # Code generation
aider                            # AI coding assistant
```

### Service Access
- **Flowise**: http://localhost:3001 (Visual AI workflows)
- **OpenHands**: http://localhost:3002 (Autonomous coding)
- **Grafana**: http://localhost:3003 (Monitoring, login: admin/admin)

### Docker Management
```bash
docker ps                        # View running containers
docker logs flowise             # Check service logs
docker restart <container>      # Restart a service
```

## Service Configuration

### Ollama API Settings
- Base URL: `http://localhost:11434`
- OpenAI-compatible: `http://localhost:11434/v1`
- API Key: `ollama` (placeholder)

### Flowise Workflow Settings
When creating workflows in Flowise:
- Model Provider: ChatOllama
- Base URL: `http://host.docker.internal:11434`
- Available models: deepseek-r1:8b, llama3.1:8b, dolphin-mistral:latest, gemma2:27b

### AutoGen Configuration
Located at: `~/.autogen/config.json`
Uses Ollama models for multi-agent conversations

## Project Structure
```
C:\Users\scarm\llmstack\
├── examples/               # Usage examples for all services
├── scripts/               # Deployment and setup scripts
├── monitoring/            # Prometheus & Grafana configs
├── LLMStack/             # Main LLMStack repository
├── orchestrator.py       # Service integration orchestrator
└── DEPLOYMENT_COMPLETE.md # Full deployment documentation
```

## Automation Scripts

### Check All Connections
```bash
python C:\Users\scarm\llmstack\verify_connections.py
```

### Run Interactive Demos
```bash
C:\Users\scarm\llmstack\RUN_ALL_DEMOS.bat
```

### Start All Services
```bash
C:\Users\scarm\llmstack\START_NOW.bat
```

## Common Tasks

### Create a Visual AI Workflow
1. Open Flowise at http://localhost:3001
2. Create new Chatflow
3. Add ChatOllama component with settings above
4. Connect Buffer Memory and Conversation Chain
5. Save and test

### Generate Code with AI
```bash
aider
# Then: "Create a Python web scraper for news sites"
```

### Multi-Agent Development
```bash
python examples/04_autogen_agents.py
# Choose option 2 for development team simulation
```

## Troubleshooting

### Service Not Responding
```bash
docker restart <service-name>
docker logs <service-name> --tail 50
```

### High Memory Usage
```bash
# Unload unused models
curl -X DELETE http://localhost:11434/api/models/<model-name>

# Clear Docker cache
docker system prune -a
```

### Slow Responses
Use smaller models (3B instead of 7B) or reduce context size

## Important Notes
- All services run locally with zero external API costs
- Total model storage: 41.6 GB
- Everything is configured for user: scarmonit@gmail.com
- No external accounts required except local Grafana (admin/admin)

## Optimization Tips
1. Use `deepseek-r1:8b` for complex reasoning tasks
2. Use `dolphin-mistral:latest` for code generation
3. Use `llama3.1:8b` for general conversation
4. Break complex tasks into smaller steps
5. Run multiple Claude sessions for parallel work