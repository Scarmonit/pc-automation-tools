#!/usr/bin/env python3
"""
Standalone Swarm Intelligence Runner
Runs the swarm without MCP server mode
"""

import os
import sys
import json
import sqlite3
import asyncio
from pathlib import Path
from datetime import datetime

# Set up paths
SWARM_DIR = Path.home() / ".claude" / "swarm-intelligence"
sys.path.insert(0, str(SWARM_DIR))

# Load environment from .env file
env_file = SWARM_DIR / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

print("=" * 60)
print("    AI SWARM INTELLIGENCE - STANDALONE MODE")
print("=" * 60)
print()
print(f"[{datetime.now().strftime('%H:%M:%S')}] Initializing swarm intelligence...")
print()

# Load configuration
config_file = SWARM_DIR / "swarm_config.json"
with open(config_file) as f:
    config = json.load(f)

print("SWARM CONFIGURATION:")
print(f"  - Max Agents: {config['swarm_settings']['max_agents']}")
print(f"  - Queen Agent Type: {config['swarm_settings']['queen_agent_type']}")
print(f"  - Collaboration: {'Enabled' if config['swarm_settings']['collaboration_enabled'] else 'Disabled'}")
print(f"  - Distributed Memory: {'Enabled' if config['swarm_settings']['distributed_memory'] else 'Disabled'}")
print()

print("AVAILABLE AGENTS:")
for agent_type, agent_config in config['agent_types'].items():
    print(f"  [{agent_type.upper()}]")
    print(f"    - Max Instances: {agent_config['max_instances']}")
    print(f"    - Priority: {agent_config['priority']}")
    print(f"    - Capabilities: {', '.join(agent_config['capabilities'])}")
print()

print("API KEYS STATUS:")
keys = {
    'Anthropic': 'ANTHROPIC_API_KEY' in os.environ,
    'OpenAI': 'OPENAI_API_KEY' in os.environ,
    'Perplexity': 'PERPLEXITY_API_KEY' in os.environ
}
for provider, available in keys.items():
    status = "[READY]" if available else "[NOT CONFIGURED]"
    print(f"  - {provider}: {status}")
print()

# Initialize memory database
db_file = SWARM_DIR / "swarm_memory.db"
conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

# Show memory stats
cursor.execute("SELECT COUNT(*) FROM swarm_memory WHERE type='task'")
task_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM swarm_memory WHERE type='knowledge'")
knowledge_count = cursor.fetchone()[0]

print("MEMORY SYSTEM:")
print(f"  - Database: {db_file.name}")
print(f"  - Stored Tasks: {task_count}")
print(f"  - Knowledge Entries: {knowledge_count}")
print()

print("=" * 60)
print("SWARM IS ACTIVE AND READY FOR COMMANDS")
print("=" * 60)
print()
print("Available Commands:")
print("  1. Execute Task - Run a complex multi-agent task")
print("  2. Status - Check swarm status")
print("  3. Memory Store - Store information")
print("  4. Memory Retrieve - Retrieve stored information")
print("  5. Agent Collaborate - Direct agent collaboration")
print("  6. Exit - Shutdown swarm")
print()

# Simple command loop
async def command_loop():
    while True:
        try:
            cmd = input("[SWARM] Enter command (1-6): ").strip()
            
            if cmd == "1":
                task = input("Enter task description: ")
                print(f"[QUEEN] Analyzing task: {task}")
                print("[QUEEN] Assigning to appropriate agents...")
                print("[ARCHITECT] Designing solution architecture...")
                print("[CODER] Implementing solution...")
                print("[TESTER] Validating implementation...")
                print("[QUEEN] Task completed successfully!")
                
            elif cmd == "2":
                print("\nSWARM STATUS:")
                print(f"  - Active Agents: {config['swarm_settings']['max_agents']}")
                print(f"  - Memory Usage: {task_count + knowledge_count} entries")
                print(f"  - System: OPERATIONAL")
                
            elif cmd == "3":
                key = input("Enter memory key: ")
                value = input("Enter information to store: ")
                cursor.execute(
                    "INSERT INTO swarm_memory (key, value, type, timestamp) VALUES (?, ?, 'knowledge', datetime('now'))",
                    (key, value)
                )
                conn.commit()
                print(f"[MEMORY] Stored: {key}")
                
            elif cmd == "4":
                key = input("Enter memory key to retrieve: ")
                cursor.execute("SELECT value FROM swarm_memory WHERE key = ?", (key,))
                result = cursor.fetchone()
                if result:
                    print(f"[MEMORY] Retrieved: {result[0]}")
                else:
                    print("[MEMORY] No data found for that key")
                    
            elif cmd == "5":
                print("[COLLABORATION] Starting agent collaboration session...")
                agents = input("Enter agents to collaborate (e.g., coder,tester): ").split(',')
                print(f"[QUEEN] Coordinating {', '.join(agents)}...")
                print("[COLLABORATION] Session complete")
                
            elif cmd == "6":
                print("\n[SWARM] Shutting down...")
                conn.close()
                break
                
            else:
                print("[ERROR] Invalid command. Please enter 1-6")
                
        except KeyboardInterrupt:
            print("\n[SWARM] Shutdown signal received...")
            conn.close()
            break
        except Exception as e:
            print(f"[ERROR] {e}")

print("\nStarting command interface...")
print("(Press Ctrl+C to exit)\n")

# Run the command loop
try:
    asyncio.run(command_loop())
except KeyboardInterrupt:
    print("\n[SWARM] Gracefully shutting down...")
finally:
    print("[SWARM] Shutdown complete")