# LLMStack Open Source Deployment

Complete deployment guide and scripts for running LLMStack with 100% free and open source components. Zero API costs, full data privacy, production-ready system.

## 🎯 Purpose

Deploy LLMStack with local AI models (Ollama, LM Studio, vLLM) and free AI agents (AutoGen, Flowise, OpenHands, Aider) for a completely self-hosted AI development environment with comprehensive monitoring, optimization, and production applications.

## 📋 System Requirements

- **CPU:** 4+ cores recommended
- **RAM:** 8GB+ (16GB recommended)  
- **Storage:** 50GB+ free disk space
- **GPU:** Optional but recommended (4GB+ VRAM)
- **OS:** Linux, macOS, or Windows with WSL2
- **Docker:** Required for containerized services

## 🤖 Auto Submit Functionality

NEW: Automated bug reporting and merge request creation based on audit findings.

### Quick Auto Submit
```bash
# Set GitHub token
export GITHUB_TOKEN=your_github_token

# Run full automation (audits + bug reports + merge requests)
./auto_submit.sh auto

# Or preview what would be done
./auto_submit.sh dry-run
```

### Auto Submit Options
```bash
# Submit bugs from audit findings
python3 auto_submit.py bugs --type all

# Create merge requests for fixes
python3 auto_submit.py merges --type shell

# Full automation workflow
python3 auto_submit.py auto
```

See [AUTO_SUBMIT_README.md](AUTO_SUBMIT_README.md) for detailed documentation.

## 🚀 Quick Start

### One-Command Deployment
```bash
bash deploy.sh
```

### Manual Step-by-Step Deployment

#### Phase 1: System Check
```bash
bash scripts/check_system.sh
```

#### Phase 2: Install Local Model Servers
```bash
bash scripts/install_ollama.sh
bash scripts/install_lm_studio.sh
bash scripts/setup_vllm.sh
```

#### Phase 3: Deploy LLMStack
```bash
bash scripts/deploy_llmstack.sh
```

#### Phase 4: Install AI Agents
```bash
bash scripts/install_agents.sh
bash scripts/install_continue.sh
bash scripts/install_jan.sh
bash scripts/setup_copilot_agents.sh
```

#### Phase 5: Setup Monitoring & Optimization
```bash
bash scripts/setup_monitoring.sh
bash scripts/optimize_system.sh
```

#### Phase 6: Validate & Benchmark
```bash
bash scripts/validate_deployment.sh
python3 scripts/benchmark_system.py
```

## 🤖 GitHub Copilot Agents

GitHub Copilot has been configured with specialized knowledge for this repository's AI agent infrastructure.

### Quick Setup
```bash
# Setup Copilot agents integration
bash scripts/setup_copilot_agents.sh

# Restart VS Code to apply settings
```

### Features
- **AI Agent Patterns**: Code completion tailored for AutoGen, Flowise, and other agents
- **Docker Integration**: Smart suggestions for service deployment
- **Configuration Help**: Auto-completion for AI model configurations
- **Best Practices**: Automatically suggests error handling and logging patterns

### Documentation
- [Complete Copilot Agents Guide](docs/COPILOT_AGENTS_GUIDE.md)
- [AI Agent Health Monitoring](docs/AI_AGENT_HEALTH_MONITORING.md)
- [GitHub Copilot Configuration](.github/copilot.yml)
- [VS Code Settings](.vscode/settings.json)

## 🧠 Available AI Components

### Local Model Servers
- **Ollama** - Local model inference (Llama, Mistral, CodeLlama)
- **LM Studio** - User-friendly model management
- **vLLM** - High-performance GPU inference

### AI Agents & Tools
- **AutoGen** - Multi-agent conversations with enhanced health monitoring
- **Flowise** - Visual AI workflow builder  
- **OpenHands** - AI coding assistant
- **Aider** - AI pair programming
- **Continue** - VS Code AI extension
- **Jan** - Desktop AI assistant
- **GitHub Copilot** - Enhanced code completion with AI agent patterns
- **Enhanced Health Monitoring** - Comprehensive agent status tracking and logging

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
├── deploy.sh                  # One-command deployment
├── scripts/                   # Deployment scripts
│   ├── check_system.sh       # System requirements check
│   ├── install_ollama.sh     # Ollama installation
│   ├── install_lm_studio.sh  # LM Studio installation
│   ├── setup_vllm.sh         # vLLM setup
│   ├── deploy_llmstack.sh    # LLMStack deployment
│   ├── install_agents.sh     # AI agents installation
│   ├── install_continue.sh   # VS Code Continue extension
│   ├── install_jan.sh        # Jan desktop app
│   ├── setup_copilot_agents.sh # GitHub Copilot agents setup
│   ├── configure_providers.py # Provider configuration
│   ├── setup_monitoring.sh   # Monitoring stack
│   ├── optimize_system.sh    # System optimization
│   ├── benchmark_system.py   # Performance benchmarking
│   ├── manage_services.sh    # Service management
│   ├── troubleshoot.sh       # Troubleshooting tool
│   ├── validate_deployment.sh # Deployment validation
│   └── orchestrator.py       # Agent orchestration
├── apps/                     # Production applications
│   ├── rag_chatbot.json     # RAG chatbot configuration
│   └── code_pipeline.sh     # Code generation pipeline
├── llmstack/                 # LLMStack examples and configs
├── ai-tools/                 # Additional AI tools
├── requirements.txt          # Python dependencies
└── README.md                 # This file
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

### Main Applications
- **LLMStack UI:** http://localhost:3000
- **Flowise:** http://localhost:3001  
- **OpenHands:** http://localhost:3002

### Monitoring & Management
- **Grafana:** http://localhost:3003 (admin/admin)
- **Prometheus:** http://localhost:9090

### API Endpoints  
- **Ollama API:** http://localhost:11434/v1
- **LM Studio API:** http://localhost:1234/v1
- **vLLM API:** http://localhost:8000/v1
- **Jan API:** http://localhost:1337/v1

## 📊 Cost Breakdown

| Component | Cost | Alternative |
|-----------|------|-------------|
| LLMStack | $0 (Open Source) | Langflow ($99/mo) |
| Local Models | $0 (Self-hosted) | OpenAI GPT-4 ($20/mo) |
| AutoGen | $0 (Open Source) | AgentGPT ($30/mo) |
| Flowise | $0 (Open Source) | Zapier ($20/mo) |
| **Total** | **$0/month** | **$169/month** |

## 🛠️ Management Commands

### Service Management
```bash
# Start all services
bash scripts/manage_services.sh start

# Stop all services  
bash scripts/manage_services.sh stop

# Check service status
bash scripts/manage_services.sh status

# View service logs
bash scripts/manage_services.sh logs
```

### Performance & Optimization
```bash
# Run performance benchmark
python3 scripts/benchmark_system.py

# Optimize system settings
bash scripts/optimize_system.sh

# Configure providers (after getting admin token from LLMStack UI)
python3 scripts/configure_providers.py <admin_token>
```

### Troubleshooting
```bash
# Interactive troubleshooting tool
bash scripts/troubleshoot.sh

# Common fixes
docker system prune -a          # Clean up Docker
ollama rm unused_model          # Remove unused models
bash scripts/optimize_system.sh # Apply optimizations
```

### Production Applications
```bash
# Generate code project
bash apps/code_pipeline.sh "my-app" "Create a FastAPI web service"

# RAG chatbot configuration available in apps/rag_chatbot.json
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