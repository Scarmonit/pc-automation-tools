# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Windows development environment with multiple AI-powered development tools and integrations, including Task Master AI, MCP servers, and various automation scripts.

## Common Development Commands

### Task Master AI (if installed in claude-code-tools)
```bash
# Initialize and manage tasks
cd claude-code-tools/claude-task-master
task-master init                      # Initialize Task Master
task-master list                      # Show all tasks
task-master next                      # Get next available task
task-master show <id>                 # View task details
task-master set-status --id=<id> --status=done  # Complete task
```

### Git Operations
```bash
# Git operations (repository is initialized)
git status                            # Check repository status
git add .                             # Stage changes
git commit -m "message"              # Commit changes
git log --oneline -10                # View recent commits
```

### Python Environment
```bash
# Python is available (Python 3.12)
python --version                      # Check Python version
pip install <package>                # Install Python packages
python script.py                     # Run Python scripts
```

### Node.js/NPM (if available)
```bash
# For Node.js projects
npm install                          # Install dependencies
npm run dev                          # Run development server
npm test                            # Run tests
```

### AI Swarm Intelligence
```bash
# Setup and launch swarm
setup_swarm_env.bat                  # Configure environment and API keys
start_swarm.bat                      # Launch swarm with menu options
python .claude/swarm-intelligence/launch_global_swarm.py  # Direct launch

# Swarm capabilities when active:
# - Queen Agent: Master coordinator
# - Architect: System design and planning
# - Coder: Implementation specialist
# - Tester: Quality assurance
# - Researcher: Information gathering
# - Analyst: Data analysis
# - Security: Vulnerability assessment
# - Optimizer: Performance tuning
```

## High-Level Architecture

### Directory Structure
```
C:\Users\scarm\
├── .claude/                         # Claude Code configuration
│   ├── claude_desktop_config.json  # MCP server configurations
│   ├── settings.local.json         # Local Claude settings and permissions
│   ├── swarm-intelligence/         # AI swarm orchestration
│   └── todos/                      # Task tracking
├── AI-Platform/                    # AI platform data and logs
├── claude-code-tools/             
│   └── claude-task-master/        # Task Master AI installation
├── ai-prompts-collection/         # AI prompts and templates
├── claude-ultimate-power.sh       # Unix/WSL AI tools setup script
├── claude-ultimate-power-windows.sh # Windows AI tools setup script
└── launch_swarm.bat               # Launch swarm intelligence
```

### Configuration Files

#### MCP Server Configuration (.claude/claude_desktop_config.json)
- **perplexity-search**: Perplexity API integration for search
- **ai-platform**: Local AI platform integration (localhost:8000)
- **filesystem**: File system access for Desktop, Downloads, Documents

#### Permissions (.claude/settings.local.json)
Configured with broad permissions including:
- Bash script execution (claude-ultimate-power scripts)
- Python and command execution
- Web search and fetch capabilities
- Git operations
- Package installations (npm, pip)

### Key Integration Points

1. **Task Master AI Integration**
   - Located in `claude-code-tools/claude-task-master/`
   - Provides task management and AI-driven development workflow
   - MCP server available for Claude Code integration

2. **AI Platform**
   - Running on localhost:8000 (main) and localhost:8001 (Tidy Assistant)
   - Data stored in `AI-Platform/data/`
   - Logs available in `AI-Platform/logs/`

3. **Swarm Intelligence**
   - Orchestration scripts in `.claude/swarm-intelligence/`
   - Launched via `start_swarm.bat` or `launch_swarm.bat`
   - Multi-agent coordination system with specialized agents
   - Distributed memory using SQLite database

## Development Workflow

### Starting a New Feature
1. If using Task Master: `task-master next` to get next task
2. Review requirements and existing code
3. Implement changes
4. Test implementation
5. Commit changes with descriptive message

### Running Scripts
- Windows batch files: Use `cmd /c script.bat` or directly `script.bat`
- Shell scripts: Use Git Bash or WSL: `bash script.sh`
- Python scripts: `python script.py`

### Testing
Check project-specific test commands in:
- `package.json` for Node.js projects (npm test)
- `setup.py` or `pyproject.toml` for Python projects
- Task Master tasks for test requirements

## Security Notes
- API keys are stored in `.claude/claude_desktop_config.json` - handle with care
- The `.claude/settings.local.json` contains broad permissions
- Git operations should not commit sensitive data

## Platform-Specific Considerations

### Windows Environment
- Using Git Bash for Unix-like commands
- Path separator is backslash (`\`) in Windows paths
- Some scripts may require WSL or Git Bash to run properly
- File permissions may differ from Unix systems

### Available Tools
- Git (via Git Bash)
- Python 3.12
- Node.js/npm (check availability)
- Windows PowerShell and CMD
- WSL (if configured)

## Troubleshooting

### Common Issues
1. **Script execution fails**: Check if running in correct shell (Git Bash vs CMD)
2. **Permission denied**: May need to run as administrator or check file permissions
3. **Module not found**: Install required dependencies with pip or npm
4. **Git issues**: Ensure you're in the repository root directory

### Swarm Intelligence Issues
1. **API key errors**: Copy `.env.template` to `.env` in `.claude/swarm-intelligence/` and add your keys
2. **MCP connection failed**: Restart Claude Desktop after updating `claude_desktop_config.json`
3. **Port 8000 not available**: Ensure AI Platform is running or check for port conflicts
4. **Python module errors**: Run `setup_swarm_env.bat` to install dependencies

### Getting Help
- Check existing documentation in project directories
- Review Task Master tasks if available
- Examine configuration files for setup details
- Swarm logs available in `.claude/swarm-intelligence/logs/`