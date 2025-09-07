# Claude Code Project Context - AI Platform

## Project Overview
This is a comprehensive AI platform that integrates multiple AI services, security tools, automation frameworks, and model management capabilities. The platform serves as a unified interface for various AI operations including web scanning, API security testing, swarm intelligence, and distributed agent systems.

## Key Architecture Components

### Core Modules
- **Core AI Platform** (`src/core/`): MCP support, autonomous and enhanced AI modes
- **Security Suite** (`src/security/`): Web vulnerability scanner, API security testing, stealth scanning
- **Dolphin Models** (`src/dolphin/`): Custom Ollama model management with GUI
- **Automation** (`src/automation/`): Swarm intelligence, distributed agents, AutoGPT integration
- **Database Layer** (`src/database/`): Unified database system with sync capabilities
- **Monitoring** (`src/monitoring/`): Health checks and alerting system
- **Integrations** (`src/integrations/`): 18+ external service integrations

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use type hints for all function signatures
- Implement comprehensive error handling with the existing `error_handling.py` module
- Document all classes and functions with docstrings
- Maintain modular architecture - each feature should be self-contained

### Testing Requirements
- Write unit tests for all new features in `src/tests/`
- Run tests before committing: `python -m pytest`
- Maintain test coverage above 80%
- Test security features in isolated environments only

### Security Practices
- NEVER commit API keys or secrets to the repository
- All sensitive data must be in `.env` files
- Use environment variables for all API keys and credentials
- Implement rate limiting for API endpoints
- Sanitize all user inputs
- Run security scanners only with explicit permission

## Common Commands

### Development Workflow
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run main application
python main.py list  # List all modules
python main.py core  # Run core AI platform

# Run tests
python -m pytest
python -m pytest --cov=src  # With coverage

# Format code
black src/
flake8 src/
```

### Module-Specific Commands
```bash
# Security operations
python main.py security --action webscan
python parallel_security_orchestrator.py

# Dolphin GUI
python main.py dolphin --action gui

# Automation
python main.py automation --action swarm

# Quick demos
python quick_security_demo.py
python signalr_quick_demo.py
```

## Environment Variables Required
The following environment variables must be set in `.env`:
- `OPENAI_API_KEY`: OpenAI API access
- `ANTHROPIC_API_KEY`: Claude API access
- `PERPLEXITY_API_KEY`: Perplexity AI access
- `GOOGLE_API_KEY`: Google services
- `XAI_API_KEY`: X.AI (Grok) access
- `MISTRAL_API_KEY`: Mistral AI access
- `OPENROUTER_API_KEY`: OpenRouter access
- `AZURE_OPENAI_API_KEY`: Azure OpenAI services
- `OLLAMA_API_KEY`: Local Ollama models

## Project Dependencies

### Core Technologies
- Python 3.8+
- Node.js 18+ (for MCP support)
- Docker & Docker Compose
- Redis (for caching/queuing)
- PostgreSQL (for persistent storage)

### Key Python Libraries
- FastAPI/Flask for API endpoints
- SQLAlchemy for database ORM
- Celery for task queuing
- pytest for testing
- Various AI SDKs (openai, anthropic, etc.)

## File Structure Notes

### Important Files
- `main.py`: Unified entry point for all modules
- `system_config.py`: Central configuration management
- `error_handling.py`: Global error handling utilities
- `optimize_ai_speed.py`: AI performance optimization
- `parallel_security_orchestrator.py`: Distributed security scanning

### Configuration
- `.env`: Environment variables (never commit)
- `config/`: Module-specific configurations
- `configs/`: Additional configuration files
- `.alpha/`: Alpha features and experimental code

### MCP Integration
- `mcp_config/`: MCP server configurations
- `mcp-memory-service/`: Memory service for MCP
- `claude-memory-mcp/`: Claude-specific memory integration

## Current Development Focus

### Active Areas
1. Enhancing MCP integration for better AI agent coordination
2. Improving security scanning performance and stealth
3. Expanding Dolphin model capabilities
4. Optimizing parallel processing for security operations
5. Implementing comprehensive monitoring dashboards

### Known Issues
- Document any current bugs or limitations here as discovered
- Track feature requests and improvements

## Testing Guidelines

### Test Categories
1. **Unit Tests**: Individual function/class testing
2. **Integration Tests**: Module interaction testing
3. **Security Tests**: Vulnerability and penetration testing
4. **Performance Tests**: Load and stress testing

### Test Execution
```bash
# Run specific test categories
python -m pytest src/tests/test_security.py
python -m pytest src/tests/test_dolphin.py
python -m pytest src/tests/test_automation.py
```

## Deployment Notes

### Docker Deployment
```bash
# Build and deploy all services
docker-compose up -d

# Deploy specific services
docker-compose up ai-platform redis postgres

# View logs
docker-compose logs -f ai-platform
```

### Production Considerations
- Use environment-specific `.env` files
- Enable SSL/TLS for all external communications
- Implement proper logging and monitoring
- Set up automated backups for databases
- Configure rate limiting and DDoS protection

## Contributing Guidelines

### Code Submission Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Run full test suite
4. Update documentation if needed
5. Submit PR with detailed description

### PR Requirements
- All tests must pass
- Code coverage maintained or improved
- Documentation updated for new features
- Security review for sensitive changes
- Performance impact assessed

## Support and Resources

### Documentation
- API Reference: `docs/api_reference.md`
- Configuration Guide: `docs/configuration.md`
- Deployment Guide: `docs/deployment.md`
- Development Guide: `docs/development.md`

### Getting Help
- Check existing documentation in `docs/`
- Review test files for usage examples
- Create GitHub issues for bugs
- Start discussions for feature requests

## Security Warnings

⚠️ **IMPORTANT SECURITY NOTES**:
- This platform includes security scanning tools - use responsibly
- Never run security scans without explicit permission
- Test security features only in authorized environments
- Report security vulnerabilities privately
- Follow responsible disclosure practices

## Performance Optimization Tips

### AI Model Optimization
- Use `optimize_ai_speed.py` for performance tuning
- Implement caching for repeated queries
- Use batch processing where possible
- Monitor token usage and costs

### System Optimization
- Use Redis for caching frequently accessed data
- Implement connection pooling for databases
- Use async operations for I/O-bound tasks
- Profile code to identify bottlenecks

---

**Last Updated**: September 2025
**Maintainer**: Project Team
**Repository**: https://github.com/Scarmonit/pc-automation-tools.git