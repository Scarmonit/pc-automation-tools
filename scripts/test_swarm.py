#!/usr/bin/env python3
"""Test the swarm intelligence system"""

import os
import sys
from pathlib import Path

# Set up paths
SWARM_DIR = Path.home() / ".claude" / "swarm-intelligence"
sys.path.insert(0, str(SWARM_DIR))

# Set environment variables
os.environ["WORKSPACE_ROOT"] = str(Path.home())
os.environ["SWARM_MEMORY_DB"] = str(SWARM_DIR / "swarm_memory.db")
os.environ["SWARM_CONFIG"] = str(SWARM_DIR / "swarm_config.json")
os.environ["PROMPTS_CONFIG"] = str(SWARM_DIR / "prompts_config.json")
os.environ["AI_PLATFORM_URL"] = "http://localhost:8000"
os.environ["DEMO_TOKEN"] = "demo-token"

# Load .env file
env_file = SWARM_DIR / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    print("[OK] Loaded API keys from .env file")

# Test imports
try:
    import sqlite3
    import json
    import aiohttp
    print("[OK] Core Python modules loaded")
    
    # Test swarm config
    config_file = SWARM_DIR / "swarm_config.json"
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
        print(f"[OK] Swarm configuration loaded: {len(config['agent_types'])} agent types configured")
        
    # Test memory database
    db_file = SWARM_DIR / "swarm_memory.db"
    if db_file.exists():
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"[OK] Memory database connected: {len(tables)} tables found")
        conn.close()
    
    # Test API keys
    keys_found = []
    for key in ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'PERPLEXITY_API_KEY']:
        if os.environ.get(key):
            keys_found.append(key.replace('_API_KEY', ''))
    
    if keys_found:
        print(f"[OK] API keys configured: {', '.join(keys_found)}")
    else:
        print("[ERROR] No API keys found")
        
    print("\n=== SWARM INTELLIGENCE SYSTEM IS READY! ===")
    print("\nAgent Types Available:")
    for agent_type in config['agent_types']:
        print(f"  - {agent_type.title()}: {', '.join(config['agent_types'][agent_type]['capabilities'])}")
        
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()