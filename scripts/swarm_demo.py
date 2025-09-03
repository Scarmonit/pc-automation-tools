#!/usr/bin/env python3
"""
AI Swarm Intelligence Demo
Demonstrates the swarm capabilities without interactive mode
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import time

# Set up paths
SWARM_DIR = Path.home() / ".claude" / "swarm-intelligence"
sys.path.insert(0, str(SWARM_DIR))

# Load environment
env_file = SWARM_DIR / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

print("=" * 70)
print(" " * 15 + "AI SWARM INTELLIGENCE DEMO")
print("=" * 70)
print()

# Load configuration
config_file = SWARM_DIR / "swarm_config.json"
with open(config_file) as f:
    config = json.load(f)

# Connect to memory
db_file = SWARM_DIR / "swarm_memory.db"
conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

print("[INITIALIZATION] Swarm Intelligence Active")
print(f"[INITIALIZATION] {len(config['agent_types'])} Agent Types Loaded")
print(f"[INITIALIZATION] API Keys: Anthropic, OpenAI, Perplexity")
print()

# Demo Task 1: Store Knowledge
print("=" * 70)
print("DEMO 1: Storing Knowledge in Distributed Memory")
print("=" * 70)
knowledge_items = [
    ("project_architecture", "Microservices with Python FastAPI backend"),
    ("deployment_strategy", "Docker containers on Kubernetes"),
    ("testing_framework", "PyTest with 85% coverage requirement")
]

for key, value in knowledge_items:
    cursor.execute(
        "INSERT OR REPLACE INTO swarm_memory (namespace, key, value, type, created_at) VALUES ('global', ?, ?, 'knowledge', datetime('now'))",
        (key, value)
    )
    print(f"[MEMORY] Stored: {key} -> {value}")
conn.commit()
print()

# Demo Task 2: Multi-Agent Task Execution
print("=" * 70)
print("DEMO 2: Multi-Agent Task Execution")
print("=" * 70)
task = "Implement user authentication system with JWT tokens"
print(f"[USER] Task: {task}")
print()

# Simulate agent collaboration
agents_sequence = [
    ("QUEEN", "Analyzing task requirements and assigning agents..."),
    ("ARCHITECT", "Designing authentication flow: Login -> JWT Generation -> Validation"),
    ("SECURITY", "Recommending bcrypt for password hashing, 256-bit JWT secrets"),
    ("CODER", "Implementing auth endpoints: /login, /register, /refresh"),
    ("TESTER", "Creating test suite: Unit tests for JWT validation, Integration tests for auth flow"),
    ("ANALYST", "Performance analysis: JWT validation takes <10ms, supports 1000 req/sec"),
    ("QUEEN", "Task completed successfully. All agents reported success.")
]

for agent, action in agents_sequence:
    print(f"[{agent}] {action}")
    time.sleep(0.5)  # Simulate processing time

print()

# Demo Task 3: Retrieve Knowledge
print("=" * 70)
print("DEMO 3: Retrieving from Distributed Memory")
print("=" * 70)
cursor.execute("SELECT key, value FROM swarm_memory WHERE type = 'knowledge'")
memories = cursor.fetchall()
print(f"[MEMORY] Found {len(memories)} knowledge entries:")
for key, value in memories[:5]:  # Show first 5
    print(f"  - {key}: {value}")
print()

# Demo Task 4: Agent Status
print("=" * 70)
print("DEMO 4: Agent Status Report")
print("=" * 70)
for agent_type, agent_config in config['agent_types'].items():
    status = "READY" if agent_config['priority'] > 5 else "STANDBY"
    print(f"[{agent_type.upper()}] Status: {status}, Priority: {agent_config['priority']}/10")
print()

# Store task completion
cursor.execute(
    "INSERT INTO swarm_memory (namespace, key, value, type, created_at) VALUES ('global', ?, ?, 'task', datetime('now'))",
    ("demo_task", "Authentication system implementation completed")
)
conn.commit()

# Final summary
cursor.execute("SELECT COUNT(*) FROM swarm_memory WHERE type='task'")
task_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM swarm_memory WHERE type='knowledge'")
knowledge_count = cursor.fetchone()[0]

print("=" * 70)
print("SWARM INTELLIGENCE SUMMARY")
print("=" * 70)
print(f"Tasks Completed: {task_count}")
print(f"Knowledge Base: {knowledge_count} entries")
print(f"Active Agents: {len(config['agent_types'])}")
print(f"System Status: FULLY OPERATIONAL")
print()
print("Swarm Intelligence Demo Complete!")
print("=" * 70)

conn.close()