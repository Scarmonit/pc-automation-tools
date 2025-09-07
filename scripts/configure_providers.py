#!/usr/bin/env python3
"""
Configure LLMStack providers for local models
"""
import requests
import json
import sys
import time

LLMSTACK_API = "http://localhost:3000/api"
ADMIN_TOKEN = "your-admin-token"  # Get from LLMStack UI

def wait_for_llmstack():
    """Wait for LLMStack to be ready"""
    print("Waiting for LLMStack to be ready...")
    for i in range(30):
        try:
            response = requests.get(f"{LLMSTACK_API}/health", timeout=2)
            if response.status_code == 200:
                print("✓ LLMStack is ready")
                return True
        except:
            pass
        time.sleep(2)
    print("✗ LLMStack not ready after 60 seconds")
    return False

def configure_providers():
    """Configure local model providers"""
    providers = [
        {
            "name": "Ollama",
            "type": "openai_compatible",
            "config": {
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",
                "models": ["llama3.2:3b", "mistral:7b", "codellama:7b"]
            }
        },
        {
            "name": "LM Studio",
            "type": "openai_compatible",
            "config": {
                "base_url": "http://localhost:1234/v1",
                "api_key": "lm-studio",
                "models": ["auto"]
            }
        },
        {
            "name": "vLLM",
            "type": "openai_compatible",
            "config": {
                "base_url": "http://localhost:8000/v1",
                "api_key": "vllm",
                "models": ["microsoft/Phi-3-mini-4k-instruct"]
            }
        }
    ]
    
    if not wait_for_llmstack():
        return False
    
    print("Configuring providers...")
    for provider in providers:
        try:
            # Check if provider endpoint is available
            test_url = provider["config"]["base_url"].replace("/v1", "")
            test_response = requests.get(f"{test_url}", timeout=2)
            
            if test_response.status_code not in [200, 404]:  # 404 is OK for some endpoints
                print(f"⚠ {provider['name']} not available, skipping")
                continue
                
            response = requests.post(
                f"{LLMSTACK_API}/providers",
                headers={"Authorization": f"Token {ADMIN_TOKEN}"},
                json=provider,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✓ Configured {provider['name']}")
            else:
                print(f"⚠ Failed to configure {provider['name']}: {response.status_code}")
                
        except Exception as e:
            print(f"⚠ Error configuring {provider['name']}: {e}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ADMIN_TOKEN = sys.argv[1]
    
    if ADMIN_TOKEN == "your-admin-token":
        print("Usage: python configure_providers.py <admin_token>")
        print("Get the admin token from LLMStack UI after initial setup")
        sys.exit(1)
    
    success = configure_providers()
    sys.exit(0 if success else 1)