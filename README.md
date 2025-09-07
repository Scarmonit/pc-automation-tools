# LLMStack Open Source Deployment

Complete deployment guide and scripts for running LLMStack with 100% free and open source components. Zero API costs, full data privacy, production-ready system.

## 🎯 Purpose

Deploy LLMStack with local AI models (Ollama, LM Studio) and free AI agents (AutoGen, Flowise, OpenHands, Aider) for a completely self-hosted AI development environment.

## 📋 System Requirements

- **CPU:** 4+ cores recommended
- **RAM:** 8GB+ (16GB recommended)
- **Storage:** 50GB+ free disk space
- **GPU:** Optional but recommended (4GB+ VRAM)
- **OS:** Linux, macOS, or Windows with WSL2

## 🚀 Quick Start

### Phase 1: System Check
```bash
bash scripts/check_system.sh
```

### Phase 2: Install Local Model Server
```bash
bash scripts/install_ollama.sh
```

### Phase 3: Deploy LLMStack
```bash
bash scripts/deploy_llmstack.sh
```

### Phase 4: Install AI Agents
```bash
bash scripts/install_agents.sh
```

### Phase 5: Validate Deployment
```bash
bash scripts/validate_deployment.sh
```

## 🧠 Available AI Agents

- **Ollama** - Local model inference (Llama, Mistral, CodeLlama)
- **AutoGen** - Multi-agent conversations
- **Flowise** - Visual AI workflow builder
- **OpenHands** - AI coding assistant
- **Aider** - AI pair programming

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLMStack UI   │    │    Flowise      │    │   OpenHands     │
│  (Port 3000)    │    │  (Port 3001)    │    │  (Port 3002)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Ollama      │
                    │  (Port 11434)   │
                    │                 │
                    │ • llama3.2:3b   │
                    │ • mistral:7b    │
                    │ • codellama:7b  │
                    └─────────────────┘
```

## 📚 Directory Structure

```
.
├── scripts/                    # Deployment scripts
│   ├── check_system.sh        # System requirements check
│   ├── install_ollama.sh      # Ollama installation
│   ├── deploy_llmstack.sh     # LLMStack deployment
│   ├── install_agents.sh      # AI agents installation
│   ├── validate_deployment.sh # Deployment validation
│   └── orchestrator.py        # Agent orchestration
├── llmstack/                  # LLMStack examples and configs
├── ai-tools/                  # Additional AI tools
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Advanced Usage

### Agent Orchestration
```python
from scripts.orchestrator import FreeAgentOrchestrator

orchestrator = FreeAgentOrchestrator()

# Route requests to appropriate agents
response = await orchestrator.route_request(
    "Write a Python function to calculate fibonacci",
    task_type="code"
)
```

### Custom Model Configuration
Edit `~/.autogen/config.json` to add custom models:
```json
{
  "model_list": [
    {
      "model": "your-custom-model",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "api_type": "openai"
    }
  ]
}
```

## 🎛️ Access Points

After successful deployment:

- **LLMStack UI:** http://localhost:3000
- **Flowise:** http://localhost:3001
- **OpenHands:** http://localhost:3002
- **Ollama API:** http://localhost:11434/v1

## 📊 Cost Breakdown

| Component | Cost | Alternative |
|-----------|------|-------------|
| LLMStack | $0 (Open Source) | Langflow ($99/mo) |
| Local Models | $0 (Self-hosted) | OpenAI GPT-4 ($20/mo) |
| AutoGen | $0 (Open Source) | AgentGPT ($30/mo) |
| Flowise | $0 (Open Source) | Zapier ($20/mo) |
| **Total** | **$0/month** | **$169/month** |

## 🛠️ Troubleshooting

### Service won't start
```bash
docker logs <container_name>
sudo systemctl status ollama
lsof -i :3000  # Check port conflicts
```

### Out of memory
```bash
docker system prune -a
ollama rm unused_model
```

### Slow inference
```bash
export OLLAMA_NUM_PARALLEL=1
ollama run llama3.2:1b  # Use smaller model
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [LLMStack](https://github.com/trypromptly/LLMStack) - Main platform
- [Ollama](https://ollama.ai/) - Local model inference
- [AutoGen](https://github.com/microsoft/autogen) - Multi-agent framework
- [Flowise](https://flowiseai.com/) - Visual AI workflows

---

**Total API Cost: $0.00 • Data Privacy: 100% Local • Production Ready: YES**