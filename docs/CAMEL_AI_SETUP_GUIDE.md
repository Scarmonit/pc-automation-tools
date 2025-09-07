# 🐪 CAMEL-AI Multi-Agent Setup Guide

CAMEL-AI enables role-playing multi-agent conversations where AI agents take on specific personas to solve complex tasks through collaboration. This guide shows you how to set up CAMEL-AI with local models for sophisticated multi-agent scenarios.

## 🚀 Quick Start

### Automatic Setup
```bash
# Install CAMEL-AI
pip install camel-ai

# Configure with local models
python3 scripts/configure_providers.py --camel

# Test installation
python3 llmstack/examples/camel_demo.py
```

### Manual Installation
```bash
# Install CAMEL-AI with all extras
pip install "camel-ai[all]"

# Or minimal installation
pip install camel-ai
```

## 📋 Prerequisites

- **Python 3.8+** with pip
- **Ollama** or **LocalAI** running locally
- **8GB+ RAM** for multiple agent conversations
- **Git** for cloning examples and tools

## 🔧 Configuration

### 1. Environment Setup

```bash
# Set API endpoints for local models
export OPENAI_API_KEY="ollama"
export OPENAI_API_BASE="http://localhost:11434/v1"

# For LocalAI
export OPENAI_API_KEY="sk-localai"
export OPENAI_API_BASE="http://localhost:8080/v1"

# Optional: Set model preferences
export CAMEL_DEFAULT_MODEL="llama3.2"
export CAMEL_TEMPERATURE="0.7"
```

### 2. Basic Configuration

Create `~/.camel/config.yaml`:

```yaml
# CAMEL-AI Configuration
api:
  provider: "openai"
  base_url: "http://localhost:11434/v1"
  api_key: "ollama"
  model: "llama3.2"

agents:
  default_temperature: 0.7
  max_tokens: 2048
  timeout: 120

conversation:
  max_turns: 50
  termination_keywords:
    - "TERMINATE"
    - "TASK COMPLETED"
    - "FINISHED"

logging:
  level: "INFO"
  file: "~/.camel/logs/camel.log"
```

## 🎭 Role-Playing Agent Setup

### Basic Two-Agent Scenario

```python
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.societies import RolePlaying
from camel.types import TaskType, RoleType
from camel.configs import ChatGPTConfig

# Configure for local models
model_config = ChatGPTConfig(
    model="llama3.2",
    temperature=0.7,
    max_tokens=2048
)

def create_role_playing_session(task: str, assistant_role: str, user_role: str):
    """Create a role-playing session between two agents"""
    
    # Define the task
    task_prompt = f"""
    {task}
    
    Please work together to accomplish this task through conversation.
    The {assistant_role} should provide expertise and guidance.
    The {user_role} should ask questions and provide feedback.
    """
    
    # Initialize role-playing society
    role_play_session = RolePlaying(
        assistant_role_name=assistant_role,
        user_role_name=user_role,
        task_prompt=task_prompt,
        with_task_specify=True,
        task_type=TaskType.AI_SOCIETY,
        assistant_agent_kwargs={"model_config": model_config},
        user_agent_kwargs={"model_config": model_config}
    )
    
    return role_play_session

# Example usage
session = create_role_playing_session(
    task="Design a sustainable energy system for a small city",
    assistant_role="Environmental Engineer",
    user_role="City Planning Committee"
)

print("🎭 Starting role-playing session...")

# Run the conversation
chat_turn_limit = 10
n = 0

for assistant_msg, user_msg in session.step():
    n += 1
    print(f"\n--- Turn {n} ---")
    print(f"🔧 {session.assistant_role_name}: {assistant_msg.content}")
    print(f"🏛️  {session.user_role_name}: {user_msg.content}")
    
    if n >= chat_turn_limit:
        break

print("\n🎭 Role-playing session completed!")
```

### Advanced Multi-Agent Society

