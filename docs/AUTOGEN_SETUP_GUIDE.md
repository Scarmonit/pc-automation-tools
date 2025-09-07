# 🤖 AutoGen Multi-Agent Setup Guide

AutoGen enables powerful multi-agent conversations where AI agents collaborate to solve complex tasks. This guide walks you through setting up AutoGen with local AI models for cost-effective, private agent workflows.

## 🚀 Quick Start

### Automatic Setup
```bash
# Install AutoGen and configure with Ollama
bash scripts/install_agents.sh

# Test the installation
python3 llmstack/examples/04_autogen_agents.py
```

### Manual Setup
```bash
# Install AutoGen
pip install pyautogen

# Configure with local models
python3 scripts/configure_providers.py
```

## 📋 Prerequisites

- **Ollama** or **LocalAI** running locally
- **Python 3.8+** with pip
- **8GB+ RAM** recommended for multiple agents
- **Docker** (optional, for containerized deployment)

## 🔧 Configuration

### 1. Model Configuration

Create or update `~/.autogen/config.json`:

```json
{
  "model_list": [
    {
      "model": "llama3.2",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "api_type": "openai"
    },
    {
      "model": "mistral:7b",
      "base_url": "http://localhost:11434/v1", 
      "api_key": "ollama",
      "api_type": "openai"
    },
    {
      "model": "codellama:7b",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama", 
      "api_type": "openai"
    }
  ]
}
```

### 2. Environment Setup

```bash
# Set environment variables
export OPENAI_API_KEY="ollama"
export OPENAI_API_BASE="http://localhost:11434/v1"

# Or use LocalAI
export OPENAI_API_BASE="http://localhost:8080/v1"
```

## 🎯 Creating Your First Multi-Agent Team

### Basic Two-Agent Setup

```python
from autogen import AssistantAgent, UserProxyAgent

# Configure LLM
llm_config = {
    "config_list": [
        {
            "model": "llama3.2",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",
            "api_type": "openai"
        }
    ],
    "temperature": 0.7,
    "timeout": 120
}

# Create coding assistant agent
assistant = AssistantAgent(
    name="CodingAssistant",
    system_message="""You are a helpful AI coding assistant. 
    You write clean, efficient code with proper error handling and documentation.
    Always provide working code examples.""",
    llm_config=llm_config
)

# Create user proxy agent
user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={
        "work_dir": "coding_workspace",
        "use_docker": False
    }
)

# Start conversation
user_proxy.initiate_chat(
    assistant, 
    message="Create a Python function to calculate fibonacci numbers with memoization"
)
```

### Advanced Group Chat Setup

```python
from autogen import GroupChat, GroupChatManager

# Create specialized agents
planner = AssistantAgent(
    name="Planner",
    system_message="You are a project planner. Break down complex tasks into smaller steps.",
    llm_config=llm_config
)

coder = AssistantAgent(
    name="Coder", 
    system_message="You are an expert programmer. Write clean, efficient code.",
    llm_config=llm_config
)

reviewer = AssistantAgent(
    name="Reviewer",
    system_message="You are a code reviewer. Check for bugs, security issues, and best practices.",
    llm_config=llm_config
)

# Create group chat
group_chat = GroupChat(
    agents=[user_proxy, planner, coder, reviewer],
    messages=[],
    max_round=20
)

# Create group chat manager
manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config
)

# Start group conversation
user_proxy.initiate_chat(
    manager,
    message="Create a REST API for a todo application with authentication"
)
```

## 🛠️ Agent Patterns

### 1. Code Generation Team
```python
# Specialized agents for different tasks
architect = AssistantAgent(
    name="SoftwareArchitect",
    system_message="Design software architecture and choose appropriate technologies.",
    llm_config=llm_config
)

frontend_dev = AssistantAgent(
    name="FrontendDeveloper", 
    system_message="Expert in React, HTML, CSS, and JavaScript. Create responsive UIs.",
    llm_config=llm_config
)

backend_dev = AssistantAgent(
    name="BackendDeveloper",
    system_message="Expert in Python, FastAPI, databases. Build robust APIs.",
    llm_config=llm_config
)
```

