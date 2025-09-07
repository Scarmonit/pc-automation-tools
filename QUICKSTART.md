# 🚀 AI Platform Quick Start Guide

## Installation

```bash
# Clone repository
git clone https://github.com/Scarmonit/pc-automation-tools.git
cd pc-automation-tools

# Install dependencies
pip install -r requirements.txt
```

## Quick Commands

### 📸 Take Screenshot for Claude
```bash
python main.py pc_tools --action screenshot
```

### 🤖 Launch AI Platform
```bash
python main.py core
```

### 🔒 Run Security Scanner
```bash
python main.py security --action webscan
```

### 🐬 Dolphin Models
```bash
python main.py dolphin --action gui
```

### 📊 List All Modules
```bash
python main.py list
```

## Windows Users - Easy Launch

Double-click `MASTER_LAUNCHER.bat` for interactive menu

## Available Modules

| Module | Description | Command |
|--------|-------------|---------|
| **core** | Main AI platform | `python main.py core` |
| **security** | Security scanners | `python main.py security` |
| **dolphin** | Model management | `python main.py dolphin` |
| **automation** | Swarm intelligence | `python main.py automation` |
| **database** | Database tools | `python main.py database` |
| **monitoring** | Health monitoring | `python main.py monitoring` |
| **pc_tools** | PC automation | `python main.py pc_tools` |

## PC Automation Tools

### Screenshot Tools
- **Quick Screenshot**: Windows + Print Screen
- **Claude Integration**: Automatic path copying
- **Location**: `~/Pictures/Screenshots/`

### System Automation
- Hotkeys configuration
- Terminal management
- Workspace control

### Cloud Tools
- RunPod management
- GPU monitoring
- Model deployment

## Configuration

1. Copy `.env.example` to `.env`
2. Add your API keys:
```env
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

## Support

- GitHub Issues: [Report bugs](https://github.com/Scarmonit/pc-automation-tools/issues)
- Documentation: See `/docs` folder