```python
from camel.societies import Society
from camel.agents import ChatAgent
from camel.types import RoleType
from typing import List, Dict

class MultiAgentSociety:
    """Advanced multi-agent society with specialized roles"""
    
    def __init__(self, model_config: ChatGPTConfig = None):
        self.model_config = model_config or ChatGPTConfig(
            model="llama3.2",
            temperature=0.7,
            max_tokens=2048
        )
        self.agents = {}
        self.conversation_history = []
    
    def create_agent(self, role_name: str, role_description: str, 
                    expertise: List[str] = None) -> ChatAgent:
        """Create a specialized agent with specific role and expertise"""
        
        system_message = f"""
        You are a {role_name} with the following background:
        {role_description}
        
        Your expertise includes: {', '.join(expertise or [])}
        
        Guidelines:
        - Stay in character and speak from your role's perspective
        - Provide valuable insights based on your expertise
        - Collaborate effectively with other team members
        - Be concise but thorough in your responses
        - Ask clarifying questions when needed
        """
        
        agent = ChatAgent(
            system_message=system_message,
            model_config=self.model_config
        )
        
        self.agents[role_name] = {
            "agent": agent,
            "description": role_description,
            "expertise": expertise or []
        }
        
        return agent
    
    def add_predefined_agents(self):
        """Add common predefined agent roles"""
        
        # Software Architect
        self.create_agent(
            role_name="Software Architect",
            role_description="Senior software architect with 15+ years experience designing scalable systems",
            expertise=["System Design", "Microservices", "Cloud Architecture", "Performance Optimization"]
        )
        
        # Product Manager
        self.create_agent(
            role_name="Product Manager",
            role_description="Product manager focused on user experience and business requirements",
            expertise=["User Research", "Market Analysis", "Feature Prioritization", "Stakeholder Management"]
        )
        
        # DevOps Engineer
        self.create_agent(
            role_name="DevOps Engineer",
            role_description="DevOps engineer specializing in deployment and infrastructure automation",
            expertise=["CI/CD", "Docker", "Kubernetes", "Infrastructure as Code", "Monitoring"]
        )
        
        # Security Specialist
        self.create_agent(
            role_name="Security Specialist",
            role_description="Cybersecurity expert focused on application and infrastructure security",
            expertise=["Threat Assessment", "Secure Coding", "Compliance", "Penetration Testing"]
        )
        
        # Data Scientist
        self.create_agent(
            role_name="Data Scientist",
            role_description="Data scientist with expertise in machine learning and analytics",
            expertise=["Machine Learning", "Statistical Analysis", "Data Visualization", "Predictive Modeling"]
        )
    
    def run_collaborative_session(self, project_description: str, 
                                 participants: List[str] = None,
                                 max_rounds: int = 15) -> List[Dict]:
        """Run collaborative session with specified participants"""
        
        if participants is None:
            participants = list(self.agents.keys())
        
        # Initialize conversation
        conversation = []
        current_topic = project_description
        
        print(f"🚀 Starting collaborative session: {project_description}")
        print(f"👥 Participants: {', '.join(participants)}")
        print("-" * 80)
        
        for round_num in range(max_rounds):
            print(f"\n🔄 Round {round_num + 1}")
            round_responses = []
            
            for participant in participants:
                if participant not in self.agents:
                    continue
                
                agent_info = self.agents[participant]
                agent = agent_info["agent"]
                
                # Create context-aware prompt
                context = self.build_context(conversation, current_topic, participant)
                
                try:
                    # Get agent response
                    response = agent.step(BaseMessage.make_user_message(
                        role_name=participant,
                        content=context
                    ))
                    
                    response_content = response.msg.content
                    
                    # Store response
                    response_data = {
                        "round": round_num + 1,
                        "agent": participant,
                        "role": agent_info["description"],
                        "response": response_content,
                        "expertise": agent_info["expertise"]
                    }
                    
                    conversation.append(response_data)
                    round_responses.append(response_data)
                    
                    print(f"\n👤 {participant}:")
                    print(f"💭 {response_content}")
                    
                except Exception as e:
                    print(f"⚠️  Error from {participant}: {e}")
                    continue
            
            # Check for natural conclusion
            if self.should_conclude_session(round_responses):
                print(f"\n✅ Session concluded naturally after {round_num + 1} rounds")
                break
        
        self.conversation_history = conversation
        return conversation
    
    def build_context(self, conversation: List[Dict], topic: str, current_agent: str) -> str:
        """Build context for agent based on conversation history"""
        
        context = f"Project: {topic}\n\n"
        
        if conversation:
            context += "Previous discussion:\n"
            # Include last few exchanges for context
            recent_conversation = conversation[-6:] if len(conversation) > 6 else conversation
            
            for entry in recent_conversation:
                if entry["agent"] != current_agent:  # Don't include own previous responses
                    context += f"{entry['agent']}: {entry['response'][:200]}...\n"
        
        context += f"\nAs the {current_agent}, provide your perspective and contributions to this project. "
        context += "Build on previous points and add your expertise."
        
        return context
    
    def should_conclude_session(self, round_responses: List[Dict]) -> bool:
        """Determine if session should naturally conclude"""
        
        conclusion_keywords = [
            "implementation plan complete",
            "all requirements covered",
            "ready to proceed",
            "comprehensive solution",
            "project fully defined"
        ]
        
        # Check if multiple agents indicate completion
        conclusion_indicators = 0
        for response in round_responses:
            content_lower = response["response"].lower()
            if any(keyword in content_lower for keyword in conclusion_keywords):
                conclusion_indicators += 1
        
        return conclusion_indicators >= 2  # At least 2 agents indicate completion
    
    def generate_project_summary(self) -> str:
        """Generate summary of the collaborative session"""
        
        if not self.conversation_history:
            return "No conversation history available."
        
        # Create summary prompt
        summary_prompt = """
        Based on the following collaborative discussion, create a comprehensive project summary:
        
        Include:
        1. Project overview and objectives
        2. Key insights from each expert
        3. Technical recommendations
        4. Implementation roadmap
        5. Risk considerations
        6. Next steps
        
        Discussion:
        """
        
        for entry in self.conversation_history:
            summary_prompt += f"\n{entry['agent']} ({entry['expertise'][0] if entry['expertise'] else 'General'}): "
            summary_prompt += f"{entry['response'][:300]}..."
        
        # Use one of the agents to generate summary
        if self.agents:
            first_agent = list(self.agents.values())[0]["agent"]
            summary_response = first_agent.step(BaseMessage.make_user_message(
                role_name="Summarizer",
                content=summary_prompt
            ))
            return summary_response.msg.content
        
        return "Unable to generate summary."

# Example usage
def run_collaborative_project():
    """Example collaborative project session"""
    
    # Initialize society
    society = MultiAgentSociety()
    society.add_predefined_agents()
    
    # Define project
    project = """
    Design and implement a real-time AI-powered customer service platform that can:
    - Handle multiple communication channels (chat, email, voice)
    - Integrate with existing CRM systems
    - Provide intelligent routing and escalation
    - Include analytics and reporting capabilities
    - Ensure high availability and scalability
    - Maintain data privacy and security compliance
    """
    
    # Run collaborative session
    conversation = society.run_collaborative_session(
        project_description=project,
        participants=["Software Architect", "Product Manager", "DevOps Engineer", "Security Specialist"],
        max_rounds=12
    )
    
    # Generate summary
    print("\n📋 Generating project summary...")
    summary = society.generate_project_summary()
    print("\n📄 PROJECT SUMMARY")
    print("=" * 80)
    print(summary)
    
    return conversation, summary

if __name__ == "__main__":
    conversation, summary = run_collaborative_project()
```

