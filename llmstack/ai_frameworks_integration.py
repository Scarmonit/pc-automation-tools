#!/usr/bin/env python3
"""
AI Frameworks Integration Module
Integrates MemGPT, AutoGen, CAMEL-AI, and LocalAI
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import frameworks (with error handling for missing packages)
try:
    import memgpt
    MEMGPT_AVAILABLE = True
except ImportError:
    logger.warning("MemGPT not available")
    MEMGPT_AVAILABLE = False

try:
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    logger.warning("AutoGen not available")
    AUTOGEN_AVAILABLE = False

try:
    from camel import CAMELAgent
    from camel.messages import BaseMessage
    from camel.agents import ChatAgent
    CAMEL_AVAILABLE = True
except ImportError:
    logger.warning("CAMEL-AI not available")
    CAMEL_AVAILABLE = False

import requests
from openai import OpenAI

@dataclass
class AIConfig:
    """Configuration for AI frameworks"""
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "sk-localai")
    localai_endpoint: str = "http://localhost:8080/v1"
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2048
    use_local: bool = True

class LocalAIClient:
    """Client for LocalAI integration"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        if config.use_local:
            self.client = OpenAI(
                api_key=config.openai_api_key,
                base_url=config.localai_endpoint
            )
        else:
            self.client = OpenAI(api_key=config.openai_api_key)
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs):
        """Create a chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return None
    
    def check_connection(self) -> bool:
        """Check if LocalAI is running"""
        try:
            if self.config.use_local:
                response = requests.get(f"{self.config.localai_endpoint}/models")
                return response.status_code == 200
            else:
                # Check OpenAI connection
                self.client.models.list()
                return True
        except:
            return False

class MemGPTAgent:
    """MemGPT Agent wrapper"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.agent = None
        if MEMGPT_AVAILABLE:
            self.initialize()
    
    def initialize(self):
        """Initialize MemGPT agent"""
        try:
            # Configure MemGPT with LocalAI or OpenAI
            import memgpt.config as memgpt_config
            
            if self.config.use_local:
                memgpt_config.set_openai_api_base(self.config.localai_endpoint)
            
            memgpt_config.set_openai_api_key(self.config.openai_api_key)
            
            # Create agent with memory
            from memgpt import create_agent
            self.agent = create_agent(
                model=self.config.model_name,
                persona="You are a helpful AI assistant with long-term memory capabilities.",
                human="User seeking assistance"
            )
            logger.info("MemGPT agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MemGPT: {e}")
    
    def chat(self, message: str) -> str:
        """Chat with MemGPT agent"""
        if not self.agent:
            return "MemGPT agent not initialized"
        
        try:
            response = self.agent.step(message)
            return response.messages[0].text if response.messages else "No response"
        except Exception as e:
            logger.error(f"MemGPT chat error: {e}")
            return f"Error: {e}"

class AutoGenOrchestrator:
    """AutoGen multi-agent orchestrator"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.agents = {}
        if AUTOGEN_AVAILABLE:
            self.initialize()
    
    def initialize(self):
        """Initialize AutoGen agents"""
        try:
            # Configure for LocalAI or OpenAI
            llm_config = {
                "model": self.config.model_name,
                "api_key": self.config.openai_api_key,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            if self.config.use_local:
                llm_config["base_url"] = self.config.localai_endpoint
            
            # Create assistant agent
            self.agents['assistant'] = AssistantAgent(
                name="Assistant",
                llm_config=llm_config,
                system_message="You are a helpful AI assistant."
            )
            
            # Create user proxy agent
            self.agents['user_proxy'] = UserProxyAgent(
                name="User",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=5,
                code_execution_config={"use_docker": False}
            )
            
            logger.info("AutoGen agents initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AutoGen: {e}")
    
    def chat(self, message: str) -> str:
        """Chat using AutoGen agents"""
        if not self.agents:
            return "AutoGen agents not initialized"
        
        try:
            self.agents['user_proxy'].initiate_chat(
                self.agents['assistant'],
                message=message
            )
            return self.agents['assistant'].last_message()["content"]
        except Exception as e:
            logger.error(f"AutoGen chat error: {e}")
            return f"Error: {e}"
    
    def create_group_chat(self, agents_config: List[Dict[str, Any]]):
        """Create a group chat with multiple agents"""
        try:
            agents = []
            for config in agents_config:
                agent = AssistantAgent(
                    name=config['name'],
                    llm_config=self._get_llm_config(),
                    system_message=config.get('system_message', '')
                )
                agents.append(agent)
            
            group_chat = GroupChat(agents=agents, messages=[], max_round=10)
            manager = GroupChatManager(groupchat=group_chat, llm_config=self._get_llm_config())
            
            return manager
        except Exception as e:
            logger.error(f"Failed to create group chat: {e}")
            return None
    
    def _get_llm_config(self):
        """Get LLM configuration"""
        config = {
            "model": self.config.model_name,
            "api_key": self.config.openai_api_key,
            "temperature": self.config.temperature
        }
        if self.config.use_local:
            config["base_url"] = self.config.localai_endpoint
        return config

class CAMELOrchestrator:
    """CAMEL-AI multi-agent orchestrator"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.agents = {}
        if CAMEL_AVAILABLE:
            self.initialize()
    
    def initialize(self):
        """Initialize CAMEL agents"""
        try:
            # Configure CAMEL with LocalAI or OpenAI
            from camel.configs import ChatGPTConfig
            from camel.agents import ChatAgent
            
            model_config = ChatGPTConfig(
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                model=self.config.model_name
            )
            
            # Create AI assistant agent
            self.agents['assistant'] = ChatAgent(
                system_message="You are a helpful AI assistant.",
                model_config=model_config
            )
            
            # Create AI user agent
            self.agents['user'] = ChatAgent(
                system_message="You are a user seeking help.",
                model_config=model_config
            )
            
            logger.info("CAMEL agents initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CAMEL: {e}")
    
    def chat(self, message: str) -> str:
        """Chat using CAMEL agents"""
        if not self.agents:
            return "CAMEL agents not initialized"
        
        try:
            from camel.messages import UserMessage
            user_msg = UserMessage(content=message)
            response = self.agents['assistant'].step(user_msg)
            return response.content
        except Exception as e:
            logger.error(f"CAMEL chat error: {e}")
            return f"Error: {e}"
    
    def role_play(self, task: str, assistant_role: str, user_role: str):
        """Create a role-playing scenario between two agents"""
        try:
            from camel.societies import RolePlaying
            
            role_play = RolePlaying(
                assistant_role=assistant_role,
                user_role=user_role,
                task=task,
                model_type="gpt-3.5-turbo"
            )
            
            # Run the role-playing session
            messages = []
            for msg in role_play.step():
                messages.append(msg)
                if len(messages) > 10:  # Limit conversation length
                    break
            
            return messages
        except Exception as e:
            logger.error(f"CAMEL role-play error: {e}")
            return []

