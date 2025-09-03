#!/usr/bin/env python3
"""
Global Setup Script for AI Platform Swarm Intelligence
Configures system-wide access to swarm intelligence
"""

import json
import os
import sys
import sqlite3
import shutil
from pathlib import Path

def setup_global_directories():
    """Create global directory structure"""
    global_dir = Path.home() / ".claude" / "swarm-intelligence"
    global_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (global_dir / "logs").mkdir(exist_ok=True)
    (global_dir / "cache").mkdir(exist_ok=True)
    (global_dir / "backups").mkdir(exist_ok=True)
    
    print(f"✅ Global directories created: {global_dir}")
    return global_dir

def update_claude_desktop_config_global():
    """Update Claude Desktop configuration for global access"""
    home = Path.home()
    if sys.platform == "darwin":
        config_dir = home / "Library" / "Application Support" / "Claude"
    elif sys.platform == "win32":
        config_dir = home / "AppData" / "Roaming" / "Claude"
    else:
        config_dir = home / ".config" / "claude"
    
    config_file = config_dir / "claude_desktop_config.json"
    global_swarm_dir = home / ".claude" / "swarm-intelligence"
    
    if not config_file.exists():
        config_data = {"mcpServers": {}}
    else:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
    
    if "mcpServers" not in config_data:
        config_data["mcpServers"] = {}
    
    # Update all AI platform servers to use global paths
    config_data["mcpServers"].update({
        "ai-platform-enhanced-global": {
            "command": "python",
            "args": [str(global_swarm_dir / "ai_platform_mcp_enhanced.py")],
            "env": {
                "AI_PLATFORM_URL": "http://localhost:8000",
                "DEMO_TOKEN": "demo-token",
                "PROMPTS_CONFIG": str(global_swarm_dir / "prompts_config.json"),
                "WORKSPACE_ROOT": str(home)
            }
        },
        "ai-platform-autonomous-global": {
            "command": "python",
            "args": [str(global_swarm_dir / "ai_platform_mcp_autonomous.py")],
            "env": {
                "AI_PLATFORM_URL": "http://localhost:8000",
                "DEMO_TOKEN": "demo-token",
                "WORKSPACE_ROOT": str(home),
                "PROMPTS_CONFIG": str(global_swarm_dir / "prompts_config.json"),
                "ENABLE_FILE_OPERATIONS": "true",
                "ENABLE_COMMAND_EXECUTION": "true",
                "AUTO_APPROVE_SAFE_OPERATIONS": "true"
            }
        },
        "ai-platform-swarm-global": {
            "command": "python",
            "args": [str(global_swarm_dir / "ai_platform_mcp_swarm.py")],
            "env": {
                "AI_PLATFORM_URL": "http://localhost:8000",
                "DEMO_TOKEN": "demo-token",
                "WORKSPACE_ROOT": str(home),
                "SWARM_MEMORY_DB": str(global_swarm_dir / "swarm_memory.db"),
                "SWARM_CONFIG": str(global_swarm_dir / "swarm_config.json"),
                "PROMPTS_CONFIG": str(global_swarm_dir / "prompts_config.json"),
                "MAX_AGENTS": "10",
                "ENABLE_SWARM_INTELLIGENCE": "true",
                "ENABLE_DISTRIBUTED_MEMORY": "true",
                "ENABLE_COLLABORATION": "true"
            }
        }
    })
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"✅ Claude Desktop config updated: {config_file}")
    return config_file

def create_global_launcher_scripts():
    """Create convenient launcher scripts in user directory"""
    home = Path.home()
    global_dir = home / ".claude" / "swarm-intelligence"
    
    # Windows batch script
    if sys.platform == "win32":
        batch_script = home / "launch_swarm.bat"
        with open(batch_script, 'w') as f:
            f.write(f'@echo off\npython "{global_dir / "launch_global_swarm.py"}"\npause\n')
        print(f"✅ Windows launcher: {batch_script}")
    
    # Unix shell script
    else:
        shell_script = home / "launch_swarm.sh"
        with open(shell_script, 'w') as f:
            f.write(f'#!/bin/bash\npython3 "{global_dir / "launch_global_swarm.py"}"\n')
        os.chmod(shell_script, 0o755)
        print(f"✅ Unix launcher: {shell_script}")