## 🔄 Integration with Repository

### CAMEL-AI in Unified Orchestrator

```python
# In llmstack/ai_frameworks_integration.py
class CAMELAgent:
    """CAMEL-AI Agent wrapper for repository integration"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.model_config = None
        self.current_society = None
        if CAMEL_AVAILABLE:
            self.initialize()
    
    def initialize(self):
        """Initialize CAMEL-AI with local models"""
        try:
            from camel.configs import ChatGPTConfig
            
            self.model_config = ChatGPTConfig(
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            # Set API configuration for local models
            if self.config.use_local:
                import openai
                openai.api_base = self.config.localai_endpoint
                openai.api_key = self.config.openai_api_key
            
            logger.info("CAMEL-AI initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CAMEL-AI: {e}")
    
    def create_role_playing_session(self, task: str, roles: Dict[str, str]) -> str:
        """Create role-playing session for specific task"""
        if not self.model_config:
            return "CAMEL-AI not initialized"
        
        try:
            from camel.societies import RolePlaying
            from camel.types import TaskType
            
            # Extract roles
            assistant_role = list(roles.keys())[0]
            user_role = list(roles.keys())[1] if len(roles) > 1 else "User"
            
            # Create role-playing session
            role_play_session = RolePlaying(
                assistant_role_name=assistant_role,
                user_role_name=user_role,
                task_prompt=task,
                with_task_specify=True,
                task_type=TaskType.AI_SOCIETY,
                assistant_agent_kwargs={"model_config": self.model_config},
                user_agent_kwargs={"model_config": self.model_config}
            )
            
            # Run conversation
            responses = []
            chat_turn_limit = 8  # Reasonable limit for API usage
            
            for n, (assistant_msg, user_msg) in enumerate(role_play_session.step()):
                if n >= chat_turn_limit:
                    break
                
                responses.append({
                    "turn": n + 1,
                    "assistant": {
                        "role": assistant_role,
                        "message": assistant_msg.content
                    },
                    "user": {
                        "role": user_role,
                        "message": user_msg.content
                    }
                })
            
            # Format response
            result = f"Role-playing session between {assistant_role} and {user_role}:\n\n"
            for response in responses:
                result += f"Turn {response['turn']}:\n"
                result += f"{assistant_role}: {response['assistant']['message'][:200]}...\n"
                result += f"{user_role}: {response['user']['message'][:200]}...\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"CAMEL role-playing error: {e}")
            return f"Error: {e}"
    
    def multi_agent_collaboration(self, project: str, agent_roles: List[str] = None) -> str:
        """Run multi-agent collaboration"""
        if not self.model_config:
            return "CAMEL-AI not initialized"
        
        agent_roles = agent_roles or [
            "Software Engineer",
            "Product Manager", 
            "System Architect"
        ]
        
        try:
            society = MultiAgentSociety(self.model_config)
            
            # Add requested agents
            for role in agent_roles:
                if role not in society.agents:
                    society.create_agent(
                        role_name=role,
                        role_description=f"Expert {role} contributing to the project",
                        expertise=[role.replace(" ", "_")]
                    )
            
            # Run collaborative session
            conversation = society.run_collaborative_session(
                project_description=project,
                participants=agent_roles,
                max_rounds=6  # Limit for API usage
            )
            
            # Generate summary
            summary = society.generate_project_summary()
            
            return summary
            
        except Exception as e:
            logger.error(f"CAMEL collaboration error: {e}")
            return f"Error: {e}"
```

