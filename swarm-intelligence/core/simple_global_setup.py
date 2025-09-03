#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def main():
    print("Setting up Global AI Platform Swarm Intelligence...")
    
    # Update Claude Desktop config
    home = Path.home()
    if sys.platform == "win32":
        config_dir = home / "AppData" / "Roaming" / "Claude"
    else:
        config_dir = home / ".config" / "claude"
    
    config_file = config_dir / "claude_desktop_config.json"
    global_swarm_dir = home / ".claude" / "swarm-intelligence"
    
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    
    # Add global servers
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
    
    print(f"SUCCESS: Claude Desktop config updated: {config_file}")
    print()
    print("GLOBAL AI PLATFORM SWARM INTELLIGENCE - SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("GLOBAL ACCESS ENABLED:")
    print("   - System-wide swarm intelligence access")
    print("   - Works from any directory")  
    print("   - Persistent memory across all sessions")
    print("   - Multi-agent coordination available globally")
    print()
    print("CLAUDE DESKTOP INTEGRATION:")
    print("   - ai-platform-enhanced-global - Smart prompts")
    print("   - ai-platform-autonomous-global - Autonomous execution")
    print("   - ai-platform-swarm-global - Multi-agent swarm")
    print()
    print("USAGE:")
    print("   1. Restart Claude Desktop")
    print("   2. Use 'swarm_execute' for complex tasks")
    print("   3. Access from any directory on your system")
    print()
    print(f"GLOBAL INSTALLATION: {global_swarm_dir}")
    print()
    print("YOUR AI IS NOW GLOBALLY ACCESSIBLE SWARM INTELLIGENCE!")

if __name__ == "__main__":
    main()