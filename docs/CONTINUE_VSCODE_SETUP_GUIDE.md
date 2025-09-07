# 💻 Continue VS Code Extension Setup Guide

Continue is a powerful VS Code extension that brings AI-powered coding assistance directly into your editor. This guide shows you how to set up Continue with local AI models for private, cost-effective AI coding assistance.

## 🚀 Quick Start

### Automatic Setup
```bash
# Install and configure Continue
bash scripts/install_continue.sh

# Configure with local models
python3 scripts/configure_providers.py --continue
```

### Manual Installation
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Continue"
4. Install the Continue extension
5. Configure with local models

## 📋 Prerequisites

- **VS Code** (latest version recommended)
- **Ollama** or **LocalAI** running locally
- **Python 3.8+** (for configuration scripts)
- **4GB+ RAM** for model inference

## 🔧 Configuration

### 1. Initial Setup

After installing the Continue extension:

1. Open VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Continue: Open config.json"
4. Select the command to open configuration

### 2. Local Model Configuration

Edit the Continue config file (`~/.continue/config.json`):

```json
{
  "models": [
    {
      "title": "Llama 3.2 (Local)",
      "provider": "ollama",
      "model": "llama3.2",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Code Llama (Local)",
      "provider": "ollama", 
      "model": "codellama:7b",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Mistral (Local)",
      "provider": "ollama",
      "model": "mistral:7b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Code Completion",
    "provider": "ollama",
    "model": "codellama:7b",
    "apiBase": "http://localhost:11434"
  },
  "customCommands": [
    {
      "name": "commit",
      "prompt": "Write a concise git commit message for these changes:\n\n{{{ diff }}}"
    },
    {
      "name": "docstring",
      "prompt": "Write a comprehensive docstring for this function:\n\n{{{ code }}}"
    },
    {
      "name": "explain",
      "prompt": "Explain how this code works:\n\n{{{ code }}}"
    },
    {
      "name": "optimize",
      "prompt": "Suggest optimizations for this code:\n\n{{{ code }}}"
    },
    {
      "name": "test",
      "prompt": "Write unit tests for this function:\n\n{{{ code }}}"
    },
    {
      "name": "refactor",
      "prompt": "Refactor this code for better readability and maintainability:\n\n{{{ code }}}"
    }
  ],
  "contextProviders": [
    {
      "name": "code",
      "params": {}
    },
    {
      "name": "docs",
      "params": {}
    },
    {
      "name": "diff",
      "params": {}
    },
    {
      "name": "terminal",
      "params": {}
    },
    {
      "name": "problems",
      "params": {}
    },
    {
      "name": "folder",
      "params": {}
    },
    {
      "name": "codebase",
      "params": {}
    }
  ],
  "slashCommands": [
    {
      "name": "edit",
      "description": "Edit selected code"
    },
    {
      "name": "comment", 
      "description": "Add comments to code"
    },
    {
      "name": "share",
      "description": "Share code snippet"
    },
    {
      "name": "cmd",
      "description": "Generate terminal command"
    }
  ],
  "allowAnonymousTelemetry": false,
  "embeddingsProvider": {
    "provider": "ollama",
    "model": "nomic-embed-text",
    "apiBase": "http://localhost:11434"
  }
}
```

### 3. Advanced Configuration

Create project-specific configuration in `.continue/config.json`:

```json
{
  "models": [
    {
      "title": "Project AI Assistant",
      "provider": "ollama",
      "model": "llama3.2",
      "apiBase": "http://localhost:11434",
      "systemMessage": "You are an AI assistant specialized in this project. You understand the codebase structure, coding patterns, and project requirements."
    }
  ],
  "customCommands": [
    {
      "name": "api-doc",
      "prompt": "Generate API documentation for this endpoint:\n\n{{{ code }}}\n\nInclude parameters, responses, and examples."
    },
    {
      "name": "debug",
      "prompt": "Help debug this code. Identify potential issues and suggest fixes:\n\n{{{ code }}}"
    },
    {
      "name": "security",
      "prompt": "Review this code for security vulnerabilities:\n\n{{{ code }}}"
    }
  ],
  "contextProviders": [
    {
      "name": "folder",
      "params": {
        "folders": ["src", "docs", "tests"]
      }
    }
  ]
}
```

## 🛠️ Using Continue