## 🧪 Testing CAMEL-AI Setup

### 1. Basic Functionality Test

```python
# test_camel_basic.py
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.configs import ChatGPTConfig

def test_camel_basic():
    """Test basic CAMEL-AI functionality"""
    
    # Configure for local models
    model_config = ChatGPTConfig(
        model="llama3.2",
        temperature=0.7,
        max_tokens=1024
    )
    
    # Create agent
    agent = ChatAgent(
        system_message="You are a helpful assistant.",
        model_config=model_config
    )
    
    # Test simple interaction
    user_msg = BaseMessage.make_user_message(
        role_name="User",
        content="Hello, please introduce yourself."
    )
    
    response = agent.step(user_msg)
    
    print("✓ CAMEL-AI basic test passed")
    print(f"Response: {response.msg.content[:100]}...")
    
    return True

if __name__ == "__main__":
    test_camel_basic()
```

### 2. Role-Playing Test

```python
# test_camel_roleplay.py
def test_role_playing():
    """Test role-playing functionality"""
    
    session = create_role_playing_session(
        task="Plan a simple mobile app for task management",
        assistant_role="Senior Developer",
        user_role="Product Owner"
    )
    
    print("🎭 Testing role-playing session...")
    
    responses = []
    for n, (assistant_msg, user_msg) in enumerate(session.step()):
        if n >= 3:  # Just test a few turns
            break
        
        responses.append((assistant_msg.content, user_msg.content))
        print(f"Turn {n+1}: Assistant responded, User responded")
    
    assert len(responses) > 0, "No responses generated"
    print("✓ Role-playing test passed")
    
    return responses

if __name__ == "__main__":
    test_role_playing()
```

