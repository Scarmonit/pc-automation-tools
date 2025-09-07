# GitHub Copilot Instructions for PC Automation Tools

## Repository Context

This repository contains comprehensive PC automation tools designed for AI assistants, with a focus on LLM stack deployment and AI agent orchestration.

## Key Components

### Core Automation Modules
- `github_automation.py` - Automated GitHub issue and PR management
- `merge_automation.py` - Automated merge request creation and code fixes
- `security_fix.py` - Automated security vulnerability remediation
- `test_automation.py` - Comprehensive test automation framework

### AI Agent Infrastructure
- **AutoGen**: Multi-agent conversation framework (`llmstack/examples/04_autogen_agents.py`)
- **Flowise**: Visual flow-based LLM app builder
- **OpenHands**: Autonomous coding assistant integration
- **Aider**: AI pair programming assistant configuration

### LLM Stack Components
- **Ollama**: Local LLM hosting and management
- **vLLM**: High-performance LLM inference server
- **LM Studio**: Desktop LLM interface
- **Jan**: Open-source ChatGPT alternative

## Coding Guidelines

### Python Code Style
- Use type hints for all function parameters and returns
- Follow dataclass patterns for structured data (see `BugReport`, `MergeRequest`)
- Implement comprehensive error handling with logging
- Use pathlib for file operations
- Follow the existing logging configuration pattern

### Shell Script Standards
- Always include `set -e` for error handling
- Use meaningful variable names with uppercase conventions
- Add comprehensive comments for complex operations
- Implement graceful error handling for optional dependencies

### AI Agent Integration
- When working with AutoGen agents, use the established llm_config pattern
- Implement proper agent role separation (security, performance, clean code reviewers)
- Use GroupChat for multi-agent coordination
- Follow the existing system message patterns for consistent agent behavior

### Security Best Practices
- Never hardcode credentials - use environment variables
- Implement input validation for all user-facing functions
- Use secure defaults for all configurations
- Follow the security checklist patterns in the codebase

### API Integration Patterns
- Use the GitHubAPI class pattern for external service integration
- Implement proper request/response handling with error retries
- Follow the dataclass pattern for API request/response modeling
- Use environment variable configuration for API endpoints

## AI Assistant Context

When suggesting code improvements:
1. Consider the multi-agent architecture already in place
2. Align with existing automation workflows
3. Leverage the established LLM stack components
4. Maintain compatibility with both local and cloud LLM deployments
5. Follow the repository's focus on autonomous operation

## Testing Approach

- Use the established test automation framework in `test_automation.py`
- Follow the unittest pattern for new test classes
- Use temporary files for testing file operations
- Implement proper cleanup in test teardown
- Test both success and error conditions

## Documentation Standards

- Update README.md for user-facing changes
- Maintain inline documentation for complex algorithms
- Use docstrings for all public methods following the existing pattern
- Include usage examples in docstrings where appropriate
