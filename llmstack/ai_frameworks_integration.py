#!/usr/bin/env python3
"""
AI Frameworks Integration Module
Integrates MemGPT, AutoGen, CAMEL-AI, and LocalAI
"""

import os
import json
import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    health_check_timeout: int = 10
    retry_attempts: int = 3
    retry_delay: float = 1.0

class LocalAIClient:
    """Client for LocalAI integration"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.name = "LocalAI"
        self.last_health_check = None
        self.health_status = False
        
        if config.use_local:
            self.client = OpenAI(
                api_key=config.openai_api_key,
                base_url=config.localai_endpoint
            )
        else:
            self.client = OpenAI(api_key=config.openai_api_key)
        
        # Perform initial health check
        self.health_check()
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for LocalAI"""
        start_time = time.time()
        health_result = {
            "name": self.name,
            "status": "unknown",
            "timestamp": time.time(),
            "response_time": None,
            "details": {},
            "error": None
        }
        
        try:
            logger.info(f"🔍 Starting health check for {self.name}")
            
            if self.config.use_local:
                # Check LocalAI endpoint
                response = requests.get(
                    f"{self.config.localai_endpoint.replace('/v1', '')}/health",
                    timeout=self.config.health_check_timeout
                )
                if response.status_code == 200:
                    health_result["details"]["endpoint_status"] = "healthy"
                else:
                    raise Exception(f"Health endpoint returned {response.status_code}")
                
                # Check models endpoint
                models_response = requests.get(
                    f"{self.config.localai_endpoint}/models",
                    timeout=self.config.health_check_timeout
                )
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    health_result["details"]["models_available"] = len(models_data.get("data", []))
                else:
                    health_result["details"]["models_available"] = 0
            else:
                # Check OpenAI connection
                models = self.client.models.list()
                health_result["details"]["models_available"] = len(list(models))
            
            health_result["status"] = "healthy"
            self.health_status = True
            logger.info(f"✅ {self.name} health check passed")
            
        except Exception as e:
            health_result["status"] = "unhealthy"
            health_result["error"] = str(e)
            self.health_status = False
            logger.error(f"❌ {self.name} health check failed: {e}")
        
        finally:
            health_result["response_time"] = time.time() - start_time
            self.last_health_check = health_result
            
        return health_result
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs):
        """Create a chat completion with retry logic"""
        for attempt in range(self.config.retry_attempts):
            try:
                logger.debug(f"🤖 {self.name} processing chat completion (attempt {attempt + 1})")
                response = self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=messages,
                    temperature=kwargs.get('temperature', self.config.temperature),
                    max_tokens=kwargs.get('max_tokens', self.config.max_tokens)
                )
                logger.info(f"✅ {self.name} chat completion successful")
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"⚠️ {self.name} attempt {attempt + 1} failed: {e}")
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    logger.error(f"❌ {self.name} all attempts failed")
                    return None
    
    def check_connection(self) -> bool:
        """Legacy connection check - use health_check() instead"""
        health_result = self.health_check()
        return health_result["status"] == "healthy"

class MemGPTAgent:
    """MemGPT Agent wrapper"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.name = "MemGPT"
        self.agent = None
        self.last_health_check = None
        self.health_status = False
        
        if MEMGPT_AVAILABLE:
            self.initialize()
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for MemGPT"""
        start_time = time.time()
        health_result = {
            "name": self.name,
            "status": "unknown",
            "timestamp": time.time(),
            "response_time": None,
            "details": {},
            "error": None
        }
        
        try:
            logger.info(f"🔍 Starting health check for {self.name}")
            
            if not MEMGPT_AVAILABLE:
                raise Exception("MemGPT package not available")
            
            if self.agent is None:
                raise Exception("MemGPT agent not initialized")
            
            # Test basic functionality
            test_response = self.chat("Hello, this is a health check")
            if test_response and "Error" not in test_response:
                health_result["details"]["agent_responsive"] = True
                health_result["status"] = "healthy"
                self.health_status = True
                logger.info(f"✅ {self.name} health check passed")
            else:
                raise Exception("Agent not responding correctly")
                
        except Exception as e:
            health_result["status"] = "unhealthy"
            health_result["error"] = str(e)
            health_result["details"]["agent_responsive"] = False
            self.health_status = False
            logger.error(f"❌ {self.name} health check failed: {e}")
        
        finally:
            health_result["response_time"] = time.time() - start_time
            self.last_health_check = health_result
            
        return health_result
    
    def initialize(self):
        """Initialize MemGPT agent"""
        try:
            logger.info(f"🚀 Initializing {self.name}")
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
            logger.info(f"✅ {self.name} initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.name}: {e}")
    
    def chat(self, message: str) -> str:
        """Chat with MemGPT agent"""
        if not self.agent:
            return f"{self.name} agent not initialized"
        
        try:
            logger.debug(f"🤖 {self.name} processing message")
            response = self.agent.step(message)
            result = response.messages[0].text if response.messages else "No response"
            logger.info(f"✅ {self.name} chat successful")
            return result
        except Exception as e:
            logger.error(f"❌ {self.name} chat error: {e}")
            return f"Error: {e}"