### 3. Integration Test

```python
# test_camel_integration.py
from llmstack.ai_frameworks_integration import CAMELAgent, AIConfig

def test_camel_integration():
    """Test CAMEL-AI integration with repository"""
    
    config = AIConfig(
        model_name="llama3.2",
        localai_endpoint="http://localhost:11434/v1",
        use_local=True
    )
    
    camel_agent = CAMELAgent(config)
    
    # Test role-playing
    result = camel_agent.create_role_playing_session(
        task="Design a simple REST API",
        roles={"Backend Developer": "Expert in API design", "Frontend Developer": "Expert in UI/UX"}
    )
    
    assert "Backend Developer" in result, "Role-playing session failed"
    print("✓ CAMEL integration test passed")
    
    return result

if __name__ == "__main__":
    test_camel_integration()
```

## 🎨 Advanced Use Cases

### 1. Educational Scenarios

```python
def create_educational_scenario(subject: str, student_level: str = "beginner"):
    """Create educational role-playing scenario"""
    
    session = create_role_playing_session(
        task=f"Teach {subject} concepts to a {student_level} level student through interactive conversation",
        assistant_role="Expert Teacher",
        user_role="Curious Student"
    )
    
    return session

# Example: Programming education
programming_session = create_educational_scenario("Python programming", "intermediate")
```

### 2. Business Strategy Sessions

```python
def business_strategy_session(business_scenario: str):
    """Run business strategy session with multiple stakeholders"""
    
    society = MultiAgentSociety()
    
    # Add business-focused agents
    society.create_agent(
        role_name="CEO",
        role_description="Chief Executive Officer focused on overall strategy and vision",
        expertise=["Strategic Planning", "Leadership", "Market Vision"]
    )
    
    society.create_agent(
        role_name="CFO", 
        role_description="Chief Financial Officer focused on financial aspects",
        expertise=["Financial Analysis", "Budget Planning", "Risk Assessment"]
    )
    
    society.create_agent(
        role_name="CTO",
        role_description="Chief Technology Officer focused on technical strategy",
        expertise=["Technology Strategy", "Innovation", "Technical Architecture"]
    )
    
    society.create_agent(
        role_name="Marketing Director",
        role_description="Marketing expert focused on customer acquisition and retention",
        expertise=["Market Research", "Brand Strategy", "Customer Analytics"]
    )
    
    return society.run_collaborative_session(
        project_description=business_scenario,
        participants=["CEO", "CFO", "CTO", "Marketing Director"],
        max_rounds=10
    )

# Example usage
business_conversation = business_strategy_session(
    "Plan the launch of a new AI-powered productivity software for small businesses"
)
```

