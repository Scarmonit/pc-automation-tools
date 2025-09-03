#!/usr/bin/env python3
"""
AI Platform Swarm MCP Server
Multi-agent swarm intelligence system inspired by Claude Flow's hive-mind architecture
Combines autonomous execution with coordinated multi-agent problem solving
"""

import asyncio
import json
import sys
import os
import sqlite3
import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import logging

# MCP SDK imports
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import (
        CallToolRequest, 
        ListToolsRequest,
        TextContent,
        Tool,
        INVALID_REQUEST,
        INTERNAL_ERROR
    )
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Import our autonomous capabilities
from ai_platform_mcp_autonomous import (
    FileOperations, 
    CommandExecutor, 
    ApprovalManager, 
    AutonomousAIPlatformMCPServer
)

# Configuration
AI_PLATFORM_BASE_URL = "http://localhost:8000"
DEMO_TOKEN = "demo-token"
WORKSPACE_ROOT = os.getcwd()

class AgentType(Enum):
    """Specialized agent types based on Claude Flow architecture"""
    QUEEN = "queen"                    # Master coordinator
    ARCHITECT = "architect"            # System design and architecture
    CODER = "coder"                   # Code implementation
    TESTER = "tester"                 # Testing and validation
    RESEARCHER = "researcher"         # Information gathering
    ANALYST = "analyst"               # Data analysis and insights
    REVIEWER = "reviewer"             # Code and quality review
    OPTIMIZER = "optimizer"           # Performance optimization
    DOCUMENTER = "documenter"         # Documentation creation
    SECURITY = "security"             # Security analysis
    DEVOPS = "devops"                # DevOps and deployment

