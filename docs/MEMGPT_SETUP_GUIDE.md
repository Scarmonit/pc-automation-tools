# 🧠 MemGPT Long-Term Memory Agent Setup Guide

MemGPT brings persistent memory to AI agents, allowing them to remember conversations, learn from interactions, and maintain context across sessions. This guide shows you how to set up MemGPT with local models for private, memory-enabled AI agents.

## 🚀 Quick Start

### Automatic Setup
```bash
# Install MemGPT and configure
pip install pymemgpt

# Configure with local models
memgpt configure

# Start your first persistent agent
memgpt run
```

### Docker Setup (Recommended)
```bash
# Using Docker for isolation
docker run -d \
  --name memgpt \
  -p 8283:8283 \
  -v memgpt_data:/root/.memgpt \
  --restart unless-stopped \
  memgpt/memgpt:latest
```

## 📋 Prerequisites

- **Python 3.10+** (MemGPT requires newer Python)
- **Ollama** or **LocalAI** running locally
- **8GB+ RAM** (for memory management)
- **SQLite** or **PostgreSQL** (for memory storage)
- **Docker** (optional but recommended)

## 🔧 Configuration

### 1. Initial Configuration

```bash
# Configure MemGPT
memgpt configure

# Follow prompts to set up:
# - Model provider (OpenAI-compatible/Ollama)
# - Embedding provider
# - Storage backend
```

### 2. Local Model Configuration

```bash
# Configure for Ollama
memgpt configure --provider openai \
  --model llama3.2 \
  --model-endpoint http://localhost:11434/v1 \
  --model-wrapper chatml

# Configure embeddings
memgpt configure --provider openai \
  --embedding-model nomic-embed-text \
  --embedding-endpoint http://localhost:11434/v1
```

### 3. Advanced Configuration File

Create `~/.memgpt/config.yaml`:

```yaml
# MemGPT Configuration
model:
  provider: openai
  model: llama3.2
  model_endpoint: http://localhost:11434/v1
  model_wrapper: chatml
  context_window: 8192

embedding:
  provider: openai
  embedding_model: nomic-embed-text
  embedding_endpoint: http://localhost:11434/v1
  embedding_dim: 768

storage:
  type: sqlite
  path: ~/.memgpt/sqlite.db

# Memory configuration
memory:
  persona_char_limit: 2048
  human_char_limit: 2048
  memory_char_limit: 2048

# Agent settings
agent:
  preset: memgpt_chat
  model: llama3.2
  context_window: 8192
```

## 🎯 Creating Your First Memory-Enabled Agent

### Basic Agent Creation

```bash
# Create a new agent
memgpt run --agent my_assistant

# Or create with specific configuration
memgpt run --agent coding_assistant \
  --preset memgpt_chat \
  --model llama3.2 \
  --persona "You are an expert software developer with extensive experience in Python, Docker, and AI systems."
```

### Custom Agent Setup

```python
# Using Python API
from memgpt import MemGPT
from memgpt.config import Config

# Initialize with local config
config = Config.load()
agent = MemGPT(
    agent_name="coding_assistant",
    model="llama3.2",
    persona="You are an expert software developer specializing in AI systems and automation tools.",
    human="A developer working on PC automation tools and AI agent frameworks."
)

# Start conversation
response = agent.user_message("Help me understand the architecture of this AI automation system.")
print(response)
```

## 🧱 Memory Architecture

### Understanding MemGPT Memory

MemGPT uses a hierarchical memory system:

1. **Core Memory** - Always accessible (persona + human description)
2. **Recall Memory** - Recent conversation history
3. **Archival Memory** - Long-term searchable storage

### Memory Management Commands

```bash
# In MemGPT chat
/memory          # View current memory status
/core            # Edit core memory
/recall          # View recall memory  
/archival        # Search archival memory
/save            # Save current state
/load            # Load previous state
```

## 🛠️ Advanced Features

### 1. Custom Memory Functions

```python
# Custom memory management
class CustomMemoryAgent:
    def __init__(self, agent_name):
        self.agent = MemGPT(agent_name=agent_name)
        self.knowledge_base = {}
    
    def add_to_knowledge(self, topic, information):
        """Add structured information to knowledge base"""
        self.knowledge_base[topic] = information
        
        # Also add to MemGPT archival memory
        self.agent.memory.archival_memory.insert(
            f"Knowledge about {topic}: {information}"
        )
    
    def retrieve_knowledge(self, query):
        """Retrieve relevant knowledge"""
        # Search both local knowledge and MemGPT memory
        local_results = [
            (topic, info) for topic, info in self.knowledge_base.items()
            if query.lower() in topic.lower() or query.lower() in info.lower()
        ]
        
        # Search MemGPT archival memory
        memgpt_results = self.agent.memory.archival_memory.search(query)
        
        return {
            "local": local_results,
            "archival": memgpt_results
        }
```