### 2. Research and Analysis Team
```python
researcher = AssistantAgent(
    name="Researcher",
    system_message="Research topics thoroughly and gather accurate information.",
    llm_config=llm_config
)

analyst = AssistantAgent(
    name="DataAnalyst", 
    system_message="Analyze data, create visualizations, and provide insights.",
    llm_config=llm_config
)

writer = AssistantAgent(
    name="TechnicalWriter",
    system_message="Create clear, comprehensive documentation and reports.",
    llm_config=llm_config
)
```

### 3. DevOps Team
```python
deployer = AssistantAgent(
    name="DevOpsEngineer",
    system_message="Expert in Docker, CI/CD, cloud deployment, and infrastructure.",
    llm_config=llm_config
)

security = AssistantAgent(
    name="SecuritySpecialist",
    system_message="Focus on security best practices, vulnerability assessment.",
    llm_config=llm_config
)
```

## 🔄 Integration with Repository

### Using the Unified Orchestrator

```python
from llmstack.unified_orchestrator import UnifiedSystemOrchestrator

# Initialize orchestrator
orchestrator = UnifiedSystemOrchestrator()

# Use AutoGen for collaborative tasks
result = orchestrator.route_task(
    "Create a web application with team collaboration",
    routing_strategy="autogen"
)

# Multi-agent collaboration
collaboration_result = orchestrator.multi_agent_collaboration(
    "Build a complete AI chatbot application",
    agents=["autogen", "flowise", "localai"]
)
```

### Custom Agent Templates

```python
# Use repository patterns
from llmstack.ai_frameworks_integration import AutoGenAgent

# Create agent with repository configuration
agent = AutoGenAgent(config=ai_config)
agent.initialize()

# Start conversation
response = agent.chat("Create a microservice for user authentication")
```

## 🧪 Testing Your Setup

### 1. Basic Functionality Test
```bash
# Run the example script
python3 llmstack/examples/04_autogen_agents.py
```

### 2. Custom Test
```python
# test_autogen.py
import autogen

def test_autogen_connection():
    """Test AutoGen with local models"""
    llm_config = {
        "config_list": [
            {
                "model": "llama3.2",
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",
                "api_type": "openai"
            }
        ],
        "timeout": 60
    }
    
    assistant = autogen.AssistantAgent(
        name="TestAgent",
        system_message="You are a helpful assistant.",
        llm_config=llm_config
    )
    
    user_proxy = autogen.UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1
    )
    
    user_proxy.initiate_chat(assistant, message="Say hello!")
    print("✓ AutoGen is working correctly!")

if __name__ == "__main__":
    test_autogen_connection()
```

## 📊 Monitoring and Performance

### Agent Performance Metrics
```python
import time
from datetime import datetime

class AgentMetrics:
    def __init__(self):
        self.start_time = None
        self.responses = []
    
    def start_conversation(self):
        self.start_time = time.time()
    
    def log_response(self, agent_name, response_time, message_length):
        self.responses.append({
            "agent": agent_name,
            "response_time": response_time,
            "message_length": message_length,
            "timestamp": datetime.now()
        })
    
    def get_summary(self):
        total_time = time.time() - self.start_time
        avg_response_time = sum(r["response_time"] for r in self.responses) / len(self.responses)
        
        return {
            "total_conversation_time": total_time,
            "average_response_time": avg_response_time,
            "total_responses": len(self.responses)
        }
```

### Resource Usage
```bash
# Monitor system resources during agent conversations
htop
nvidia-smi  # If using GPU
docker stats  # If using Docker
```

## 🛟 Troubleshooting

### Common Issues

#### 1. Connection Errors
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Check available models
ollama list

# Pull required models if missing
ollama pull llama3.2
ollama pull mistral:7b
ollama pull codellama:7b
```

#### 2. Timeout Issues
```python
# Increase timeout in config
llm_config = {
    "config_list": [...],
    "timeout": 300,  # Increase to 5 minutes
    "request_timeout": 300
}
```

#### 3. Memory Issues
```bash
# Check memory usage
free -h