class AutoGenOrchestrator:
    """AutoGen multi-agent orchestrator"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.name = "AutoGen"
        self.agents = {}
        self.last_health_check = None
        self.health_status = False
        
        if AUTOGEN_AVAILABLE:
            self.initialize()
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for AutoGen"""
        start_time = time.time()
        health_result = {
            "name": self.name,
            "status": "unknown",
            "timestamp": time.time(),
            "response_time": None,
            "details": {},
            "error": None
        }
        
        try:
            logger.info(f"🔍 Starting health check for {self.name}")
            
            if not AUTOGEN_AVAILABLE:
                raise Exception("AutoGen package not available")
            
            if not self.agents:
                raise Exception("AutoGen agents not initialized")
            
            # Check if required agents exist
            required_agents = ['assistant', 'user_proxy']
            for agent_name in required_agents:
                if agent_name not in self.agents:
                    raise Exception(f"Required agent '{agent_name}' not found")
            
            health_result["details"]["agents_count"] = len(self.agents)
            health_result["details"]["required_agents_present"] = True
            
            # Test basic functionality with a simple chat
            test_response = self.chat("Hello, this is a health check")
            if test_response and "Error" not in test_response:
                health_result["details"]["chat_functional"] = True
                health_result["status"] = "healthy"
                self.health_status = True
                logger.info(f"✅ {self.name} health check passed")
            else:
                raise Exception("Chat functionality test failed")
                
        except Exception as e:
            health_result["status"] = "unhealthy" 
            health_result["error"] = str(e)
            health_result["details"]["chat_functional"] = False
            self.health_status = False
            logger.error(f"❌ {self.name} health check failed: {e}")
        
        finally:
            health_result["response_time"] = time.time() - start_time
            self.last_health_check = health_result
            
        return health_result
    
    def initialize(self):
        """Initialize AutoGen agents"""
        try:
            logger.info(f"🚀 Initializing {self.name}")
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
            
            logger.info(f"✅ {self.name} initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.name}: {e}")
    
    def chat(self, message: str) -> str:
        """Chat using AutoGen agents"""
        if not self.agents:
            return f"{self.name} agents not initialized"
        
        try:
            logger.debug(f"🤖 {self.name} processing chat")
            self.agents['user_proxy'].initiate_chat(
                self.agents['assistant'],
                message=message
            )
            result = self.agents['assistant'].last_message()["content"]
            logger.info(f"✅ {self.name} chat successful")
            return result
        except Exception as e:
            logger.error(f"❌ {self.name} chat error: {e}")
            return f"Error: {e}"
    
    def create_group_chat(self, agents_config: List[Dict[str, Any]]):
        """Create a group chat with multiple agents"""
        try:
            logger.info(f"🚀 Creating {self.name} group chat with {len(agents_config)} agents")
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
            
            logger.info(f"✅ {self.name} group chat created successfully")
            return manager
        except Exception as e:
            logger.error(f"❌ Failed to create {self.name} group chat: {e}")
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
        self.name = "CAMEL-AI"
        self.agents = {}
        self.last_health_check = None
        self.health_status = False
        
        if CAMEL_AVAILABLE:
            self.initialize()
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for CAMEL-AI"""
        start_time = time.time()
        health_result = {
            "name": self.name,
            "status": "unknown",
            "timestamp": time.time(),
            "response_time": None,
            "details": {},
            "error": None
        }
        
        try:
            logger.info(f"🔍 Starting health check for {self.name}")
            
            if not CAMEL_AVAILABLE:
                raise Exception("CAMEL-AI package not available")
            
            if not self.agents:
                raise Exception("CAMEL-AI agents not initialized")
            
            # Check if required agents exist
            required_agents = ['assistant', 'user']
            for agent_name in required_agents:
                if agent_name not in self.agents:
                    raise Exception(f"Required agent '{agent_name}' not found")
            
            health_result["details"]["agents_count"] = len(self.agents)
            health_result["details"]["required_agents_present"] = True
            
            # Test basic functionality
            test_response = self.chat("Hello, this is a health check")
            if test_response and "Error" not in test_response:
                health_result["details"]["chat_functional"] = True
                health_result["status"] = "healthy"
                self.health_status = True
                logger.info(f"✅ {self.name} health check passed")
            else:
                raise Exception("Chat functionality test failed")
                
        except Exception as e:
            health_result["status"] = "unhealthy"
            health_result["error"] = str(e)
            health_result["details"]["chat_functional"] = False
            self.health_status = False
            logger.error(f"❌ {self.name} health check failed: {e}")
        
        finally:
            health_result["response_time"] = time.time() - start_time
            self.last_health_check = health_result
            
        return health_result
    
    def initialize(self):
        """Initialize CAMEL agents"""
        try:
            logger.info(f"🚀 Initializing {self.name}")
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
            
            logger.info(f"✅ {self.name} initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.name}: {e}")
    
    def chat(self, message: str) -> str:
        """Chat using CAMEL agents"""
        if not self.agents:
            return f"{self.name} agents not initialized"
        
        try:
            logger.debug(f"🤖 {self.name} processing chat")
            # Use assistant agent for chat
            agent = self.agents.get('assistant')
            if not agent:
                return f"{self.name} assistant agent not available"
            
            # Create a message object
            from camel.messages import BaseMessage
            message_obj = BaseMessage.make_user_message(
                role_name="User",
                content=message
            )
            
            response = agent.step(message_obj)
            result = response.msg.content
            logger.info(f"✅ {self.name} chat successful")
            return result
        except Exception as e:
            logger.error(f"❌ {self.name} chat error: {e}")
            return f"Error: {e}"
    
    def role_play(self, task: str, assistant_role: str, user_role: str):
        """Create a role-playing scenario between two agents"""
        try:
            logger.info(f"🎭 Starting {self.name} role-play scenario")
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
            
            logger.info(f"✅ {self.name} role-play completed")
            return messages
        except Exception as e:
            logger.error(f"❌ {self.name} role-play error: {e}")
            return []

class UnifiedAIOrchestrator:
    """Unified orchestrator for all AI frameworks"""
    
    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()
        self.name = "UnifiedOrchestrator"
        self.last_health_check = None
        
        # Initialize all frameworks
        logger.info("🚀 Initializing Unified AI Orchestrator")
        self.localai = LocalAIClient(self.config)
        self.memgpt = MemGPTAgent(self.config)
        self.autogen = AutoGenOrchestrator(self.config)
        self.camel = CAMELOrchestrator(self.config)
        
        # Agents registry for easy access
        self.agents = {
            "localai": self.localai,
            "memgpt": self.memgpt,
            "autogen": self.autogen,
            "camel": self.camel
        }
        
        # Perform initial health check
        logger.info("🔍 Performing initial system health check")
        self.comprehensive_health_check()
    
    def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check on all agents"""
        start_time = time.time()
        health_results = {
            "orchestrator_name": self.name,
            "timestamp": time.time(),
            "overall_status": "unknown",
            "agents": {},
            "summary": {},
            "response_time": None
        }
        
        logger.info("🔍 Starting comprehensive health check for all AI agents")
        
        healthy_count = 0
        total_count = 0
        
        for agent_name, agent in self.agents.items():
            total_count += 1
            
            if hasattr(agent, 'health_check'):
                agent_health = agent.health_check()
                health_results["agents"][agent_name] = agent_health
                
                if agent_health["status"] == "healthy":
                    healthy_count += 1
            else:
                # Fallback for agents without health_check method
                try:
                    if agent_name == "localai":
                        is_healthy = agent.check_connection()
                    else:
                        # Simple availability check
                        is_healthy = getattr(agent, 'agents', None) is not None
                    
                    health_results["agents"][agent_name] = {
                        "name": agent_name,
                        "status": "healthy" if is_healthy else "unhealthy",
                        "timestamp": time.time(),
                        "details": {"basic_check": is_healthy}
                    }
                    
                    if is_healthy:
                        healthy_count += 1
                        
                except Exception as e:
                    health_results["agents"][agent_name] = {
                        "name": agent_name,
                        "status": "unhealthy",
                        "timestamp": time.time(),
                        "error": str(e)
                    }
        
        # Calculate overall status
        health_percentage = (healthy_count / total_count) * 100 if total_count > 0 else 0
        
        if health_percentage >= 75:
            health_results["overall_status"] = "healthy"
        elif health_percentage >= 50:
            health_results["overall_status"] = "degraded"
        else:
            health_results["overall_status"] = "unhealthy"
        
        health_results["summary"] = {
            "healthy_agents": healthy_count,
            "total_agents": total_count,
            "health_percentage": health_percentage
        }
        
        health_results["response_time"] = time.time() - start_time
        self.last_health_check = health_results
        
        # Log summary
        logger.info(f"🏥 Health check completed: {healthy_count}/{total_count} agents healthy ({health_percentage:.1f}%)")
        for agent_name, result in health_results["agents"].items():
            status_emoji = "✅" if result["status"] == "healthy" else "❌"
            logger.info(f"  {status_emoji} {agent_name}: {result['status']}")
        
        return health_results
    
    def check_status(self) -> Dict[str, bool]:
        """Check status of all components (legacy method)"""
        health_check = self.comprehensive_health_check()
        status = {}
        
        for agent_name, result in health_check["agents"].items():
            status[agent_name] = result["status"] == "healthy"
        
        return status
    
    def chat(self, message: str, framework: str = "localai") -> str:
        """Chat using specified framework with enhanced error handling"""
        framework = framework.lower()
        
        logger.info(f"🤖 Routing message to {framework}")
        
        try:
            if framework == "localai":
                return self.localai.chat_completion([{"role": "user", "content": message}])
            elif framework == "memgpt":
                return self.memgpt.chat(message)
            elif framework == "autogen":
                return self.autogen.chat(message)
            elif framework == "camel":
                return self.camel.chat(message)
            else:
                available_frameworks = list(self.agents.keys())
                return f"Unknown framework '{framework}'. Available: {', '.join(available_frameworks)}"
                
        except Exception as e:
            logger.error(f"❌ Error in {framework} chat: {e}")
            return f"Error in {framework}: {e}"
    
    def multi_agent_task(self, task: str, agents: List[str] = None):
        """Execute a task using multiple agents with enhanced logging"""
        agents = agents or ["autogen", "camel"]
        results = {}
        
        logger.info(f"🔀 Starting multi-agent task with {len(agents)} agents")
        
        for agent in agents:
            try:
                logger.info(f"🤖 Processing with {agent}...")
                start_time = time.time()
                result = self.chat(task, framework=agent)
                response_time = time.time() - start_time
                
                results[agent] = {
                    "result": result,
                    "response_time": response_time,
                    "status": "success" if result and "Error" not in result else "failed"
                }
                
                logger.info(f"✅ {agent} completed in {response_time:.2f}s")
                
            except Exception as e:
                logger.error(f"❌ {agent} failed: {e}")
                results[agent] = {
                    "result": f"Error: {e}",
                    "response_time": None,
                    "status": "error"
                }
        
        return results
    
    async def async_multi_agent(self, task: str, agents: List[str] = None):
        """Execute task with multiple agents asynchronously"""
        agents = agents or ["localai", "autogen", "camel"]
        
        logger.info(f"🔀 Starting async multi-agent task with {len(agents)} agents")
        
        async def process_agent(agent: str):
            try:
                start_time = time.time()
                result = self.chat(task, framework=agent)
                response_time = time.time() - start_time
                logger.info(f"✅ Async {agent} completed in {response_time:.2f}s")
                return agent, result
            except Exception as e:
                logger.error(f"❌ Async {agent} failed: {e}")
                return agent, f"Error: {e}"
        
        tasks = [process_agent(agent) for agent in agents]
        results = await asyncio.gather(*tasks)
        
        return dict(results)
    
    def get_agent_registry(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered agents"""
        registry = {}
        
        for agent_name, agent in self.agents.items():
            agent_info = {
                "name": agent_name,
                "class": agent.__class__.__name__,
                "available": True,
                "last_health_check": getattr(agent, 'last_health_check', None),
                "health_status": getattr(agent, 'health_status', False)
            }
            
            # Add specific information based on agent type
            if hasattr(agent, 'agents') and agent.agents:
                agent_info["sub_agents"] = list(agent.agents.keys())
            
            registry[agent_name] = agent_info
        
        return registry
        
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