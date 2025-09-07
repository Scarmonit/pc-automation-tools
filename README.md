# AI Platform

A comprehensive, modular AI platform combining multiple AI services, security tools, automation frameworks, and model management capabilities.

## 🚀 Features

- **Core AI Platform**: Multiple AI model integrations and MCP support
- **Security Suite**: Web scanning, API security testing, pattern detection
- **Dolphin Models**: Custom Ollama model management with GUI
- **Automation**: Swarm intelligence, distributed agents, AutoGPT integration
- **Database Layer**: Unified database system with sync capabilities
- **Monitoring**: Health checks and alerting system
- **18+ Integrations**: Anaconda, Bayesian networks, CI/CD, and more

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-platform.git
cd ai-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Quick Start

```bash
# List all available modules
python main.py list

# Run the core AI platform
python main.py core

# Launch security scanner
python main.py security --action webscan

# Start Dolphin GUI
python main.py dolphin --action gui

# Run automation swarm
python main.py automation --action swarm
```

## 📁 Project Structure

```
ai_platform/
├── main.py                 # Unified entry point
├── src/
│   ├── core/              # Core AI functionality
│   ├── security/          # Security tools
│   ├── dolphin/           # Dolphin model management
│   ├── automation/        # Automation and swarm tools
│   ├── database/          # Database management
│   ├── monitoring/        # Health monitoring
│   ├── integrations/      # External service integrations
│   ├── infrastructure/    # Docker and deployment
│   ├── utils/            # Utilities
│   └── tests/            # Test suite
├── docs/                 # Documentation
├── config/               # Configuration files
└── scripts/              # Helper scripts
```

## 🔧 Configuration

1. Copy `.env.example` to `.env`
2. Add your API keys and configuration:

```bash
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
# ... other API keys
```

## 🐳 Docker Support

```bash
# Build and run with Docker
docker-compose up -d

# Run specific services
docker-compose up ai-platform redis postgres
```

## 📚 Modules

### Core
- Main AI platform with MCP support
- Autonomous and enhanced modes

### Security
- Web vulnerability scanner
- API security testing
- Stealth scanning capabilities
- Pattern detection engine

### Dolphin
- Custom Ollama model management
- Interactive GUI
- Multiple model configurations
- Model enhancement tools

### Automation
- Swarm intelligence framework
- Distributed agent system
- AutoGPT integration
- Test automation

### Database
- Unified database abstraction
- Connection pooling
- Synchronization layers
- Migration tools

### Integrations
18+ integrations including:
- Anaconda environments
- Bayesian networks
- CI/CD automation
- Network access tools
- And many more...

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run specific module tests
python -m pytest src/tests/test_security.py

# Run with coverage
python -m pytest --cov=src
```

## 📖 Documentation

See the `docs/` directory for detailed documentation:
- [API Reference](docs/api_reference.md)
- [Configuration Guide](docs/configuration.md)
- [Deployment Guide](docs/deployment.md)
- [Development Guide](docs/development.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude
- Ollama for local model support
- All contributors and maintainers

## 📞 Support

- Create an issue for bug reports
- Start a discussion for feature requests
- Check existing documentation in `docs/`

## ⚠️ Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Report security issues privately

---

**Note**: This project consolidates multiple AI tools and services. Ensure you have appropriate API keys and permissions for the services you intend to use.