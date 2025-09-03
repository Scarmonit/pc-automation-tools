# AI Swarm Intelligence System 🤖🐝

A powerful multi-agent AI system featuring distributed intelligence, autonomous coordination, and cloud-native deployment capabilities.

## 🌟 Features

- **Multi-Agent Coordination**: 8 specialized AI agents working in harmony
- **Distributed Memory**: Persistent knowledge base with SQLite/Cosmos DB
- **Cloud-Native**: Full Azure deployment with Kubernetes orchestration
- **API Integration**: Support for Anthropic, OpenAI, and Perplexity models
- **Autonomous Execution**: Self-organizing swarm intelligence
- **Scalable Architecture**: Auto-scaling from local to global deployment

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│                 Queen Agent                      │
│            (Master Coordinator)                  │
└─────────────┬───────────────────────────────────┘
              │
    ┌─────────┴─────────┬─────────┬─────────┐
    │                   │         │         │
┌───▼───┐  ┌───────┐  ┌─▼───┐  ┌─▼───┐  ┌─▼───┐
│Architect│ │ Coder │  │Tester│  │Analyst│ │Security│
└────────┘  └───────┘  └──────┘  └───────┘ └────────┘
           ┌────────┐  ┌──────────┐  ┌─────────┐
           │Researcher│ │ Optimizer │ │ Memory DB│
           └──────────┘ └───────────┘ └─────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker (optional, for containerized deployment)
- Azure CLI (optional, for cloud deployment)
- API Keys: Anthropic, OpenAI, or Perplexity

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Scarmonit/claude-powered-repo.git
cd claude-powered-repo
```

2. **Set up environment**
```bash
# Copy environment template
cp swarm-intelligence/config/.env.template swarm-intelligence/config/.env

# Edit .env with your API keys
nano swarm-intelligence/config/.env
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the swarm**
```bash
python scripts/run_swarm_standalone.py
```

## 📦 Project Structure

```
claude-powered-repo/
├── swarm-intelligence/          # Core swarm system
│   ├── core/                   # Python modules
│   ├── config/                 # Configuration files
│   └── docs/                   # Swarm documentation
├── azure-deploy/               # Azure deployment configs
│   ├── docker/                 # Dockerfiles
│   ├── kubernetes/             # K8s manifests
│   └── build-and-push.sh      # Container build script
├── scripts/                    # Utility scripts
│   ├── setup/                  # Setup scripts
│   └── maintenance/            # Maintenance tools
└── docs/                      # Project documentation
```

## 🐝 Agent Types

| Agent | Role | Capabilities |
|-------|------|-------------|
| **Queen** | Master Coordinator | Strategy, task delegation, consensus |
| **Architect** | System Designer | Architecture, planning, design patterns |
| **Coder** | Implementation | Code generation, debugging, refactoring |
| **Tester** | Quality Assurance | Unit tests, integration tests, validation |
| **Researcher** | Information Gathering | Web search, documentation, analysis |
| **Analyst** | Data Analysis | Performance metrics, insights, reporting |
| **Security** | Security Expert | Vulnerability assessment, best practices |
| **Optimizer** | Performance Tuning | Resource optimization, efficiency |

## ☁️ Cloud Deployment (Azure)

### Quick Azure Setup

1. **Run setup script**
```bash
cd azure-config
./azure-setup.sh
```

2. **Build and push containers**
```bash
./azure-deploy/build-and-push.sh
```

3. **Deploy to Kubernetes**
```bash
kubectl apply -f azure-deploy/kubernetes/
```

See [Azure Deployment Guide](docs/AZURE_SWARM_DEPLOYMENT.md) for detailed instructions.

## 🧪 Local Development

### Docker Compose

```bash
cd azure-deploy
docker-compose up -d
```

### Testing

```bash
# Run swarm demo
python scripts/swarm_demo.py

# Test swarm configuration
python scripts/test_swarm.py
```

## 📚 Documentation

- [Claude Integration Guide](docs/CLAUDE.md)
- [Azure Deployment Guide](docs/AZURE_SWARM_DEPLOYMENT.md)
- [Swarm Setup Guide](swarm-intelligence/docs/SWARM_SETUP_README.md)

## 🔧 Configuration

### API Keys

Add your API keys to `swarm-intelligence/config/.env`:

```env
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY
OPENAI_API_KEY=sk-proj-YOUR-KEY
PERPLEXITY_API_KEY=pplx-YOUR-KEY
```

### Swarm Settings

Edit `swarm-intelligence/config/swarm_config.json`:

```json
{
  "swarm_settings": {
    "max_agents": 10,
    "queen_agent_type": "strategic",
    "collaboration_enabled": true
  }
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Claude AI assistance
- Powered by Anthropic, OpenAI, and Perplexity APIs
- Deployed on Microsoft Azure

## 📞 Contact

- GitHub: [@Scarmonit](https://github.com/Scarmonit)
- Repository: [claude-powered-repo](https://github.com/Scarmonit/claude-powered-repo)

---

**Note**: Remember to keep your API keys secure and never commit them to version control!