### 2. Integration with Repository

```python
# In llmstack/ai_frameworks_integration.py
class MemGPTAgent:
    """Enhanced MemGPT Agent with repository integration"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.agent = None
        self.initialize()
    
    def initialize(self):
        """Initialize MemGPT with local models"""
        try:
            from memgpt import MemGPT
            
            self.agent = MemGPT(
                agent_name="repository_assistant",
                model=self.config.model_name,
                persona="""You are an AI assistant specialized in PC automation tools.
                You have deep knowledge of:
                - AutoGen multi-agent systems
                - Flowise visual workflows  
                - OpenHands coding assistance
                - Docker deployment patterns
                - Local AI model management
                
                Remember our conversations and build on previous knowledge.""",
                human="A developer working with AI automation tools and agent frameworks."
            )
            
            # Add repository context to memory
            self.add_repository_context()
            
        except Exception as e:
            logger.error(f"Failed to initialize MemGPT: {e}")
    
    def add_repository_context(self):
        """Add repository-specific context to memory"""
        context_items = [
            "Repository contains AutoGen, Flowise, OpenHands, Aider, and other AI tools",
            "Uses Ollama for local model inference with llama3.2, mistral, codellama models",
            "Docker-based deployment with monitoring via Prometheus and Grafana", 
            "Unified orchestrator manages multiple AI frameworks",
            "GitHub Copilot integration provides repository-aware code completion"
        ]
        
        for item in context_items:
            self.agent.memory.archival_memory.insert(item)
    
    def chat_with_memory(self, message: str) -> str:
        """Chat with memory context"""
        if not self.agent:
            return "MemGPT agent not initialized"
        
        try:
            response = self.agent.user_message(message)
            return response
        except Exception as e:
            logger.error(f"MemGPT chat error: {e}")
            return f"Error: {e}"
    
    def search_memory(self, query: str) -> List[str]:
        """Search agent's memory"""
        if not self.agent:
            return []
        
        try:
            results = self.agent.memory.archival_memory.search(query)
            return [str(result) for result in results]
        except Exception as e:
            logger.error(f"Memory search error: {e}")
            return []
```

### 3. Persistent Learning System

```python
# learning_agent.py
class LearningMemGPTAgent:
    """Agent that learns and improves over time"""
    
    def __init__(self, agent_name, domain="general"):
        self.agent = MemGPT(agent_name=agent_name)
        self.domain = domain
        self.learning_log = []
    
    def learn_from_interaction(self, user_input, agent_response, feedback=None):
        """Learn from each interaction"""
        learning_entry = {
            "input": user_input,
            "response": agent_response,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain
        }
        
        self.learning_log.append(learning_entry)
        
        # Add to archival memory
        memory_entry = f"Learned from interaction: {user_input} -> {agent_response}"
        if feedback:
            memory_entry += f" (Feedback: {feedback})"
            
        self.agent.memory.archival_memory.insert(memory_entry)
    
    def get_relevant_experience(self, current_input):
        """Find relevant past experiences"""
        similar_entries = self.agent.memory.archival_memory.search(current_input)
        
        # Also search local learning log
        local_matches = [
            entry for entry in self.learning_log
            if any(word in entry["input"].lower() for word in current_input.lower().split())
        ]
        
        return {
            "archival": similar_entries,
            "recent": local_matches[-5:]  # Last 5 relevant entries
        }
```

## 🧪 Testing MemGPT Setup

### 1. Basic Memory Test

```bash
# Start agent
memgpt run --agent test_agent

# Test conversation continuity
User: My name is John and I work on AI automation tools.
Agent: Nice to meet you, John! I'll remember that you work on AI automation tools.

# Exit and restart
/exit
memgpt run --agent test_agent

# Test memory persistence
User: What do you remember about me?
Agent: I remember that your name is John and you work on AI automation tools.
```

### 2. Memory Capacity Test