class UnifiedAIOrchestrator:
    """Unified orchestrator for all AI frameworks"""
    
    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()
        self.localai = LocalAIClient(self.config)
        self.memgpt = MemGPTAgent(self.config)
        self.autogen = AutoGenOrchestrator(self.config)
        self.camel = CAMELOrchestrator(self.config)
        
        # Check connections
        self.check_status()
    
    def check_status(self) -> Dict[str, bool]:
        """Check status of all components"""
        status = {
            "localai": self.localai.check_connection(),
            "memgpt": MEMGPT_AVAILABLE,
            "autogen": AUTOGEN_AVAILABLE,
            "camel": CAMEL_AVAILABLE
        }
        
        logger.info(f"System status: {status}")
        return status
    
    def chat(self, message: str, framework: str = "localai") -> str:
        """Chat using specified framework"""
        framework = framework.lower()
        
        if framework == "localai":
            return self.localai.chat_completion([{"role": "user", "content": message}])
        elif framework == "memgpt":
            return self.memgpt.chat(message)
        elif framework == "autogen":
            return self.autogen.chat(message)
        elif framework == "camel":
            return self.camel.chat(message)
        else:
            return f"Unknown framework: {framework}"
    
    def multi_agent_task(self, task: str, agents: List[str] = None):
        """Execute a task using multiple agents"""
        agents = agents or ["autogen", "camel"]
        results = {}
        
        for agent in agents:
            logger.info(f"Processing with {agent}...")
            result = self.chat(task, framework=agent)
            results[agent] = result
        
        return results
    
    async def async_multi_agent(self, task: str, agents: List[str] = None):
        """Execute task with multiple agents asynchronously"""
        agents = agents or ["localai", "autogen", "camel"]
        
        async def process_agent(agent: str):
            return agent, self.chat(task, framework=agent)
        
        tasks = [process_agent(agent) for agent in agents]
        results = await asyncio.gather(*tasks)
        
        return dict(results)

def main():
    """Main function to demonstrate the integration"""
    print("=" * 60)
    print("AI Frameworks Integration System")
    print("=" * 60)
    
    # Initialize the unified orchestrator
    config = AIConfig(
        use_local=True,  # Set to False to use OpenAI instead of LocalAI
        model_name="gpt-3.5-turbo",
        temperature=0.7
    )
    
    orchestrator = UnifiedAIOrchestrator(config)
    
    # Check system status
    print("\nSystem Status:")
    status = orchestrator.check_status()
    for component, available in status.items():
        status_str = "✓ Available" if available else "✗ Not Available"
        print(f"  {component}: {status_str}")
    
    # Interactive demo
    print("\n" + "=" * 60)
    print("Interactive Demo")
    print("Available frameworks: localai, memgpt, autogen, camel")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\nEnter your message: ")
            if user_input.lower() == 'quit':
                break
            
            framework = input("Choose framework (default: localai): ").strip() or "localai"
            
            print(f"\nProcessing with {framework}...")
            response = orchestrator.chat(user_input, framework=framework)
            print(f"\nResponse: {response}")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()