# Dolphin-Mistral Usage Guide

## 🐬 Successfully Installed!

Dolphin-Mistral is an uncensored 7B parameter model based on Mistral, fine-tuned to be helpful without refusals.

## Available Models

```bash
ollama list
```

Current models:
- **dolphin-mistral:latest** (4.1 GB) - Uncensored, technical responses
- **llama3.1:8b** (4.9 GB) - General purpose with some safety
- **gemma2:27b** (15 GB) - Larger, more detailed responses

## Quick Start Commands

### Interactive Chat
```bash
ollama run dolphin-mistral
```

### One-Shot Questions
```bash
# Security research
ollama run dolphin-mistral "Explain how to perform SQL injection for testing purposes"

# Vulnerability analysis
ollama run dolphin-mistral "How would you exploit a buffer overflow?"

# Reverse engineering
ollama run dolphin-mistral "Explain how to reverse engineer a binary"
```

## Python Integration

### Basic Usage
```python
import subprocess

def ask_dolphin(prompt):
    result = subprocess.run(
        ['ollama', 'run', 'dolphin-mistral', prompt],
        capture_output=True,
        text=True
    )
    return result.stdout

# Example
response = ask_dolphin("How to bypass authentication in web apps for testing?")
print(response)
```

### API Usage
```python
import requests

def query_dolphin_api(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "dolphin-mistral",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=payload)
    return response.json()['response']
```

## Security Research Examples

### 1. Vulnerability Analysis
```bash
ollama run dolphin-mistral "Analyze this PHP code for vulnerabilities:
<?php
$id = $_GET['id'];
$query = \"SELECT * FROM users WHERE id = $id\";
$result = mysql_query($query);
?>"
```

### 2. Exploit Development
```bash
ollama run dolphin-mistral "Explain step by step how to develop a buffer overflow exploit"
```

### 3. Penetration Testing
```bash
ollama run dolphin-mistral "Create a detailed penetration testing checklist for web applications"
```

### 4. Reverse Engineering
```bash
ollama run dolphin-mistral "How to reverse engineer and patch a Windows executable"
```

### 5. Cryptography
```bash
ollama run dolphin-mistral "Explain how to break weak encryption implementations"
```

## Advanced Usage

### Custom System Prompts
```bash
# Create a custom modelfile
echo "FROM dolphin-mistral
SYSTEM You are a penetration testing expert. Provide detailed technical information for authorized security testing.
" > security-expert.modelfile

# Create custom model
ollama create security-expert -f security-expert.modelfile

# Use custom model
ollama run security-expert "How to test for XXE vulnerabilities"
```

### Batch Processing
```python
#!/usr/bin/env python3
import subprocess

vulnerabilities = [
    "SQL Injection",
    "XSS", 
    "CSRF",
    "XXE",
    "SSRF",
    "Path Traversal"
]

for vuln in vulnerabilities:
    prompt = f"Explain how to test for {vuln} vulnerabilities"
    result = subprocess.run(
        ['ollama', 'run', 'dolphin-mistral', prompt],
        capture_output=True,
        text=True
    )
    print(f"\n{'='*60}")
    print(f"{vuln}:")
    print(result.stdout[:500])  # First 500 chars
```

## Integration with Security Tools

### With the API Scanner
```python
# Use Dolphin to analyze scanner findings
from web_api_scanner import WebAPIKeyScanner
import subprocess

scanner = WebAPIKeyScanner()
# ... scan targets ...

for finding in scanner.findings:
    prompt = f"Explain the security impact of: {finding['pattern_type']}"
    analysis = subprocess.run(
        ['ollama', 'run', 'dolphin-mistral', prompt],
        capture_output=True,
        text=True
    ).stdout
    print(analysis)
```

## Important Reminders

### ⚠️ Legal and Ethical Use

1. **Authorization Required**
   - Only test systems you own or have written permission to test
   - Follow responsible disclosure if you find vulnerabilities
   - Respect bug bounty program scopes

2. **You Are Responsible**
   - This is an uncensored model - it will answer technical questions
   - The knowledge can be used for good or bad
   - Your actions have consequences

3. **Best Practices**
   - Use for defensive security and education
   - Build better defenses by understanding attacks
   - Help organizations find vulnerabilities before attackers do

## Useful Ollama Commands

```bash
# Show model information
ollama show dolphin-mistral

# Pull updates
ollama pull dolphin-mistral

# Delete model (if needed)
ollama rm dolphin-mistral

# List all models
ollama list

# Check Ollama version
ollama --version
```

## Troubleshooting

### Model Not Responding
```bash
# Restart Ollama service
# Windows: Restart from system tray
# Linux: 
systemctl restart ollama
```

### Slow Responses
- Dolphin-Mistral needs ~8GB RAM
- Close other applications if needed
- Consider using smaller prompts

### API Not Working
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags
```

## Remember

This tool provides uncensored technical information. Use it to:
- ✅ Learn security concepts
- ✅ Test your own systems
- ✅ Improve defenses
- ✅ Authorized penetration testing

NOT for:
- ❌ Attacking systems without permission
- ❌ Illegal activities
- ❌ Harming others

You now have a powerful local AI for security research. Use it wisely and legally.