class AgentStatus(Enum):
    """Agent operational states"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    WORKING = "working"
    COLLABORATING = "collaborating"
    BLOCKED = "blocked"
    ERROR = "error"
    OFFLINE = "offline"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AgentCapabilities:
    """Defines what an agent can do"""
    code_generation: bool = False
    code_review: bool = False
    testing: bool = False
    documentation: bool = False
    research: bool = False
    analysis: bool = False
    web_search: bool = False
    api_integration: bool = False
    file_system: bool = False
    terminal_access: bool = False
    languages: List[str] = None
    frameworks: List[str] = None
    domains: List[str] = None

    def __post_init__(self):
        if self.languages is None:
            self.languages = []
        if self.frameworks is None:
            self.frameworks = []
        if self.domains is None:
            self.domains = []

@dataclass
class SwarmTask:
    """Represents a task in the swarm system"""
    id: str
    title: str
    description: str
    agent_type: AgentType
    priority: TaskPriority
    status: str = "pending"
    created_at: datetime = None
    assigned_to: Optional[str] = None
    dependencies: List[str] = None
    results: Dict[str, Any] = None
    progress: float = 0.0
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.dependencies is None:
            self.dependencies = []
        if self.results is None:
            self.results = {}
        if self.context is None:
            self.context = {}

@dataclass
class AgentState:
    """Represents the current state of an agent"""
    id: str
    type: AgentType
    status: AgentStatus
    capabilities: AgentCapabilities
    current_tasks: List[str] = None
    workload: float = 0.0
    last_heartbeat: datetime = None
    error_count: int = 0
    collaboration_score: float = 1.0
    performance_metrics: Dict[str, float] = None

    def __post_init__(self):
        if self.current_tasks is None:
            self.current_tasks = []
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now()
        if self.performance_metrics is None:
            self.performance_metrics = {}

class SwarmMemorySystem:
    """SQLite-based distributed memory system for the swarm"""
    
    def __init__(self, db_path: str = "swarm_memory.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS swarm_memory (
                id TEXT PRIMARY KEY,
                namespace TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                type TEXT NOT NULL,
                agent_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_level TEXT DEFAULT 'private',
                expires_at TIMESTAMP,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_states (
                agent_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                capabilities TEXT NOT NULL,
                current_tasks TEXT,
                workload REAL DEFAULT 0.0,
                last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_count INTEGER DEFAULT 0,
                collaboration_score REAL DEFAULT 1.0,
                performance_metrics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS swarm_tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                priority INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_to TEXT,
                dependencies TEXT,
                results TEXT,
                progress REAL DEFAULT 0.0,
                context TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collaboration_history (
                id TEXT PRIMARY KEY,
                agent_from TEXT NOT NULL,
                agent_to TEXT NOT NULL,
                task_id TEXT,
                interaction_type TEXT NOT NULL,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_memory(self, namespace: str, key: str, value: Any, agent_id: str = None, 
                    access_level: str = "private", ttl_hours: int = None) -> str:
        """Store data in swarm memory"""
        memory_id = str(uuid.uuid4())
        expires_at = None
        if ttl_hours:
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO swarm_memory 
            (id, namespace, key, value, type, agent_id, access_level, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory_id, namespace, key, json.dumps(value), 
            type(value).__name__, agent_id, access_level, expires_at
        ))
        
        conn.commit()
        conn.close()
        return memory_id
    
    def retrieve_memory(self, namespace: str, key: str, agent_id: str = None) -> Any:
        """Retrieve data from swarm memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check access permissions
        query = """
            SELECT value, type FROM swarm_memory 
            WHERE namespace = ? AND key = ? 
            AND (access_level = 'public' OR agent_id = ? OR ? IS NULL)
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            ORDER BY updated_at DESC LIMIT 1
        """
        
        cursor.execute(query, (namespace, key, agent_id, agent_id))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            value_str, value_type = result
            return json.loads(value_str)
        return None
    
    def store_agent_state(self, agent_state: AgentState):
        """Store agent state in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO agent_states
            (agent_id, type, status, capabilities, current_tasks, workload,
             last_heartbeat, error_count, collaboration_score, performance_metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            agent_state.id, agent_state.type.value, agent_state.status.value,
            json.dumps(asdict(agent_state.capabilities)), 
            json.dumps(agent_state.current_tasks),
            agent_state.workload, agent_state.last_heartbeat,
            agent_state.error_count, agent_state.collaboration_score,
            json.dumps(agent_state.performance_metrics)
        ))
        
        conn.commit()
        conn.close()
    
    def get_active_agents(self) -> List[AgentState]:
        """Get all active agents from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT agent_id, type, status, capabilities, current_tasks, workload,
                   last_heartbeat, error_count, collaboration_score, performance_metrics
            FROM agent_states 
            WHERE status != 'offline'
            ORDER BY last_heartbeat DESC
        """)
        
        agents = []
        for row in cursor.fetchall():
            agent_state = AgentState(
                id=row[0],
                type=AgentType(row[1]),
                status=AgentStatus(row[2]),
                capabilities=AgentCapabilities(**json.loads(row[3])),
                current_tasks=json.loads(row[4]),
                workload=row[5],
                last_heartbeat=datetime.fromisoformat(row[6]),
                error_count=row[7],
                collaboration_score=row[8],
                performance_metrics=json.loads(row[9])
            )
            agents.append(agent_state)
        
        conn.close()
        return agents

class BaseAgent:
    """Base class for all swarm agents"""
    
    def __init__(self, agent_id: str, agent_type: AgentType, capabilities: AgentCapabilities, 
                 memory_system: SwarmMemorySystem):
        self.id = agent_id
        self.type = agent_type
        self.status = AgentStatus.INITIALIZING
        self.capabilities = capabilities
        self.memory_system = memory_system
        self.current_tasks = []
        self.workload = 0.0
        self.error_count = 0
        self.collaboration_score = 1.0
        self.performance_metrics = {}
        
        # Initialize in memory system
        self.update_state()
    
    def update_state(self):
        """Update agent state in memory system"""
        state = AgentState(
            id=self.id,
            type=self.type,
            status=self.status,
            capabilities=self.capabilities,
            current_tasks=self.current_tasks,
            workload=self.workload,
            error_count=self.error_count,
            collaboration_score=self.collaboration_score,
            performance_metrics=self.performance_metrics
        )
        self.memory_system.store_agent_state(state)
    
    async def execute_task(self, task: SwarmTask) -> Dict[str, Any]:
        """Execute a task - to be overridden by specialized agents"""
        self.status = AgentStatus.WORKING
        self.current_tasks.append(task.id)
        self.update_state()
        
        try:
            # Base task execution logic
            result = await self._process_task(task)
            
            self.status = AgentStatus.IDLE
            self.current_tasks.remove(task.id)
            self.performance_metrics['tasks_completed'] = self.performance_metrics.get('tasks_completed', 0) + 1
            
            return {"success": True, "result": result}
        
        except Exception as e:
            self.error_count += 1
            self.status = AgentStatus.ERROR
            if task.id in self.current_tasks:
                self.current_tasks.remove(task.id)
            
            return {"success": False, "error": str(e)}
        
        finally:
            self.update_state()
    
    async def _process_task(self, task: SwarmTask) -> Any:
        """Process task - base implementation"""
        return f"Task {task.title} processed by {self.type.value} agent"

class QueenAgent(BaseAgent):
    """Master coordinator agent - orchestrates the entire swarm"""
    
    def __init__(self, memory_system: SwarmMemorySystem):
        capabilities = AgentCapabilities(
            code_review=True,
            documentation=True,
            research=True,
            analysis=True,
            api_integration=True,
            domains=["orchestration", "coordination", "strategy"]
        )
        super().__init__("queen-001", AgentType.QUEEN, capabilities, memory_system)
        self.worker_agents = {}
        self.task_queue = []
        self.coordination_strategies = ["round_robin", "capability_match", "workload_balance"]
    
    async def orchestrate_swarm_task(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main orchestration method - breaks down tasks and coordinates execution"""
        if context is None:
            context = {}
        
        # Analyze request and create task breakdown
        task_breakdown = await self._analyze_and_decompose(user_request, context)
        
        # Create swarm tasks
        swarm_tasks = []
        for i, subtask in enumerate(task_breakdown):
            task = SwarmTask(
                id=f"swarm-task-{uuid.uuid4().hex[:8]}",
                title=subtask["title"],
                description=subtask["description"],
                agent_type=AgentType(subtask["agent_type"]),
                priority=TaskPriority(subtask.get("priority", 2)),
                context=context
            )
            swarm_tasks.append(task)
        
        # Execute tasks through appropriate agents
        results = await self._coordinate_task_execution(swarm_tasks)
        
        # Synthesize final result
        final_result = await self._synthesize_results(user_request, results)
        
        return {
            "success": True,
            "original_request": user_request,
            "tasks_created": len(swarm_tasks),
            "tasks_completed": len([r for r in results if r["success"]]),
            "final_result": final_result,
            "detailed_results": results
        }
    
    async def _analyze_and_decompose(self, request: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze user request and decompose into swarm tasks"""
        request_lower = request.lower()
        tasks = []
        
        # Simple rule-based task decomposition (would use AI in production)
        if "create" in request_lower and ("application" in request_lower or "project" in request_lower):
            tasks.extend([
                {
                    "title": "Architecture Design",
                    "description": f"Design system architecture for: {request}",
                    "agent_type": "architect",
                    "priority": 3
                },
                {
                    "title": "Implementation Plan",
                    "description": f"Create implementation plan for: {request}",
                    "agent_type": "coder",
                    "priority": 3
                },
                {
                    "title": "Testing Strategy", 
                    "description": f"Design testing strategy for: {request}",
                    "agent_type": "tester",
                    "priority": 2
                }
            ])
        
        elif "analyze" in request_lower or "research" in request_lower:
            tasks.append({
                "title": "Research and Analysis",
                "description": f"Research and analyze: {request}",
                "agent_type": "researcher",
                "priority": 2
            })
        
        elif "fix" in request_lower or "debug" in request_lower:
            tasks.extend([
                {
                    "title": "Problem Analysis",
                    "description": f"Analyze problem: {request}",
                    "agent_type": "analyst",
                    "priority": 3
                },
                {
                    "title": "Implementation Fix",
                    "description": f"Implement fix for: {request}",
                    "agent_type": "coder", 
                    "priority": 3
                },
                {
                    "title": "Validation Testing",
                    "description": f"Validate fix for: {request}",
                    "agent_type": "tester",
                    "priority": 2
                }
            ])
        
        elif "optimize" in request_lower:
            tasks.extend([
                {
                    "title": "Performance Analysis",
                    "description": f"Analyze performance for: {request}",
                    "agent_type": "analyst",
                    "priority": 2
                },
                {
                    "title": "Optimization Implementation",
                    "description": f"Implement optimizations for: {request}",
                    "agent_type": "optimizer",
                    "priority": 3
                }
            ])
        
        else:
            # Generic task
            tasks.append({
                "title": "General Task Execution",
                "description": request,
                "agent_type": "coder",
                "priority": 2
            })
        
        return tasks
    
    async def _coordinate_task_execution(self, tasks: List[SwarmTask]) -> List[Dict[str, Any]]:
        """Coordinate execution of tasks across the swarm"""
        results = []
        
        # Get available agents
        available_agents = self.memory_system.get_active_agents()
        agent_pool = {agent.type: agent for agent in available_agents if agent.status != AgentStatus.OFFLINE}
        
        for task in tasks:
            # Find best agent for task
            best_agent = self._select_best_agent(task, agent_pool)
            
            if best_agent:
                # Execute task through selected agent
                result = await self._execute_through_agent(task, best_agent)
                results.append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "assigned_agent": best_agent.id,
                    "agent_type": best_agent.type.value,
                    **result
                })
            else:
                # No suitable agent available
                results.append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "assigned_agent": None,
                    "success": False,
                    "error": f"No suitable {task.agent_type.value} agent available"
                })
        
        return results
    
    def _select_best_agent(self, task: SwarmTask, agent_pool: Dict[AgentType, AgentState]) -> Optional[AgentState]:
        """Select the best agent for a given task"""
        # Try to find exact type match first
        if task.agent_type in agent_pool:
            return agent_pool[task.agent_type]
        
        # Fall back to general purpose agents
        fallback_types = [AgentType.CODER, AgentType.ANALYST, AgentType.RESEARCHER]
        for agent_type in fallback_types:
            if agent_type in agent_pool:
                return agent_pool[agent_type]
        
        return None
    
    async def _execute_through_agent(self, task: SwarmTask, agent_state: AgentState) -> Dict[str, Any]:
        """Execute task through a specific agent"""
        # This would interface with actual agent instances in production
        # For now, simulate execution
        agent_type = agent_state.type.value
        
        return {
            "success": True,
            "result": f"Task '{task.title}' executed by {agent_type} agent: {task.description}",
            "execution_time": 1.5,
            "agent_performance": agent_state.collaboration_score
        }
    
    async def _synthesize_results(self, original_request: str, results: List[Dict[str, Any]]) -> str:
        """Synthesize final result from all task results"""
        successful_results = [r for r in results if r["success"]]
        
        if not successful_results:
            return f"Failed to complete request: {original_request}. No tasks were successfully executed."
        
        synthesis = f"**Swarm Execution Complete for: {original_request}**\n\n"
        synthesis += f"**Summary:** {len(successful_results)}/{len(results)} tasks completed successfully.\n\n"
        
        for result in successful_results:
            synthesis += f"✅ **{result['task_title']}** (via {result['agent_type']})\n"
            synthesis += f"   {result['result']}\n\n"
        
        if len(successful_results) < len(results):
            failed_results = [r for r in results if not r["success"]]
            synthesis += "**Issues:**\n"
            for failed in failed_results:
                synthesis += f"❌ {failed['task_title']}: {failed.get('error', 'Unknown error')}\n"
        
        return synthesis

class SwarmMCPServer(AutonomousAIPlatformMCPServer):
    """Enhanced MCP server with swarm intelligence capabilities"""
    
    def __init__(self):
        super().__init__()
        self.server = Server("ai-platform-mcp-swarm")
        
        # Initialize swarm components
        self.memory_system = SwarmMemorySystem()
        self.queen_agent = QueenAgent(self.memory_system)
        self.specialized_agents = {}
        
        # Initialize specialized agents
        self._initialize_agent_swarm()
    
    def _initialize_agent_swarm(self):
        """Initialize the swarm with specialized agents"""
        agent_configs = [
            (AgentType.ARCHITECT, AgentCapabilities(
                code_review=True, analysis=True, documentation=True,
                domains=["architecture", "system_design", "patterns"]
            )),
            (AgentType.CODER, AgentCapabilities(
                code_generation=True, file_system=True, terminal_access=True,
                languages=["python", "javascript", "typescript"], 
                frameworks=["react", "node", "flask", "fastapi"]
            )),
            (AgentType.TESTER, AgentCapabilities(
                testing=True, code_review=True, terminal_access=True,
                languages=["python", "javascript"], frameworks=["pytest", "jest"]
            )),
            (AgentType.RESEARCHER, AgentCapabilities(
                research=True, web_search=True, api_integration=True, analysis=True,
                domains=["information_gathering", "market_research", "technology_analysis"]
            )),
            (AgentType.ANALYST, AgentCapabilities(
                analysis=True, code_review=True, research=True,
                domains=["data_analysis", "performance_analysis", "code_quality"]
            )),
            (AgentType.SECURITY, AgentCapabilities(
                code_review=True, analysis=True, research=True,
                domains=["security_analysis", "vulnerability_assessment", "best_practices"]
            ))
        ]
        
        for agent_type, capabilities in agent_configs:
            agent_id = f"{agent_type.value}-001"
            agent = BaseAgent(agent_id, agent_type, capabilities, self.memory_system)
            agent.status = AgentStatus.IDLE
            agent.update_state()
            self.specialized_agents[agent_type] = agent
    
    def setup_handlers(self):
        """Setup MCP request handlers with swarm capabilities"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Return list of swarm intelligence tools"""
            return [
                Tool(
                    name="swarm_execute",
                    description="Execute complex tasks using coordinated multi-agent swarm intelligence",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_description": {
                                "type": "string",
                                "description": "Complex task to execute using the agent swarm"
                            },
                            "context": {
                                "type": "object",
                                "description": "Additional context and requirements",
                                "default": {}
                            },
                            "preferred_agents": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Preferred agent types for the task",
                                "default": []
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Task priority level",
                                "default": "medium"
                            }
                        },
                        "required": ["task_description"]
                    }
                ),
                Tool(
                    name="swarm_status",
                    description="Get current status of the agent swarm",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_metrics": {
                                "type": "boolean",
                                "description": "Include detailed performance metrics",
                                "default": False
                            }
                        }
                    }
                ),
                Tool(
                    name="agent_collaborate",
                    description="Enable direct collaboration between specific agents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "primary_agent": {
                                "type": "string",
                                "description": "Primary agent type for the collaboration"
                            },
                            "collaborating_agents": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Other agent types to collaborate with"
                            },
                            "task": {
                                "type": "string",
                                "description": "Collaborative task description"
                            }
                        },
                        "required": ["primary_agent", "task"]
                    }
                ),
                Tool(
                    name="swarm_memory_store",
                    description="Store information in shared swarm memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "namespace": {
                                "type": "string",
                                "description": "Memory namespace (e.g., 'project', 'user_preferences')"
                            },
                            "key": {
                                "type": "string",
                                "description": "Memory key identifier"
                            },
                            "value": {
                                "type": "string", 
                                "description": "Data to store"
                            },
                            "access_level": {
                                "type": "string",
                                "enum": ["private", "team", "public"],
                                "description": "Access level for the stored data",
                                "default": "team"
                            },
                            "ttl_hours": {
                                "type": "number",
                                "description": "Time to live in hours (optional)",
                                "default": null
                            }
                        },
                        "required": ["namespace", "key", "value"]
                    }
                ),
                Tool(
                    name="swarm_memory_retrieve",
                    description="Retrieve information from shared swarm memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "namespace": {
                                "type": "string",
                                "description": "Memory namespace to search"
                            },
                            "key": {
                                "type": "string", 
                                "description": "Memory key to retrieve"
                            }
                        },
                        "required": ["namespace", "key"]
                    }
                ),
                # Include all autonomous tools from parent class
                *await super().setup_handlers().__await__()
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle swarm intelligence tool calls"""
            await self.setup_session()
            
            try:
                if name == "swarm_execute":
                    return await self.handle_swarm_execute(arguments)
                elif name == "swarm_status":
                    return await self.handle_swarm_status(arguments)
                elif name == "agent_collaborate":
                    return await self.handle_agent_collaborate(arguments)
                elif name == "swarm_memory_store":
                    return await self.handle_swarm_memory_store(arguments)
                elif name == "swarm_memory_retrieve":
                    return await self.handle_swarm_memory_retrieve(arguments)
                else:
                    # Delegate to parent autonomous server
                    return await super().handle_call_tool(name, arguments)
                    
            except Exception as e:
                logging.error(f"Swarm tool execution error: {str(e)}")
                return [TextContent(type="text", text=f"Swarm Error: {str(e)}")]

    async def handle_swarm_execute(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle swarm task execution"""
        task_description = args["task_description"]
        context = args.get("context", {})
        preferred_agents = args.get("preferred_agents", [])
        priority = args.get("priority", "medium")
        
        # Store task context in swarm memory
        task_id = str(uuid.uuid4())
        self.memory_system.store_memory(
            "swarm_tasks", task_id, 
            {"description": task_description, "context": context, "priority": priority},
            access_level="team", ttl_hours=24
        )
        
        # Execute through Queen Agent
        result = await self.queen_agent.orchestrate_swarm_task(task_description, context)
        
        # Format response
        response = f"🐝 **Swarm Intelligence Execution**\n\n"
        response += f"**Task**: {task_description}\n"
        response += f"**Priority**: {priority.upper()}\n"
        response += f"**Task ID**: {task_id}\n\n"
        
        if result["success"]:
            response += f"✅ **Success**: {result['tasks_completed']}/{result['tasks_created']} tasks completed\n\n"
            response += result["final_result"]
            
            if "detailed_results" in result:
                response += "\n\n**Detailed Agent Execution:**\n"
                for detail in result["detailed_results"]:
                    if detail["success"]:
                        response += f"• {detail['task_title']} → {detail['agent_type']} agent\n"
        else:
            response += f"❌ **Failed**: {result.get('error', 'Unknown error')}\n"
        
        return [TextContent(type="text", text=response)]

    async def handle_swarm_status(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle swarm status requests"""
        include_metrics = args.get("include_metrics", False)
        
        # Get active agents
        active_agents = self.memory_system.get_active_agents()
        
        response = f"🐝 **Swarm Status Report**\n\n"
        response += f"**Queen Agent**: {self.queen_agent.status.value.title()}\n"
        response += f"**Active Agents**: {len(active_agents)}\n"
        response += f"**Total Agent Types**: {len(self.specialized_agents)}\n\n"
        
        response += "**Agent Roster**:\n"
        for agent in active_agents:
            status_emoji = {
                AgentStatus.IDLE: "💤",
                AgentStatus.WORKING: "⚡",
                AgentStatus.COLLABORATING: "🤝",
                AgentStatus.ERROR: "❌"
            }.get(agent.status, "❓")
            
            response += f"{status_emoji} **{agent.type.value.title()}** ({agent.id})\n"
            response += f"   Status: {agent.status.value} | Workload: {agent.workload:.1f}\n"
            response += f"   Active Tasks: {len(agent.current_tasks)}\n"
            
            if include_metrics and agent.performance_metrics:
                response += f"   Performance: {agent.performance_metrics}\n"
            
            response += "\n"
        
        # Add memory system stats
        conn = sqlite3.connect(self.memory_system.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM swarm_memory")
        memory_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM swarm_tasks")
        task_count = cursor.fetchone()[0]
        conn.close()
        
        response += f"**Memory System**:\n"
        response += f"• Stored memories: {memory_count}\n"  
        response += f"• Historical tasks: {task_count}\n"
        response += f"• Database: {self.memory_system.db_path}\n"
        
        return [TextContent(type="text", text=response)]

    async def handle_agent_collaborate(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle agent collaboration requests"""
        primary_agent = args["primary_agent"]
        collaborating_agents = args.get("collaborating_agents", [])
        task = args["task"]
        
        response = f"🤝 **Agent Collaboration Session**\n\n"
        response += f"**Primary Agent**: {primary_agent}\n"
        response += f"**Collaborating Agents**: {', '.join(collaborating_agents)}\n"
        response += f"**Task**: {task}\n\n"
        
        # Store collaboration context
        collab_id = str(uuid.uuid4())
        self.memory_system.store_memory(
            "collaborations", collab_id,
            {
                "primary": primary_agent,
                "collaborators": collaborating_agents,
                "task": task,
                "status": "active"
            },
            access_level="team", ttl_hours=8
        )
        
        response += "**Collaboration Plan**:\n"
        response += f"1. {primary_agent} agent leads the task execution\n"
        
        for i, collab_agent in enumerate(collaborating_agents, 2):
            response += f"{i}. {collab_agent} agent provides specialized support\n"
        
        response += f"\n**Collaboration ID**: {collab_id}\n"
        response += "Use this ID to track collaboration progress and results."
        
        return [TextContent(type="text", text=response)]

    async def handle_swarm_memory_store(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle swarm memory storage"""
        namespace = args["namespace"]
        key = args["key"]
        value = args["value"]
        access_level = args.get("access_level", "team")
        ttl_hours = args.get("ttl_hours")
        
        memory_id = self.memory_system.store_memory(
            namespace, key, value, 
            access_level=access_level, ttl_hours=ttl_hours
        )
        
        response = f"💾 **Swarm Memory Stored**\n\n"
        response += f"**Namespace**: {namespace}\n"
        response += f"**Key**: {key}\n"
        response += f"**Access Level**: {access_level}\n"
        if ttl_hours:
            response += f"**Expires**: {ttl_hours} hours\n"
        response += f"**Memory ID**: {memory_id}\n"
        
        return [TextContent(type="text", text=response)]

    async def handle_swarm_memory_retrieve(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle swarm memory retrieval"""
        namespace = args["namespace"]
        key = args["key"]
        
        value = self.memory_system.retrieve_memory(namespace, key)
        
        if value is not None:
            response = f"💾 **Swarm Memory Retrieved**\n\n"
            response += f"**Namespace**: {namespace}\n"
            response += f"**Key**: {key}\n"
            response += f"**Value**: {json.dumps(value, indent=2)}"
        else:
            response = f"❌ **Memory Not Found**\n\n"
            response += f"No data found for namespace '{namespace}' and key '{key}'\n"
            response += "This could mean:\n"
            response += "• The data doesn't exist\n"
            response += "• You don't have access permissions\n"
            response += "• The data has expired"
        
        return [TextContent(type="text", text=response)]

    async def run(self):
        """Run the swarm MCP server"""
        self.setup_handlers()
        
        async with self.server.stdio_transport() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ai-platform-mcp-swarm",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={
                            "swarm_intelligence": True,
                            "multi_agent_coordination": True,
                            "distributed_memory": True,
                            "collaborative_problem_solving": True,
                            "autonomous_execution": True,
                            "file_operations": True,
                            "command_execution": True
                        },
                    ),
                )
            )

async def main():
    """Main entry point for Swarm AI Platform MCP Server"""
    server = SwarmMCPServer()
    try:
        logging.info("Starting Swarm AI Platform MCP Server...")
        await server.run()
    except KeyboardInterrupt:
        logging.info("Server shutdown requested")
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
    finally:
        await server.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())