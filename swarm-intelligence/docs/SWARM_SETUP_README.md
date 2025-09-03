# AI Swarm Intelligence Setup Guide

## Quick Start

Your AI Swarm Intelligence system is now configured and ready to use!

### 1. Configure API Keys

**IMPORTANT**: You need to add your API keys before the swarm can function.

1. Navigate to `.claude\swarm-intelligence\`
2. Copy `.env.template` to `.env`
3. Edit `.env` and add at least one API key:
   - `ANTHROPIC_API_KEY` (recommended for Claude models)
   - `OPENAI_API_KEY` (for GPT models)
   - `PERPLEXITY_API_KEY` (for research capabilities)

### 2. Launch the Swarm

Three ways to start the swarm:

#### Option A: Interactive Menu (Recommended)
```bash
start_swarm.bat
```
This provides a menu to choose between:
- Standard Swarm mode
- MCP Server mode (for Claude Desktop)
- Debug mode

#### Option B: Direct Launch
```bash
python .claude/swarm-intelligence/launch_global_swarm.py
```

#### Option C: Quick Launch
```bash
launch_swarm.bat
```

### 3. Claude Desktop Integration (Optional)

The swarm MCP server has been added to your Claude Desktop configuration. To activate:

1. Edit `.claude/claude_desktop_config.json`
2. Replace `YOUR-ANTHROPIC-KEY-HERE` with your actual API key
3. Restart Claude Desktop
4. The swarm tools will be available in Claude Desktop

### Available Swarm Agents

When the swarm is active, you have access to:

- **Queen Agent**: Master coordinator for complex tasks
- **Architect**: System design and architecture planning
- **Coder**: Code implementation specialist
- **Tester**: Quality assurance and testing
- **Researcher**: Information gathering and analysis
- **Analyst**: Data analysis and insights
- **Security**: Security assessment and vulnerability detection
- **Optimizer**: Performance optimization

### Swarm Tools (When Active)

- `swarm_execute` - Execute complex multi-agent tasks
- `swarm_status` - Monitor swarm status in real-time
- `agent_collaborate` - Direct agent collaboration
- `swarm_memory_store` - Store information in distributed memory
- `swarm_memory_retrieve` - Retrieve stored intelligence

### Files Created

1. **start_swarm.bat** - Interactive swarm launcher with menu
2. **setup_swarm_env.bat** - Environment setup and dependency installer
3. **.env.template** - API key configuration template
4. **SWARM_SETUP_README.md** - This guide
5. Updated **CLAUDE.md** with swarm commands
6. Updated **claude_desktop_config.json** with swarm MCP server

### Troubleshooting

#### API Key Issues
- Make sure you've copied `.env.template` to `.env` in `.claude/swarm-intelligence/`
- Add your actual API keys to the `.env` file
- At least one AI provider key is required

#### Port Issues
- The AI Platform should be running on port 8000
- Check with: `netstat -an | findstr 8000`
- If not running, the swarm will have limited functionality

#### Python Module Errors
- Run `setup_swarm_env.bat` to install all dependencies
- Or manually install: `pip install mcp aiohttp anthropic`

#### MCP Connection Failed
- Restart Claude Desktop after updating configuration
- Check that Python path is correct in config
- Verify API keys are set correctly

### Configuration Files

- **swarm_config.json** - Agent types, priorities, and collaboration rules
- **prompts_config.json** - Specialized prompts for different agent types
- **swarm_memory.db** - SQLite database for distributed memory

### Next Steps

1. Add your API keys to `.env`
2. Run `start_swarm.bat` and select option 1
3. The swarm will initialize and be ready for complex tasks
4. For Claude Desktop integration, update the config with your API key and restart

The swarm intelligence system provides powerful multi-agent coordination for complex development tasks. Each agent specializes in different aspects of software development, working together under the Queen agent's coordination.