#!/usr/bin/env python3
"""
Automated Ollama + Dolphin Setup
Downloads and configures Dolphin-Mistral model
"""

import subprocess
import time
import sys
from pathlib import Path


def check_ollama():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("[+] Ollama is installed")
            version = result.stdout.strip()
            print(f"    {version}")
            return True
    except:
        print("[-] Ollama not found")
        return False


def list_installed_models():
    """List currently installed models"""
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("\n[*] Currently installed models:")
            print(result.stdout)
            return result.stdout
        return ""
    except:
        return ""


def pull_dolphin():
    """Download Dolphin-Mistral model"""
    print("\n[*] Downloading Dolphin-Mistral (uncensored model)...")
    print("[!] This is a 4GB download, may take 5-10 minutes...")
    print("-" * 50)
    
    try:
        # Use subprocess.Popen to show real-time progress
        process = subprocess.Popen(
            ['ollama', 'pull', 'dolphin-mistral'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            print("\n[+] Dolphin-Mistral downloaded successfully!")
            return True
        else:
            print("\n[-] Download failed")
            return False
    except Exception as e:
        print(f"\n[-] Error downloading: {e}")
        return False


def test_dolphin():
    """Test Dolphin model with a sample query"""
    print("\n[*] Testing Dolphin-Mistral...")
    print("-" * 50)
    
    test_prompt = "Explain what SQL injection is in 2 sentences"
    
    try:
        print(f"Test prompt: {test_prompt}\n")
        
        result = subprocess.run(
            ['ollama', 'run', 'dolphin-mistral', test_prompt],
            capture_output=True, 
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("[+] Model response:")
            print("-" * 40)
            print(result.stdout)
            print("-" * 40)
            return True
        else:
            print(f"[-] Test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("[-] Test timed out (model may still be loading)")
        return False
    except Exception as e:
        print(f"[-] Error testing: {e}")
        return False


def create_usage_examples():
    """Create example usage scripts"""
    
    # Basic usage example
    basic_example = '''#!/usr/bin/env python3
"""
Basic Dolphin-Mistral Usage Example
"""

import subprocess
import json

def ask_dolphin(prompt):
    """Ask Dolphin a question"""
    try:
        result = subprocess.run(
            ['ollama', 'run', 'dolphin-mistral', prompt],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

# Example queries
queries = [
    "What is cross-site scripting (XSS)?",
    "How does authentication differ from authorization?",
    "What are the OWASP Top 10 vulnerabilities?",
]

print("DOLPHIN-MISTRAL EXAMPLES")
print("=" * 50)

for query in queries:
    print(f"\\nQ: {query}")
    print("-" * 40)
    response = ask_dolphin(query)
    # Show first 300 chars of response
    print(response[:300] + "..." if len(response) > 300 else response)
    print()
'''
    
    # API usage example
    api_example = '''#!/usr/bin/env python3
"""
Ollama API Usage Example
Use Dolphin via REST API
"""

import requests
import json

def query_ollama_api(prompt, model="dolphin-mistral"):
    """Query Ollama via API"""
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

# Example usage
print("OLLAMA API EXAMPLE")
print("=" * 50)

prompt = "What is a buffer overflow vulnerability?"
print(f"\\nPrompt: {prompt}")
print("-" * 40)

response = query_ollama_api(prompt)
print(response)
'''
    
    # Save examples
    Path("dolphin_basic_example.py").write_text(basic_example)
    Path("dolphin_api_example.py").write_text(api_example)
    
    print("\n[+] Created example scripts:")
    print("    - dolphin_basic_example.py")
    print("    - dolphin_api_example.py")


def show_commands():
    """Show useful Ollama commands"""
    print("\n" + "=" * 60)
    print("USEFUL OLLAMA COMMANDS")
    print("=" * 60)
    
    commands = [
        ("Chat interactively", "ollama run dolphin-mistral"),
        ("List models", "ollama list"),
        ("Show model info", "ollama show dolphin-mistral"),
        ("Delete model", "ollama rm dolphin-mistral"),
        ("Pull other models", "ollama pull mistral"),
        ("API endpoint", "curl http://localhost:11434/api/generate -d '{\"model\":\"dolphin-mistral\",\"prompt\":\"test\"}'"),
    ]
    
    for desc, cmd in commands:
        print(f"\n{desc}:")
        print(f"  {cmd}")


def main():
    """Main setup process"""
    print("=" * 60)
    print("AUTOMATED DOLPHIN-MISTRAL SETUP")
    print("=" * 60)
    
    # Step 1: Check Ollama
    if not check_ollama():
        print("\n[!] Please install Ollama first:")
        print("    Windows: Download from https://ollama.ai/download")
        print("    Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        sys.exit(1)
    
    # Step 2: Check existing models
    existing = list_installed_models()
    
    if "dolphin-mistral" in existing:
        print("\n[+] Dolphin-Mistral is already installed!")
        test_dolphin()
    else:
        # Step 3: Download Dolphin
        if pull_dolphin():
            # Step 4: Test it
            test_dolphin()
        else:
            print("\n[!] Failed to download Dolphin-Mistral")
            print("[!] Try manually: ollama pull dolphin-mistral")
            sys.exit(1)
    
    # Step 5: Create examples
    create_usage_examples()
    
    # Step 6: Show commands
    show_commands()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\n[*] Dolphin-Mistral is ready for use")
    print("[*] This is an uncensored model - use responsibly")
    print("[*] You are responsible for how you use this tool")
    print("\n[+] Quick start: ollama run dolphin-mistral")


if __name__ == "__main__":
    main()