### Basic Commands

#### 1. Chat Interface
- Press `Ctrl+I` (or `Cmd+I` on Mac) to open Continue chat
- Ask questions about your code
- Get explanations and suggestions

#### 2. Code Editing
- Select code in the editor
- Press `Ctrl+I` to edit with AI
- Describe the changes you want

#### 3. Tab Completion
- Start typing code
- Continue will suggest completions
- Press `Tab` to accept suggestions

### Custom Commands

#### Using Slash Commands
```
/edit - Edit selected code with AI assistance
/comment - Add detailed comments to code
/explain - Get explanations for complex code
/test - Generate unit tests
/commit - Generate git commit messages
```

#### Custom Command Examples

**Generate Documentation:**
```python
# Select this function and use /docstring command
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
```

**Code Review:**
```python
# Select code and use /security command
user_input = input("Enter your password: ")
query = f"SELECT * FROM users WHERE password = '{user_input}'"
```

**Generate Tests:**
```python
# Select function and use /test command
def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

## 🔄 Integration with Repository

### Repository-Specific Configuration

Create `.vscode/settings.json` in your project:

```json
{
  "continue.enableTabAutocomplete": true,
  "continue.enableInlineCompletion": true,
  "continue.maxAutocompleteTokens": 100,
  "continue.debounceDelay": 500,
  "continue.customCommands": {
    "ai-tools-doc": {
      "prompt": "Document this AI tool function with usage examples:\n\n{{{ code }}}"
    },
    "docker-gen": {
      "prompt": "Generate a Dockerfile for this application:\n\n{{{ code }}}"
    },
    "config-explain": {
      "prompt": "Explain this configuration file in the context of AI automation tools:\n\n{{{ code }}}"
    }
  }
}
```

### Integration with AI Frameworks

```python
# scripts/configure_continue.py
import json
import os
from pathlib import Path
from typing import Dict, Any

class ContinueConfigurator:
    """Configure Continue extension for AI tools repository"""
    
    def __init__(self):
        self.continue_dir = Path.home() / ".continue"
        self.config_file = self.continue_dir / "config.json"
        self.ensure_config_dir()
    
    def ensure_config_dir(self):
        """Ensure Continue config directory exists"""
        self.continue_dir.mkdir(exist_ok=True)
    
    def generate_ai_tools_config(self) -> Dict[str, Any]:
        """Generate Continue config optimized for AI tools development"""
        
        config = {
            "models": [
                {
                    "title": "AI Tools Assistant",
                    "provider": "ollama",
                    "model": "llama3.2",
                    "apiBase": "http://localhost:11434",
                    "systemMessage": self.get_ai_tools_system_message()
                },
                {
                    "title": "Code Generator",
                    "provider": "ollama", 
                    "model": "codellama:7b",
                    "apiBase": "http://localhost:11434"
                },
                {
                    "title": "Documentation Writer",
                    "provider": "ollama",
                    "model": "mistral:7b", 
                    "apiBase": "http://localhost:11434"
                }
            ],
            "tabAutocompleteModel": {
                "title": "Code Completion",
                "provider": "ollama",
                "model": "codellama:7b",
                "apiBase": "http://localhost:11434"
            },
            "customCommands": self.get_ai_tools_commands(),
            "contextProviders": [
                {"name": "code", "params": {}},
                {"name": "docs", "params": {}},
                {"name": "diff", "params": {}},
                {"name": "folder", "params": {"folders": ["llmstack", "scripts", "docs"]}},
                {"name": "codebase", "params": {}}
            ],
            "allowAnonymousTelemetry": False,
            "embeddingsProvider": {
                "provider": "ollama",
                "model": "nomic-embed-text",
                "apiBase": "http://localhost:11434"
            }
        }
        
        return config
    
    def get_ai_tools_system_message(self) -> str:
        """Get system message for AI tools context"""
        return """You are an AI assistant specialized in PC automation tools and AI agent development.

You have expertise in:
- AutoGen multi-agent systems
- Flowise visual workflows
- OpenHands coding assistance  
- Aider AI pair programming
- MemGPT persistent memory agents
- CAMEL-AI role-playing agents
- Docker deployment patterns
- Ollama local model management
- Prometheus/Grafana monitoring
- AI framework integration

When helping with code:
- Follow repository patterns and conventions
- Include proper error handling and logging
- Use type hints and comprehensive docstrings
- Consider performance and resource usage
- Suggest appropriate AI models for tasks
- Include integration with the unified orchestrator when relevant

You understand the repository structure and can provide context-aware suggestions."""
    
    def get_ai_tools_commands(self) -> list:
        """Get custom commands for AI tools development"""
        return [
            {
                "name": "agent-create",
                "prompt": "Create an AI agent using the repository patterns:\n\n{{{ code }}}\n\nInclude proper initialization, error handling, and integration with the unified orchestrator."
            },
            {
                "name": "docker-service",
                "prompt": "Generate a Docker service configuration for this component:\n\n{{{ code }}}\n\nInclude health checks, monitoring, and follow repository deployment patterns."
            },
            {
                "name": "ai-config",
                "prompt": "Create a configuration for this AI component:\n\n{{{ code }}}\n\nUse the AIConfig dataclass pattern and include local model settings."
            },
            {
                "name": "monitor-add",
                "prompt": "Add monitoring and metrics to this code:\n\n{{{ code }}}\n\nInclude Prometheus metrics, logging, and health checks."
            },
            {
                "name": "test-ai",
                "prompt": "Create comprehensive tests for this AI component:\n\n{{{ code }}}\n\nInclude unit tests, integration tests, and mock configurations."
            },
            {
                "name": "doc-guide",
                "prompt": "Create documentation following repository standards:\n\n{{{ code }}}\n\nInclude emoji headers, troubleshooting section, and practical examples."
            }
        ]
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to Continue config file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Continue configuration saved to {self.config_file}")
    
    def setup_ai_tools_configuration(self):
        """Setup Complete configuration for AI tools development"""
        config = self.generate_ai_tools_config()
        self.save_config(config)
        
        print("✓ Continue configured for AI tools development")
        print("✓ Restart VS Code to apply changes")
        print("✓ Press Ctrl+I to start using Continue")