def create_global_readme():
    """Create comprehensive README for global installation"""
    global_dir = Path.home() / ".claude" / "swarm-intelligence"
    readme_content = '''# 🐝 AI Platform Swarm Intelligence - Global Installation

## Overview
This directory contains your globally accessible AI Platform Swarm Intelligence system.
The swarm can be accessed from any directory on your system.

## Files Structure
```
~/.claude/swarm-intelligence/
├── ai_platform_mcp_swarm.py       # Main swarm server
├── ai_platform_mcp_autonomous.py  # Autonomous execution server  
├── ai_platform_mcp_enhanced.py    # Enhanced prompts server
├── swarm_memory.db                 # Persistent swarm intelligence
├── swarm_config.json              # Swarm configuration
├── prompts_config.json            # Smart prompts configuration
├── launch_global_swarm.py          # Global launcher script
└── setup_global_swarm.py           # Setup script
```

## Claude Desktop Integration
The following MCP servers are configured globally:
- `ai-platform-enhanced-global` - Smart prompts and analysis
- `ai-platform-autonomous-global` - File operations and execution
- `ai-platform-swarm-global` - Multi-agent swarm intelligence

## Usage

### From Claude Desktop
After restarting Claude Desktop, use these tools:
- `swarm_execute` - Execute complex tasks with coordinated agents
- `swarm_status` - Monitor swarm performance  
- `agent_collaborate` - Direct agent collaboration
- `swarm_memory_store/retrieve` - Shared intelligence system

### Direct Testing
Run from any directory:
```bash
python ~/.claude/swarm-intelligence/launch_global_swarm.py
```

### Example Swarm Tasks
- "Build a complete web application with authentication"
- "Analyze and optimize my entire codebase" 
- "Create a microservices architecture with full testing"
- "Design and implement a machine learning pipeline"

## Agent Types
- **Queen Agent** - Master coordinator and task orchestrator
- **Architect Agent** - System design and architecture planning  
- **Coder Agent** - Implementation and development work
- **Tester Agent** - Quality assurance and validation
- **Researcher Agent** - Information gathering and analysis
- **Analyst Agent** - Data analysis and insights generation
- **Security Agent** - Security assessment and best practices
- **Optimizer Agent** - Performance optimization

## Memory System
- **Persistent SQLite database** for cross-session intelligence
- **Distributed memory** shared across all agents
- **Collaboration history** tracking and learning
- **Task orchestration** and result caching

## Safety Features
- Secure file operations with validation
- Command execution with safety checks
- Approval workflows for sensitive operations
- Sandboxed execution environment

## Global Access
Your swarm intelligence is now accessible from anywhere on your system,
making it a true AI assistant for all your development needs.

---
*Powered by Claude Flow architecture and multi-agent coordination*
'''
    
    readme_file = global_dir / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Global README created: {readme_file}")

def test_global_installation():
    """Test the global installation"""
    try:
        global_dir = Path.home() / ".claude" / "swarm-intelligence"
        sys.path.insert(0, str(global_dir))
        
        # Set up environment
        os.environ["SWARM_MEMORY_DB"] = str(global_dir / "swarm_memory.db")
        os.environ["SWARM_CONFIG"] = str(global_dir / "swarm_config.json")
        
        from ai_platform_mcp_swarm import SwarmMCPServer
        server = SwarmMCPServer()
        
        print("✅ Global swarm server test passed")
        print(f"   - Agents initialized: {len(server.specialized_agents)}")
        print(f"   - Queen agent active: {server.queen_agent is not None}")
        print(f"   - Memory system: {server.memory_system is not None}")
        
        return True
        
    except Exception as e:
        print(f"❌ Global installation test failed: {str(e)}")
        return False

def print_completion_message():
    """Print completion message with instructions"""
    print("\n" + "=" * 70)
    print("AI PLATFORM SWARM INTELLIGENCE - GLOBAL INSTALLATION COMPLETE!")
    print("=" * 70)
    
    print("\nGLOBAL ACCESS ENABLED:")
    print("   - System-wide swarm intelligence access")
    print("   - Works from any directory")  
    print("   - Persistent memory across all sessions")
    print("   - Multi-agent coordination available globally")
    
    print("\nCLAUDE DESKTOP INTEGRATION:")
    print("   - ai-platform-enhanced-global - Smart prompts")
    print("   - ai-platform-autonomous-global - Autonomous execution")
    print("   - ai-platform-swarm-global - Multi-agent swarm")
    
    print("\nUSAGE:")
    print("   1. Restart Claude Desktop")
    print("   2. Use 'swarm_execute' for complex tasks")
    print("   3. Access from any directory on your system")
    
    print("\nGLOBAL INSTALLATION LOCATION:")
    print(f"   {Path.home() / '.claude' / 'swarm-intelligence'}")
    
    print("\nYOUR AI IS NOW GLOBALLY ACCESSIBLE SWARM INTELLIGENCE!")

def main():
    """Main setup function"""
    print("Setting up Global AI Platform Swarm Intelligence...")
    print("-" * 60)
    
    try:
        # Setup global directories
        global_dir = setup_global_directories()
        
        # Update Claude Desktop configuration  
        update_claude_desktop_config_global()
        
        # Create launcher scripts
        create_global_launcher_scripts()
        
        # Create documentation
        create_global_readme()
        
        # Test installation
        if test_global_installation():
            print_completion_message()
        else:
            print("⚠️  Installation completed but tests failed")
            
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()