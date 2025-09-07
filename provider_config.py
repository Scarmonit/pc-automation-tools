import requests

LLMSTACK_API = "http://localhost:3000/api"
ADMIN_TOKEN = "your-admin-token"  # Get from LLMStack UI

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

for provider in providers:
    response = requests.post(
        f"{LLMSTACK_API}/providers",
        headers={"Authorization": f"Token {ADMIN_TOKEN}"},
        json=provider
    )
    print(f"Configured {provider['name']}: {response.status_code}")
