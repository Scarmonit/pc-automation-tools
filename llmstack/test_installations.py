#!/usr/bin/env python3
"""Test AI Framework Installations"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print(f"Python: {sys.version}")
print("-" * 60)

# Test each framework
frameworks = {
    'memgpt': 'MemGPT',
    'autogen': 'AutoGen',
    'camel': 'CAMEL-AI',
    'openai': 'OpenAI',
    'requests': 'Requests'
}

installed = []
missing = []

for module, name in frameworks.items():
    try:
        __import__(module)
        print(f"[OK] {name} installed")
        installed.append(name)
    except ImportError:
        print(f"[X] {name} not installed")
        missing.append(name)

print("-" * 60)
print(f"Installed: {len(installed)}/{len(frameworks)}")

if missing:
    print(f"Missing: {', '.join(missing)}")
    print("\nTo install missing packages, run:")
    for name in missing:
        module = [k for k, v in frameworks.items() if v == name][0]
        if module == 'autogen':
            print(f"  pip install pyautogen")
        else:
            print(f"  pip install {module}")
else:
    print("All frameworks are installed!")

# Test LocalAI connection
print("\n" + "-" * 60)
print("Testing LocalAI connection...")
try:
    import requests
    response = requests.get("http://localhost:8080/models", timeout=2)
    if response.status_code == 200:
        print("[OK] LocalAI is running at http://localhost:8080")
    else:
        print(f"[X] LocalAI returned status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("[X] LocalAI is not running. Run 'setup_localai.bat' to start it.")
except Exception as e:
    print(f"[X] Error connecting to LocalAI: {e}")

print("-" * 60)