```python
# test_memgpt_memory.py
from memgpt import MemGPT
import time

def test_memory_persistence():
    """Test that MemGPT maintains memory across sessions"""
    
    # First session
    agent = MemGPT(agent_name="memory_test")
    
    # Add information
    test_facts = [
        "The repository uses Docker for deployment",
        "Ollama runs on port 11434", 
        "AutoGen handles multi-agent conversations",
        "Flowise provides visual workflow building",
        "OpenHands offers AI coding assistance"
    ]
    
    for fact in test_facts:
        agent.user_message(f"Remember this: {fact}")
    
    # Save and create new session
    del agent
    time.sleep(1)
    
    # New session
    agent = MemGPT(agent_name="memory_test")
    
    # Test recall
    response = agent.user_message("What do you know about this repository's architecture?")
    
    # Check if facts are recalled
    recalled_facts = sum(1 for fact in test_facts if any(word in response.lower() for word in fact.lower().split()))
    
    print(f"Recalled {recalled_facts}/{len(test_facts)} facts")
    return recalled_facts >= len(test_facts) * 0.8  # 80% recall threshold

if __name__ == "__main__":
    success = test_memory_persistence()
    print(f"Memory test {'PASSED' if success else 'FAILED'}")
```

### 3. Integration Test

```python
# test_memgpt_integration.py
from llmstack.ai_frameworks_integration import MemGPTAgent, AIConfig

def test_repository_integration():
    """Test MemGPT integration with repository"""
    
    config = AIConfig(
        model_name="llama3.2",
        localai_endpoint="http://localhost:11434/v1",
        use_local=True
    )
    
    agent = MemGPTAgent(config)
    
    # Test repository knowledge
    response = agent.chat_with_memory("What AI frameworks are available in this repository?")
    
    expected_frameworks = ["autogen", "flowise", "openhands", "aider"]
    mentioned_frameworks = sum(1 for fw in expected_frameworks if fw.lower() in response.lower())
    
    print(f"Mentioned {mentioned_frameworks}/{len(expected_frameworks)} frameworks")
    
    # Test memory search
    search_results = agent.search_memory("docker deployment")
    print(f"Found {len(search_results)} memory entries about Docker")
    
    return mentioned_frameworks >= 2 and len(search_results) > 0

if __name__ == "__main__":
    success = test_repository_integration()
    print(f"Integration test {'PASSED' if success else 'FAILED'}")
```

## 📊 Memory Management

### Memory Optimization

```python
# memory_optimizer.py
class MemoryOptimizer:
    """Optimize MemGPT memory usage"""
    
    def __init__(self, agent):
        self.agent = agent
    
    def compress_old_memories(self, days_old=30):
        """Compress memories older than specified days"""
        # Implementation depends on MemGPT's memory API
        pass
    
    def prioritize_memories(self, importance_threshold=0.7):
        """Keep only high-importance memories in active recall"""
        # Implementation would analyze memory relevance
        pass
    
    def export_knowledge_base(self, format="json"):
        """Export knowledge for backup or analysis"""
        memories = self.agent.memory.archival_memory.get_all()
        
        if format == "json":
            import json
            return json.dumps([str(memory) for memory in memories], indent=2)
        
        return memories
    
    def import_knowledge_base(self, knowledge_data):
        """Import external knowledge into memory"""
        if isinstance(knowledge_data, str):
            import json
            knowledge_data = json.loads(knowledge_data)
        
        for item in knowledge_data:
            self.agent.memory.archival_memory.insert(str(item))
```

### Memory Analytics

```python
# memory_analytics.py
class MemoryAnalytics:
    """Analyze MemGPT memory patterns"""
    
    def __init__(self, agent):
        self.agent = agent
    
    def analyze_memory_usage(self):
        """Analyze memory usage patterns"""
        core_memory = self.agent.memory.get_core_memory()
        recall_memory = self.agent.memory.get_recall_memory()
        archival_count = len(self.agent.memory.archival_memory.get_all())
        
        return {
            "core_memory_length": len(str(core_memory)),
            "recall_memory_length": len(str(recall_memory)),
            "archival_memory_count": archival_count,
            "memory_utilization": self.calculate_utilization()
        }
    
    def find_memory_gaps(self, topic_list):
        """Identify gaps in memory coverage"""
        gaps = []
        
        for topic in topic_list:
            results = self.agent.memory.archival_memory.search(topic)
            if len(results) == 0:
                gaps.append(topic)
        
        return gaps
    
    def calculate_utilization(self):
        """Calculate memory system utilization"""
        # Implementation would calculate memory efficiency metrics
        return 0.75  # Placeholder
```

## 🛟 Troubleshooting

### Common Issues

#### 1. Installation Problems
```bash
# Update Python (MemGPT requires 3.10+)
python --version

# Clean install
pip uninstall pymemgpt
pip install --no-cache-dir pymemgpt

# Or use conda
conda install -c conda-forge pymemgpt
```

#### 2. Configuration Issues
```bash
# Reset configuration
rm -rf ~/.memgpt/config.yaml
memgpt configure

# Check configuration
memgpt configure --show
```