def main():
    """Configure Continue for AI tools development"""
    configurator = ContinueConfigurator()
    configurator.setup_ai_tools_configuration()

if __name__ == "__main__":
    main()
```

## 🧪 Testing Continue Setup

### 1. Basic Functionality Test

1. Open VS Code in your project
2. Press `Ctrl+I` to open Continue chat
3. Type: "Explain the structure of this repository"
4. Verify Continue responds with repository understanding

### 2. Code Completion Test

1. Create a new Python file
2. Start typing:
   ```python
   def create_ai_agent(
   ```
3. Continue should suggest completions
4. Press `Tab` to accept

### 3. Custom Commands Test

1. Select a function in your code
2. Press `Ctrl+I`
3. Type `/test` to generate tests
4. Verify tests are generated appropriately

### 4. Context Awareness Test

```python
# test_continue_context.py
"""Test Continue's understanding of repository context"""

# Select this code and ask Continue to explain
from llmstack.ai_frameworks_integration import AutoGenAgent, AIConfig

def setup_autogen_agent():
    config = AIConfig(
        model_name="llama3.2",
        localai_endpoint="http://localhost:11434/v1",
        use_local=True
    )
    
    agent = AutoGenAgent(config)
    return agent

# Ask Continue: "How does this integrate with the repository's AI stack?"
```

## 🎯 Productivity Tips

### 1. Effective Prompting

**Good prompts:**
```
- "Refactor this function to use async/await"
- "Add error handling for network requests"
- "Generate docstring with type hints and examples"
- "Optimize this loop for better performance"
```

**Repository-specific prompts:**
```
- "Integrate this with the unified orchestrator"
- "Add Prometheus metrics to this function"
- "Create AutoGen agent for this task"
- "Add Docker health check for this service"
```

### 2. Workflow Integration

**Daily Development Workflow:**
1. Use Continue for code generation and completion
2. Ask for explanations of complex code
3. Generate tests with `/test` command
4. Create documentation with `/doc-guide`
5. Review code security with `/security`

**Code Review Workflow:**
1. Select changed code
2. Use `/explain` to understand changes
3. Use `/optimize` for improvement suggestions
4. Use `/security` for security review

### 3. Model Selection

**For different tasks:**
- **Code completion**: CodeLlama 7B (fast, accurate)
- **Explanations**: Llama 3.2 (comprehensive understanding)
- **Documentation**: Mistral 7B (good writing quality)
- **Quick questions**: Llama 3.2 1B (fast responses)

## 🛟 Troubleshooting

### Common Issues

#### 1. Continue Not Responding
```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Check models are available
ollama list

# Restart VS Code
code --relaunch
```

#### 2. Slow Code Completion
```json
// In Continue config, reduce tokens
"tabAutocompleteModel": {
  "title": "Fast Completion",
  "provider": "ollama",
  "model": "codellama:7b",
  "apiBase": "http://localhost:11434",
  "completionOptions": {
    "maxTokens": 50,
    "temperature": 0.2
  }
}
```

#### 3. Configuration Issues
```bash
# Check Continue config location
ls ~/.continue/

# Validate JSON config
python -m json.tool ~/.continue/config.json

# Reset to default
rm ~/.continue/config.json
# Restart VS Code and reconfigure
```

#### 4. Context Not Working
```json
// Ensure proper context providers
"contextProviders": [
  {
    "name": "codebase",
    "params": {
      "nRetrieve": 25,
      "nFinal": 5
    }
  }
]
```

### Performance Optimization

#### 1. Reduce Model Size
```json
"models": [
  {
    "title": "Fast Assistant",
    "provider": "ollama",
    "model": "llama3.2:1b",  // Smaller model
    "apiBase": "http://localhost:11434"
  }
]
```

#### 2. Optimize Completion Settings
```json
"tabAutocompleteModel": {
  "provider": "ollama",
  "model": "codellama:7b",
  "completionOptions": {
    "temperature": 0.1,     // More deterministic
    "maxTokens": 30,        // Fewer tokens
    "stop": ["\n\n", "```"] // Better stopping
  }
}
```

#### 3. Limit Context
```json
"contextProviders": [
  {
    "name": "code",
    "params": {
      "maxChars": 10000  // Limit context size
    }
  }
]
```

## 🚀 Advanced Features

### 1. Custom Context Providers

```python
# Create custom context provider for AI tools
{
  "name": "ai-tools-context",
  "params": {
    "includePatterns": ["*.py", "*.yml", "*.md"],
    "excludePatterns": ["node_modules/**", "*.pyc"],
    "maxFiles": 50
  }
}
```

### 2. Workflow Automation

```json
{
  "customCommands": [
    {
      "name": "full-setup",
      "prompt": "Based on this code, generate:\n1. Comprehensive tests\n2. Documentation\n3. Docker configuration\n4. Monitoring setup\n\nCode:\n{{{ code }}}"
    }
  ]
}
```

### 3. Integration Scripts

```python
# scripts/continue_helpers.py
import json
import subprocess
from pathlib import Path

def sync_continue_config():
    """Sync Continue config with repository changes"""
    config_path = Path.home() / ".continue" / "config.json"
    
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        
        # Update system message with latest repository info
        for model in config.get("models", []):
            if "AI Tools Assistant" in model.get("title", ""):
                model["systemMessage"] = get_updated_system_message()
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✓ Continue config updated")

def get_updated_system_message():
    """Get updated system message based on current repository state"""
    # Implementation to analyze repository and update context
    return "Updated system message with current repository state..."

if __name__ == "__main__":
    sync_continue_config()
```

## 📈 Next Steps

1. **Master Custom Commands**: Create domain-specific commands for your workflow
2. **Explore Context Providers**: Optimize context for better suggestions
3. **Integrate with CI/CD**: Use Continue for automated code review
4. **Team Configuration**: Share configurations across your development team
5. **Advanced Prompting**: Develop sophisticated prompts for complex tasks

## 🎓 Learning Resources

### Official Documentation
- [Continue Documentation](https://continue.dev/docs)
- [Continue GitHub Repository](https://github.com/continuedev/continue)

### Repository Examples
- [Continue Configuration](scripts/install_continue.sh)
- [AI Tools Integration](llmstack/ai_frameworks_integration.py)

### VS Code Resources
- [VS Code Extension API](https://code.visualstudio.com/api)
- [VS Code Settings Reference](https://code.visualstudio.com/docs/getstarted/settings)

---

**💻 Continue is now configured for AI-powered coding in VS Code!**

Start coding with AI assistance directly in your editor and experience enhanced productivity with intelligent code completion and generation.