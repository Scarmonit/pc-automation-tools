# Ollama Chat Examples

## Quick Chat Sessions

### 1. Basic Chat
```bash
# Start interactive chat with DeepSeek (best for reasoning)
ollama run deepseek-r1:8b

# Example prompts:
# > Explain quantum computing in simple terms
# > Write a Python function to find prime numbers
# > Help me debug this code: [paste your code]
```

### 2. Code Generation with Dolphin
```bash
# Use Dolphin for uncensored coding help
ollama run dolphin-mistral:latest

# Example prompts:
# > Create a REST API in FastAPI with user authentication
# > Write a web scraper for news articles
# > Build a Discord bot that responds to commands
```

### 3. One-liner Commands
```bash
# Quick question without entering chat
echo "What is the capital of France?" | ollama run llama3.1:8b

# Generate code and save to file
echo "Write a Python web server" | ollama run dolphin-mistral:latest > server.py

# Pipe file contents for analysis
cat mycode.py | ollama run deepseek-r1:8b "Review this code for bugs"
```

## API Usage Examples

### Python Script
```python
import requests
import json

def ask_ollama(prompt, model="deepseek-r1:8b"):
    response = requests.post(
        "http://localhost:11434/v1/chat/completions",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
    )
    return response.json()["choices"][0]["message"]["content"]

# Examples
print(ask_ollama("Write a haiku about programming"))
print(ask_ollama("Fix this SQL: SELCT * FORM users", "dolphin-mistral:latest"))
```

### Curl Command
```bash
curl -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "stream": false
  }'
```

### Streaming Responses
```python
import requests
import json

def stream_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/v1/chat/completions",
        json={
            "model": "deepseek-r1:8b",
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        },
        stream=True
    )
    
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8').replace('data: ', ''))
                if 'choices' in data:
                    print(data['choices'][0]['delta'].get('content', ''), end='')
            except:
                pass

stream_ollama("Write a story about a robot learning to paint")
```