#### 3. Memory Persistence Issues
```bash
# Check database
ls -la ~/.memgpt/

# Reset agent memory (WARNING: loses data)
memgpt delete --agent agent_name
```

#### 4. Model Connection Issues
```bash
# Test Ollama connection
curl http://localhost:11434/api/version

# Test with simple model
memgpt run --agent test --model llama3.2:1b
```

#### 5. Performance Issues
```bash
# Check memory usage
free -h

# Use smaller models
memgpt configure --model llama3.2:1b

# Optimize database
sqlite3 ~/.memgpt/sqlite.db "VACUUM;"
```

### Error Resolution

#### "Database locked" Error
```bash
# Kill existing processes
pkill -f memgpt

# Remove lock files
rm ~/.memgpt/*.lock

# Restart agent
memgpt run --agent your_agent
```

#### "Context window exceeded" Error
```python
# Implement context management
def manage_context_window(agent, max_tokens=7000):
    """Manage context window size"""
    current_context = agent.memory.get_recall_memory()
    
    if len(current_context) > max_tokens:
        # Summarize and compress older context
        agent.memory.compress_recall_memory()
```

#### "Embedding model not found" Error
```bash
# Install embedding model
ollama pull nomic-embed-text

# Or configure different embedding
memgpt configure --embedding-model all-MiniLM-L6-v2
```

## 🚀 Advanced Use Cases

### 1. Domain Expert Agent

```python
# Create specialized expert
expert_agent = MemGPT(
    agent_name="ai_tools_expert",
    persona="""You are a world-class expert in AI automation tools and frameworks. 
    You have deep knowledge of:
    - AutoGen multi-agent systems and conversation patterns
    - Flowise visual workflow design and best practices  
    - OpenHands coding assistance and project management
    - Docker deployment strategies for AI systems
    - Local AI model optimization and management
    
    You remember all our conversations and continuously build your expertise."""
)
```

### 2. Project Memory Assistant

```python
# Project-specific memory agent
class ProjectMemoryAssistant:
    def __init__(self, project_name):
        self.agent = MemGPT(
            agent_name=f"project_{project_name}",
            persona=f"You are a memory assistant for the {project_name} project."
        )
        self.project_name = project_name
    
    def log_decision(self, decision, rationale):
        """Log project decisions"""
        entry = f"Project decision: {decision}. Rationale: {rationale}"
        self.agent.memory.archival_memory.insert(entry)
    
    def recall_decisions(self, topic):
        """Recall past decisions"""
        return self.agent.memory.archival_memory.search(f"decision {topic}")
    
    def project_summary(self):
        """Generate project summary from memory"""
        return self.agent.user_message("Summarize the key decisions and progress for this project")
```

### 3. Learning and Adaptation

```python
# Self-improving agent
class AdaptiveMemGPTAgent:
    def __init__(self, agent_name):
        self.agent = MemGPT(agent_name=agent_name)
        self.performance_metrics = {}
    
    def learn_from_feedback(self, interaction_id, feedback_score, feedback_text):
        """Learn from user feedback"""
        learning_entry = f"Feedback for interaction {interaction_id}: Score {feedback_score}/10. {feedback_text}"
        self.agent.memory.archival_memory.insert(learning_entry)
        
        # Update performance metrics
        self.performance_metrics[interaction_id] = {
            "score": feedback_score,
            "feedback": feedback_text
        }
    
    def adapt_behavior(self):
        """Adapt behavior based on feedback patterns"""
        low_scores = [k for k, v in self.performance_metrics.items() if v["score"] < 6]
        
        if len(low_scores) > 5:
            improvement_prompt = "Based on recent feedback, I need to improve my responses. The common issues seem to be..."
            self.agent.user_message(improvement_prompt)
```

## 📈 Next Steps

1. **Master Memory Management**: Learn to effectively use core, recall, and archival memory
2. **Create Specialized Agents**: Build domain-specific agents with persistent knowledge
3. **Implement Learning Systems**: Add feedback loops and continuous improvement
4. **Scale Memory Operations**: Optimize for large-scale memory management
5. **Integrate with Other Tools**: Combine with AutoGen, Flowise, and other frameworks

## 🎓 Learning Resources

### Official Documentation
- [MemGPT Documentation](https://memgpt.readthedocs.io/)
- [MemGPT GitHub Repository](https://github.com/cpacker/MemGPT)

### Repository Examples
- [AI Frameworks Integration](llmstack/ai_frameworks_integration.py)
- [Unified Orchestrator](llmstack/unified_orchestrator.py)

### Research Papers
- [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560)

---

**🧠 MemGPT is now configured for persistent, memory-enabled AI agents!**

Start building agents that remember, learn, and grow smarter with every interaction.