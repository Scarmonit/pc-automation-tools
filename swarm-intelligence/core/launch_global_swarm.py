#!/usr/bin/env python3
"""
Global Launcher for AI Platform Swarm Intelligence
Can be run from anywhere on the system
"""

import asyncio
import sys
import os
from pathlib import Path

# Set up paths
GLOBAL_SWARM_DIR = Path.home() / ".claude" / "swarm-intelligence"
sys.path.insert(0, str(GLOBAL_SWARM_DIR))

# Set environment variables for global operation
os.environ["WORKSPACE_ROOT"] = str(Path.home())
os.environ["SWARM_MEMORY_DB"] = str(GLOBAL_SWARM_DIR / "swarm_memory.db")
os.environ["SWARM_CONFIG"] = str(GLOBAL_SWARM_DIR / "swarm_config.json")
os.environ["PROMPTS_CONFIG"] = str(GLOBAL_SWARM_DIR / "prompts_config.json")
os.environ["AI_PLATFORM_URL"] = "http://localhost:8000"
os.environ["DEMO_TOKEN"] = "demo-token"
os.environ["ENABLE_SWARM_INTELLIGENCE"] = "true"
os.environ["ENABLE_DISTRIBUTED_MEMORY"] = "true"
os.environ["ENABLE_COLLABORATION"] = "true"
os.environ["MAX_AGENTS"] = "10"

try:
    from ai_platform_mcp_swarm import main
except ImportError:
    print("Error: Swarm intelligence files not found in global directory")
    print(f"Expected location: {GLOBAL_SWARM_DIR}")
    print("Run the setup script to install globally")
    sys.exit(1)

if __name__ == "__main__":
    print("GLOBAL AI PLATFORM SWARM INTELLIGENCE")
    print("=" * 60)
    print(f"Global Installation: {GLOBAL_SWARM_DIR}")
    print(f"Working from: {Path.cwd()}")
    print(f"Memory Database: {os.environ['SWARM_MEMORY_DB']}")
    print()
    print("SWARM INTELLIGENCE CAPABILITIES ENABLED:")
    print("   - Multi-Agent Coordination (Queen + Workers)")
    print("   - Distributed Memory System (SQLite)")
    print("   - Collaborative Problem Solving")
    print("   - Task Orchestration and Planning")
    print("   - Cross-Agent Communication")
    print("   - Global System Access")
    print()
    print("Available Agent Types:")
    print("   - Queen Agent (Master Coordinator)")
    print("   - Architect (System Design)")
    print("   - Coder (Implementation)")
    print("   - Tester (Quality Assurance)")
    print("   - Researcher (Information Gathering)")
    print("   - Analyst (Data Analysis)")
    print("   - Security (Security Assessment)")
    print("   - Optimizer (Performance Optimization)")
    print()
    print("Swarm Tools Available:")
    print("   - swarm_execute - Complex multi-agent task execution")
    print("   - swarm_status - Real-time swarm monitoring")
    print("   - agent_collaborate - Direct agent collaboration")
    print("   - swarm_memory_store/retrieve - Shared intelligence")
    print()
    print("Memory System: SQLite-based distributed storage")
    print("Safety: All autonomous server protections active")
    print("Scope: Global system access from any directory")
    print()
    print("Press Ctrl+C to stop the swarm")
    print("-" * 60)
    
    asyncio.run(main())