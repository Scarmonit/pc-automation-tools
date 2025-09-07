# AI Platform - Consolidated Project Structure

## Overview
This project has been reorganized from 100+ individual scripts into a unified, modular architecture.

## Directory Structure

```
ai_platform/
├── main.py                 # Unified entry point
├── src/
│   ├── core/              # Core AI platform functionality
│   │   ├── ai_platform.py
│   │   ├── ai_platform_mcp_autonomous.py
│   │   └── ai_platform_mcp_enhanced.py
│   │
│   ├── security/          # Security scanning and analysis
│   │   ├── web_api_scanner.py
│   │   ├── ultimate_security_scanner.py
│   │   ├── stealth_web_scanner.py
│   │   └── [14 total security modules]
│   │
│   ├── dolphin/           # Dolphin model management
│   │   ├── dolphin_gui.py
│   │   ├── setup_ollama_dolphin.py
│   │   ├── *.modelfile files
│   │   └── [11 total dolphin modules]
│   │
│   ├── automation/        # Swarm and automation
│   │   ├── master_ai_swarm_intelligence.py
│   │   ├── distributed_agent_swarm.py
│   │   ├── autogpt_integration.py
│   │   └── [13 total automation modules]
│   │
│   ├── database/          # Database management
│   │   ├── unified_database_system.py
│   │   ├── database_sync_layer.py
│   │   └── [6 total database modules]
│   │
│   ├── monitoring/        # Health and alerts
│   │   ├── health_monitor.py
│   │   └── monitoring_alerts.py
│   │
│   ├── integrations/      # Service integrations
│   │   ├── integrate_anaconda.py
│   │   ├── integrate_bayesian_networks.py
│   │   └── [18 total integration modules]
│   │
│   ├── infrastructure/    # Docker, deployment configs
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile
│   │   └── [deployment configurations]
│   │
│   ├── utils/            # Utility modules
│   └── tests/            # Test suite
│
├── docs/                 # Documentation
├── config/               # Configuration files
├── scripts/              # Batch/PowerShell scripts
└── data/                 # Data storage

```

## Usage

### Main Entry Point
```bash
# List all available modules
python main.py list

# Run core AI platform
python main.py core

# Run security scanner
python main.py security --action webscan

# Launch Dolphin GUI
python main.py dolphin --action gui

# Start swarm intelligence
python main.py automation --action swarm

# Start monitoring
python main.py monitoring
```

### Module-Specific Usage

#### Security Module
```bash
python main.py security --action webscan    # Web scanner
python main.py security --action apiscan    # API scanner
```

#### Dolphin Module
```bash
python main.py dolphin --action setup       # Setup Dolphin
python main.py dolphin --action gui         # Launch GUI
```

#### Automation Module
```bash
python main.py automation --action swarm    # Swarm intelligence
```

## Key Components

### Core (3 modules)
- Main AI platform functionality
- MCP autonomous operations
- Enhanced MCP features

### Security (14 modules)
- Web scanning
- API scanning
- Pattern detection
- Stealth operations
- Deep crawling

### Dolphin (11 modules)
- Model management
- GUI interface
- Multiple model configurations
- Enhancement tools

### Automation (13 modules)
- Swarm intelligence
- Distributed agents
- AutoGPT integration
- Test automation

### Database (6 modules)
- Unified database system
- Connection pooling
- Sync layers
- Migration tools

### Integrations (18 modules)
- Anaconda
- Bayesian networks
- CI/CD automation
- Network access
- And many more...

## Benefits of Consolidation

1. **Single Entry Point**: All functionality accessible through `main.py`
2. **Organized Structure**: Clear separation of concerns
3. **Modular Design**: Easy to maintain and extend
4. **Reduced Clutter**: From 100+ files in root to organized modules
5. **Better Discovery**: Easy to find and understand components

## Next Steps

1. Add proper dependency management (requirements.txt per module)
2. Implement unit tests for each module
3. Create API documentation
4. Add configuration management system
5. Implement logging framework