# Reduce number of concurrent agents
# Or use smaller models like llama3.2:1b
```

#### 4. Configuration Issues
```bash
# Verify config file
cat ~/.autogen/config.json

# Test with simple configuration
python3 -c "
import autogen
config = autogen.config_list_from_json('~/.autogen/config.json')
print('Config loaded successfully:', len(config), 'models')
"
```

### Performance Optimization

#### 1. Model Selection
```python
# Use appropriate model sizes
small_config = {"model": "llama3.2:1b"}  # Fast, less accurate
medium_config = {"model": "llama3.2:3b"}  # Balanced
large_config = {"model": "llama3.2:8b"}   # Slow, more accurate
```

#### 2. Agent Optimization
```python
# Limit conversation rounds
user_proxy = UserProxyAgent(
    name="UserProxy",
    max_consecutive_auto_reply=5,  # Reduce from default 10
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", "")
)
```

#### 3. Parallel Processing
```python
import asyncio
from autogen import Agent

async def run_parallel_agents(tasks):
    """Run multiple agent conversations in parallel"""
    results = await asyncio.gather(*[
        agent.achat(task) for task in tasks
    ])
    return results
```

## 🔗 Integration Examples

### With Flowise
```python
# Combine AutoGen with Flowise workflows
import requests

def trigger_flowise_flow(flow_id, data):
    """Trigger Flowise flow from AutoGen agent"""
    response = requests.post(
        f"http://localhost:3001/api/v1/prediction/{flow_id}",
        json={"question": data}
    )
    return response.json()

# Use in agent system message
system_message = """You can trigger Flowise workflows using trigger_flowise_flow(flow_id, data)
when you need additional processing capabilities."""
```

### With OpenHands
```python
# Route complex coding tasks to OpenHands
def route_to_openhands(task):
    """Route complex coding tasks to OpenHands"""
    # Implementation depends on OpenHands API
    pass
```

## 📚 Advanced Features

### 1. Custom Termination Conditions
```python
def custom_is_termination_msg(msg):
    """Custom termination logic"""
    content = msg.get("content", "").lower()
    return any(phrase in content for phrase in [
        "task completed",
        "finished successfully", 
        "no further action needed"
    ])

user_proxy = UserProxyAgent(
    name="UserProxy",
    is_termination_msg=custom_is_termination_msg
)
```

### 2. Code Execution Security
```python
# Safe code execution with Docker
code_execution_config = {
    "work_dir": "safe_workspace",
    "use_docker": True,
    "docker_image": "python:3.9-slim",
    "timeout": 120
}
```

### 3. Agent Memory
```python
# Implement simple memory for agents
class MemoryAgent(AssistantAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = []
    
    def save_to_memory(self, interaction):
        self.memory.append(interaction)
    
    def recall_memory(self, query):
        # Simple keyword-based memory recall
        relevant = [m for m in self.memory if query.lower() in str(m).lower()]
        return relevant[:3]  # Return top 3 relevant memories
```

## 📈 Next Steps

1. **Explore Multi-Agent Patterns**: Try different agent configurations for your use case
2. **Integrate with Other Tools**: Combine with Flowise, OpenHands, and other agents
3. **Custom Agent Development**: Create specialized agents for your domain
4. **Performance Optimization**: Fine-tune for your hardware and requirements
5. **Production Deployment**: Scale with Docker and monitoring

## 🎓 Learning Resources

### Official Documentation
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [AutoGen GitHub Repository](https://github.com/microsoft/autogen)

### Repository Examples
- [Basic AutoGen Examples](llmstack/examples/04_autogen_agents.py)
- [AI Frameworks Integration](llmstack/ai_frameworks_integration.py)
- [Unified Orchestrator](llmstack/unified_orchestrator.py)

### Community Resources
- [AutoGen Cookbook](https://github.com/microsoft/autogen/tree/main/notebook)
- [Multi-Agent Examples](https://github.com/microsoft/autogen/tree/main/samples)

---

**🎯 AutoGen is now configured for powerful multi-agent AI collaboration with your local models!**

Start building agent teams and experience the power of collaborative AI problem-solving.