# 🤖 Jan Desktop AI Assistant Setup Guide

Jan is a user-friendly desktop application that provides a ChatGPT-like interface for local AI models. This guide shows you how to set up Jan with your local AI infrastructure for a seamless desktop AI experience.

## 🚀 Quick Start

### Automatic Setup
```bash
# Install Jan desktop app
bash scripts/install_jan.sh

# Configure with local models
python3 scripts/configure_providers.py --jan
```

### Manual Installation

#### Windows
1. Download Jan from [jan.ai](https://jan.ai/download)
2. Run the installer
3. Follow setup wizard

#### macOS
```bash
# Using Homebrew
brew install --cask jan

# Or download from website
```

#### Linux
```bash
# Ubuntu/Debian
wget https://github.com/janhq/jan/releases/latest/download/jan-linux-amd64.deb
sudo dpkg -i jan-linux-amd64.deb

# Or use AppImage
wget https://github.com/janhq/jan/releases/latest/download/jan-linux-x86_64.AppImage
chmod +x jan-linux-x86_64.AppImage
./jan-linux-x86_64.AppImage
```

## 📋 Prerequisites

- **4GB+ RAM** for running local models
- **10GB+ Storage** for models and application
- **Modern CPU** (4+ cores recommended)
- **Optional GPU** for acceleration
- **Internet connection** for initial setup and model downloads

## 🔧 Configuration

### 1. Initial Setup

When you first launch Jan:

1. **Welcome Screen**: Complete the initial setup wizard
2. **Model Selection**: Choose or download AI models
3. **Settings Configuration**: Configure performance and behavior
4. **Local Server**: Enable API server for integrations

### 2. Local Model Integration

#### Connect to Ollama
1. Open Jan Settings (⚙️ icon)
2. Go to "Extensions" tab
3. Enable "Local Server Extension"
4. Configure Ollama connection:

```json
{
  "server": {
    "host": "localhost",
    "port": 11434,
    "https": false
  },
  "models": [
    {
      "id": "llama3.2",
      "name": "Llama 3.2",
      "provider": "ollama"
    },
    {
      "id": "mistral:7b", 
      "name": "Mistral 7B",
      "provider": "ollama"
    },
    {
      "id": "codellama:7b",
      "name": "Code Llama 7B", 
      "provider": "ollama"
    }
  ]
}
```

#### Download Models Directly in Jan
1. Go to "Hub" tab in Jan
2. Browse available models
3. Click "Download" for desired models
4. Wait for download to complete

### 3. Advanced Configuration

#### Performance Settings
```json
{
  "engine": {
    "nitro": {
      "ctx_len": 4096,
      "ngl": 32,
      "cpu_threads": 4,
      "cont_batching": true,
      "embedding": true
    }
  },
  "app": {
    "gpuAcceleration": true,
    "theme": "dark",
    "language": "en"
  }
}
```

#### API Server Configuration
```json
{
  "apiServer": {
    "enabled": true,
    "port": 1337,
    "cors": true,
    "prefix": "/v1",
    "verboseLogging": false
  }
}
```

## 💬 Using Jan

### Basic Chat Interface

#### 1. Starting a Conversation
1. Open Jan desktop app
2. Click "New Thread" or use existing thread
3. Select your preferred model
4. Start typing your message

#### 2. Model Selection
- **Quick Tasks**: Use smaller, faster models (Llama 3.2 1B)
- **Complex Reasoning**: Use larger models (Llama 3.2 8B)
- **Coding Tasks**: Use specialized models (Code Llama)
- **Writing Tasks**: Use language-focused models (Mistral)

#### 3. Chat Features
- **Thread Management**: Organize conversations by topic
- **Model Switching**: Change models mid-conversation
- **Export/Import**: Save and share conversations
- **Search**: Find previous conversations

### Advanced Features

#### 1. System Instructions
Create custom system prompts for different use cases:

```
// For coding assistance
You are an expert software developer specializing in Python, Docker, and AI systems. 
You provide practical, working code solutions with proper error handling and documentation.
You understand this project uses AutoGen, Flowise, OpenHands, and other AI tools.

// For documentation
You are a technical writer who creates clear, comprehensive documentation. 
You use emoji headers, include troubleshooting sections, and provide practical examples.
You follow the repository's documentation standards.

// For system administration  
You are a DevOps engineer expert in Docker, monitoring, and AI system deployment.
You provide secure, scalable solutions with proper monitoring and logging.
```

#### 2. Temperature and Parameters
Adjust model behavior for different tasks:

```json
{
  "temperature": 0.1,  // For factual, consistent responses
  "top_p": 0.9,
  "top_k": 40,
  "max_tokens": 2048,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0
}
```

```json
{
  "temperature": 0.8,  // For creative, varied responses
  "top_p": 0.95,
  "top_k": 50,
  "max_tokens": 2048,
  "frequency_penalty": 0.1,
  "presence_penalty": 0.1
}
```

## 🔄 Integration with Repository

### API Integration

Jan provides an OpenAI-compatible API that you can integrate with your automation tools:

```python
# jan_integration.py
import requests
import json
from typing import Dict, Any, Optional

class JanAPI:
    """Jan Desktop API client"""
    
    def __init__(self, base_url: str = "http://localhost:1337/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def chat_completion(self, messages: list, model: str = "llama3.2", 
                       temperature: float = 0.7, max_tokens: int = 2048) -> Dict[str, Any]:
        """Send chat completion request to Jan"""
        
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Jan API error: {e}")
    
    def list_models(self) -> list:
        """List available models in Jan"""
        url = f"{self.base_url}/models"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.RequestException as e:
            raise Exception(f"Jan API error: {e}")
    
    def stream_chat(self, messages: list, model: str = "llama3.2"):
        """Stream chat response from Jan"""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        try:
            response = self.session.post(url, json=payload, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str != '[DONE]':
                            try:
                                data = json.loads(data_str)
                                delta = data.get('choices', [{}])[0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
                                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Jan API error: {e}")

# Example usage
def chat_with_jan():
    """Example Jan API usage"""
    jan = JanAPI()
    
    # List available models
    models = jan.list_models()
    print("Available models:", [m["id"] for m in models])
    
    # Chat conversation
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant for PC automation tools."},
        {"role": "user", "content": "Explain how to use AutoGen for multi-agent conversations"}
    ]
    
    # Get response
    response = jan.chat_completion(messages)
    print("Jan response:", response["choices"][0]["message"]["content"])
    
    # Stream response
    print("Streaming response:")
    for chunk in jan.stream_chat(messages):
        print(chunk, end="", flush=True)

if __name__ == "__main__":
    chat_with_jan()
```

### Integration with Unified Orchestrator

```python
# In llmstack/ai_frameworks_integration.py
class JanAgent:
    """Jan Desktop Agent wrapper"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.jan_api = JanAPI()
        self.models_cache = None
        
    def initialize(self):
        """Initialize Jan connection"""
        try:
            # Test connection
            models = self.jan_api.list_models()
            self.models_cache = models
            logger.info(f"Jan initialized with {len(models)} models")
        except Exception as e:
            logger.error(f"Failed to initialize Jan: {e}")
    
    def chat(self, message: str, model: str = None) -> str:
        """Chat with Jan desktop app"""
        if not self.models_cache:
            self.initialize()
        
        model = model or self.config.model_name
        
        messages = [
            {
                "role": "system", 
                "content": "You are an AI assistant for PC automation tools and AI agent development."
            },
            {"role": "user", "content": message}
        ]
        
        try:
            response = self.jan_api.chat_completion(messages, model=model)
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Jan chat error: {e}")
            return f"Error: {e}"
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        if not self.models_cache:
            self.initialize()
        return [model["id"] for model in self.models_cache or []]
```

## 🎨 Customization

### 1. Custom Themes

Create custom theme for Jan:

```json
{
  "theme": {
    "name": "AI Tools Dark",
    "colors": {
      "primary": "#3b82f6",
      "secondary": "#1e293b", 
      "background": "#0f172a",
      "surface": "#1e293b",
      "text": "#f1f5f9",
      "accent": "#06b6d4"
    },
    "fonts": {
      "primary": "Inter",
      "code": "JetBrains Mono"
    }
  }
}
```

### 2. Custom Shortcuts

Configure keyboard shortcuts:

```json
{
  "shortcuts": {
    "newThread": "Ctrl+N",
    "clearThread": "Ctrl+L", 
    "exportThread": "Ctrl+E",
    "switchModel": "Ctrl+M",
    "settings": "Ctrl+,",
    "search": "Ctrl+F"
  }
}
```

### 3. Model Presets

Create model presets for different tasks:

```json
{
  "presets": {
    "coding": {
      "model": "codellama:7b",
      "temperature": 0.2,
      "system": "You are an expert programmer. Provide working code with explanations."
    },
    "writing": {
      "model": "mistral:7b", 
      "temperature": 0.8,
      "system": "You are a skilled technical writer. Create clear, engaging content."
    },
    "analysis": {
      "model": "llama3.2",
      "temperature": 0.3,
      "system": "You are an analytical AI. Provide thorough, factual analysis."
    }
  }
}
```

## 🧪 Testing Jan Setup

### 1. Basic Functionality Test

```python
# test_jan_basic.py
def test_jan_connection():
    """Test basic Jan functionality"""
    jan = JanAPI()
    
    try:
        # Test model listing
        models = jan.list_models()
        assert len(models) > 0, "No models available"
        print(f"✓ Jan has {len(models)} models available")
        
        # Test simple chat
        messages = [{"role": "user", "content": "Say hello"}]
        response = jan.chat_completion(messages)
        
        assert "choices" in response, "Invalid response format"
        assert len(response["choices"]) > 0, "No response choices"
        
        content = response["choices"][0]["message"]["content"]
        assert len(content) > 0, "Empty response"
        
        print("✓ Jan chat test passed")
        print(f"Response: {content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Jan test failed: {e}")
        return False

if __name__ == "__main__":
    test_jan_connection()
```

### 2. Model Performance Test

```python
# test_jan_performance.py
import time

def test_jan_performance():
    """Test Jan response times with different models"""
    jan = JanAPI()
    models = ["llama3.2:1b", "llama3.2:3b", "codellama:7b"]
    
    test_prompt = "Explain what Docker is in one sentence."
    messages = [{"role": "user", "content": test_prompt}]
    
    results = {}
    
    for model in models:
        try:
            start_time = time.time()
            response = jan.chat_completion(messages, model=model)
            end_time = time.time()
            
            duration = end_time - start_time
            content = response["choices"][0]["message"]["content"]
            
            results[model] = {
                "duration": duration,
                "response_length": len(content),
                "words_per_second": len(content.split()) / duration
            }
            
            print(f"✓ {model}: {duration:.2f}s, {results[model]['words_per_second']:.1f} words/sec")
            
        except Exception as e:
            print(f"✗ {model}: Error - {e}")
            results[model] = {"error": str(e)}
    
    return results

if __name__ == "__main__":
    test_jan_performance()
```

### 3. Integration Test

```python
# test_jan_integration.py
from llmstack.ai_frameworks_integration import JanAgent, AIConfig

def test_jan_integration():
    """Test Jan integration with repository"""
    
    config = AIConfig(
        model_name="llama3.2",
        use_local=True
    )
    
    jan_agent = JanAgent(config)
    jan_agent.initialize()
    
    # Test repository-aware conversation
    response = jan_agent.chat("What AI frameworks are available in this repository?")
    
    # Check for repository knowledge
    frameworks = ["autogen", "flowise", "openhands", "aider"]
    mentioned_frameworks = sum(1 for fw in frameworks if fw.lower() in response.lower())
    
    assert mentioned_frameworks >= 2, f"Only mentioned {mentioned_frameworks} frameworks"
    print(f"✓ Jan mentioned {mentioned_frameworks} repository frameworks")
    
    # Test model availability
    models = jan_agent.get_available_models()
    assert len(models) > 0, "No models available"
    print(f"✓ Jan has {len(models)} models available")
    
    return True

if __name__ == "__main__":
    test_jan_integration()
```

## 🛟 Troubleshooting

### Common Issues

#### 1. Jan Won't Start
```bash
# Check if port is available
netstat -an | grep 1337

# Kill conflicting processes
sudo kill -9 $(sudo lsof -t -i:1337)

# Clear Jan cache (Linux/Mac)
rm -rf ~/.jan/cache

# Windows
del /s /q "%APPDATA%\jan\cache\*"
```

#### 2. Models Not Loading
```bash
# Check available disk space
df -h

# Check Jan logs
# Linux/Mac: ~/.jan/logs/
# Windows: %APPDATA%\jan\logs\

# Manually download models
jan model pull llama3.2
```

#### 3. API Not Responding
```bash
# Check Jan API server status
curl http://localhost:1337/v1/models

# Restart Jan with API enabled
# Settings > Extensions > Local Server > Enable

# Check firewall settings
sudo ufw allow 1337
```

#### 4. Performance Issues
```json
// Reduce context length in settings
{
  "engine": {
    "nitro": {
      "ctx_len": 2048,  // Reduce from 4096
      "ngl": 16,        // Reduce GPU layers
      "cpu_threads": 2  // Reduce CPU threads
    }
  }
}
```

#### 5. Integration Issues
```python
# Test Jan API directly
import requests

response = requests.get("http://localhost:1337/v1/models")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

### Performance Optimization

#### 1. Model Selection
- **Quick responses**: Use 1B parameter models
- **Balanced performance**: Use 3B parameter models  
- **Best quality**: Use 7B+ parameter models
- **Coding tasks**: Use specialized code models

#### 2. Hardware Optimization
```json
{
  "engine": {
    "nitro": {
      "ngl": 32,           // GPU layers (if GPU available)
      "cpu_threads": 8,    // Match CPU cores
      "cont_batching": true,
      "flash_attn": true   // If supported
    }
  }
}
```

#### 3. Memory Management
```json
{
  "engine": {
    "nitro": {
      "ctx_len": 4096,     // Context length
      "n_batch": 512,      // Batch size
      "n_keep": 48,        // Tokens to keep
      "mlock": true        // Lock memory
    }
  }
}
```

## 🚀 Advanced Usage

### 1. Multi-Model Workflows

```python
# multi_model_jan.py
class MultiModelJanWorkflow:
    """Use multiple Jan models for different tasks"""
    
    def __init__(self):
        self.jan = JanAPI()
        self.models = {
            "fast": "llama3.2:1b",
            "balanced": "llama3.2:3b", 
            "detailed": "llama3.2:8b",
            "coding": "codellama:7b",
            "writing": "mistral:7b"
        }
    
    def process_request(self, request: str, task_type: str = "balanced"):
        """Process request with appropriate model"""
        model = self.models.get(task_type, self.models["balanced"])
        
        messages = [
            {"role": "system", "content": self.get_system_message(task_type)},
            {"role": "user", "content": request}
        ]
        
        return self.jan.chat_completion(messages, model=model)
    
    def get_system_message(self, task_type: str) -> str:
        """Get appropriate system message for task type"""
        system_messages = {
            "coding": "You are an expert programmer. Provide working code with explanations.",
            "writing": "You are a skilled technical writer. Create clear, engaging content.",
            "analysis": "You are an analytical AI. Provide thorough, factual analysis.",
            "fast": "You are a helpful assistant. Provide quick, concise responses.",
            "detailed": "You are an expert AI. Provide comprehensive, detailed responses."
        }
        
        return system_messages.get(task_type, "You are a helpful AI assistant.")

# Example usage
workflow = MultiModelJanWorkflow()

# Quick question
quick_response = workflow.process_request("What is Docker?", "fast")

# Detailed analysis
detailed_response = workflow.process_request("Analyze the benefits of microservices", "detailed")

# Code generation
code_response = workflow.process_request("Create a Python REST API", "coding")
```

### 2. Jan as Development Assistant

```python
# jan_dev_assistant.py
class JanDevelopmentAssistant:
    """Jan-powered development assistant"""
    
    def __init__(self):
        self.jan = JanAPI()
    
    def code_review(self, code: str) -> str:
        """Review code for issues and improvements"""
        messages = [
            {
                "role": "system",
                "content": "You are a senior software engineer. Review code for bugs, security issues, performance problems, and suggest improvements."
            },
            {
                "role": "user", 
                "content": f"Please review this code:\n\n```\n{code}\n```"
            }
        ]
        
        response = self.jan.chat_completion(messages, model="codellama:7b")
        return response["choices"][0]["message"]["content"]
    
    def generate_tests(self, function_code: str) -> str:
        """Generate unit tests for function"""
        messages = [
            {
                "role": "system",
                "content": "You are a test engineer. Generate comprehensive unit tests with edge cases."
            },
            {
                "role": "user",
                "content": f"Generate unit tests for this function:\n\n```\n{function_code}\n```"
            }
        ]
        
        response = self.jan.chat_completion(messages, model="codellama:7b")
        return response["choices"][0]["message"]["content"]
    
    def explain_code(self, code: str) -> str:
        """Explain how code works"""
        messages = [
            {
                "role": "system",
                "content": "You are a programming teacher. Explain code clearly and comprehensively."
            },
            {
                "role": "user",
                "content": f"Explain how this code works:\n\n```\n{code}\n```"
            }
        ]
        
        response = self.jan.chat_completion(messages, model="llama3.2")
        return response["choices"][0]["message"]["content"]

# Example usage
assistant = JanDevelopmentAssistant()

# Review code
code_to_review = """
def authenticate_user(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    return database.execute(query)
"""

review = assistant.code_review(code_to_review)
print("Code Review:", review)
```

## 📈 Next Steps

1. **Explore Model Hub**: Try different models for various tasks
2. **Create Custom Presets**: Build task-specific configurations
3. **API Integration**: Integrate Jan with your development workflow
4. **Team Sharing**: Share configurations and models with your team
5. **Advanced Features**: Explore extensions and plugins

## 🎓 Learning Resources

### Official Documentation
- [Jan Documentation](https://jan.ai/docs)
- [Jan GitHub Repository](https://github.com/janhq/jan)

### Repository Examples
- [Jan Integration](scripts/install_jan.sh)
- [AI Frameworks Integration](llmstack/ai_frameworks_integration.py)

### Community Resources
- [Jan Discord Community](https://discord.gg/jan)
- [Model Hub](https://jan.ai/models)

---

**🤖 Jan is now configured for desktop AI assistance!**

Enjoy a user-friendly ChatGPT-like interface with your local AI models for private, powerful AI conversations.