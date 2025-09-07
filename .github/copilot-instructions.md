# GitHub Copilot Instructions for PC Automation Tools

## Repository Context
This is a comprehensive PC automation tools repository with extensive AI agent infrastructure. The codebase includes local AI model servers, multi-agent systems, and automation workflows.

## Key Technologies & Frameworks
- **AI Agents**: AutoGen, Flowise, OpenHands, Aider, CAMEL
- **Local AI Models**: Ollama, LM Studio, vLLM
- **Languages**: Python (primary), Shell scripts, PowerShell
- **Orchestration**: Docker, Docker Compose
- **Monitoring**: Prometheus, Grafana

## Code Style & Patterns

### Python Code
- Use type hints consistently
- Follow PEP 8 style guidelines
- Prefer async/await for I/O operations
- Use dataclasses for configuration objects
- Include comprehensive docstrings for classes and functions

### Agent Development
- Use the existing `AIConfig` dataclass for agent configuration
- Follow the pattern in `llmstack/ai_frameworks_integration.py` for new agents
- Include proper error handling and logging for agent interactions
- Use the unified orchestrator pattern when creating multi-agent workflows

### Shell Scripts
- Include proper error handling with `set -e`
- Use descriptive comments for complex operations
- Follow the pattern in `scripts/install_agents.sh` for new installations
- Include validation checks before performing operations

## Common Patterns

### Agent Configuration
```python
@dataclass
class AIConfig:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "sk-localai")
    localai_endpoint: str = "http://localhost:8080/v1"
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2048
    use_local: bool = True
```

### AutoGen Agent Setup
```python
llm_config = {
    "config_list": [
        {
            "model": "llama3.2",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",
            "api_type": "openai"
        }
    ],
    "temperature": 0.7,
    "timeout": 120
}
```

### Service Deployment
```bash
docker run -d \
  --name service_name \
  -p port:port \
  -v volume_path:/container_path \
  --restart unless-stopped \
  image_name
```

## File Structure Conventions
- Agent implementations go in `llmstack/`
- Installation scripts go in `scripts/`
- Configuration files use consistent naming (e.g., `service_config.json`)
- Documentation follows the established format with emoji headers

## Integration Guidelines
- All agents should integrate with the unified orchestrator
- Use the existing logging patterns from `ai_frameworks_integration.py`
- Include health checks for new services
- Follow the monitoring patterns for new components

## Testing Approach
- Include validation scripts for new features
- Use the existing test patterns in `test_automation.py`
- Verify agent responses with sample prompts
- Include integration tests with the broader AI stack

## Documentation Standards
- Use clear, action-oriented headers with emojis
- Include both quick start and detailed setup instructions
- Provide troubleshooting sections for complex installations
- Include example code and configuration snippets

When suggesting code, prioritize compatibility with the existing infrastructure and follow the established patterns for agent development and service deployment.