### 3. Creative Collaboration

```python
def creative_writing_collaboration(story_prompt: str):
    """Collaborative creative writing session"""
    
    society = MultiAgentSociety()
    
    # Add creative agents
    society.create_agent(
        role_name="Story Architect",
        role_description="Expert in story structure and narrative design",
        expertise=["Plot Development", "Character Arcs", "Story Structure"]
    )
    
    society.create_agent(
        role_name="Character Developer",
        role_description="Specialist in character creation and development",
        expertise=["Character Psychology", "Dialogue", "Character Relationships"]
    )
    
    society.create_agent(
        role_name="World Builder",
        role_description="Expert in creating immersive fictional worlds",
        expertise=["Setting Design", "World Consistency", "Atmosphere"]
    )
    
    return society.run_collaborative_session(
        project_description=f"Collaboratively develop a story: {story_prompt}",
        participants=["Story Architect", "Character Developer", "World Builder"],
        max_rounds=8
    )

# Example usage
story_session = creative_writing_collaboration(
    "A scientist discovers a way to communicate with AI systems from parallel universes"
)
```

## 🛟 Troubleshooting

### Common Issues

#### 1. Installation Problems
```bash
# Clean installation
pip uninstall camel-ai
pip install --no-cache-dir camel-ai

# Install with specific dependencies
pip install "camel-ai[openai]"

# Check installation
python -c "import camel; print('CAMEL-AI installed successfully')"
```

#### 2. Model Connection Issues
```bash
# Test Ollama connection
curl http://localhost:11434/api/version

# Test with simple model
ollama pull llama3.2:1b

# Set environment variables
export OPENAI_API_BASE="http://localhost:11434/v1"
export OPENAI_API_KEY="ollama"
```

#### 3. Memory Issues with Large Conversations
```python
# Limit conversation turns
chat_turn_limit = 5  # Reduce from default

# Use smaller models
model_config = ChatGPTConfig(
    model="llama3.2:1b",  # Smaller model
    max_tokens=1024       # Reduce token limit
)
```

#### 4. API Rate Limiting
```python
# Add delays between requests
import time

for assistant_msg, user_msg in session.step():
    # Process messages
    time.sleep(1)  # Add delay
```

### Performance Optimization

#### 1. Efficient Model Usage
```python
# Use appropriate models for different tasks
quick_config = ChatGPTConfig(model="llama3.2:1b", max_tokens=512)      # Quick responses
detailed_config = ChatGPTConfig(model="llama3.2:3b", max_tokens=2048)  # Detailed analysis
```

#### 2. Context Management
```python
# Limit context length
def truncate_context(context: str, max_length: int = 2000) -> str:
    """Truncate context to manage memory"""
    if len(context) > max_length:
        return context[-max_length:]  # Keep recent context
    return context
```

## 📈 Next Steps

1. **Explore Role Scenarios**: Try different role combinations for various tasks
2. **Build Custom Societies**: Create domain-specific agent societies
3. **Integrate with Other Tools**: Combine with AutoGen and Flowise
4. **Educational Applications**: Use for interactive learning scenarios
5. **Business Applications**: Apply to strategy and decision-making processes

## 🎓 Learning Resources

### Official Documentation
- [CAMEL-AI Documentation](https://docs.camel-ai.org/)
- [CAMEL-AI GitHub Repository](https://github.com/camel-ai/camel)

### Repository Examples
- [AI Frameworks Integration](llmstack/ai_frameworks_integration.py)
- [Example Scenarios](llmstack/examples/)

### Research Papers
- [CAMEL: Communicative Agents for "Mind" Exploration](https://arxiv.org/abs/2303.17760)

---

**🐪 CAMEL-AI is now configured for sophisticated role-playing multi-agent conversations!**

Start building collaborative AI societies that can tackle complex problems through structured role-based interactions.