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

# Firecrawl integration
from firecrawl_service import FirecrawlService

# MCP SDK imports
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
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
    web_crawling: bool = False
    data_extraction: bool = False
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
    
    def get_web_research_results(self, result_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve web research results from memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if result_type:
            # Get specific type of web research results
            cursor.execute("""
                SELECT namespace, key, value, created_at, metadata 
                FROM swarm_memory 
                WHERE namespace = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (f"web_research_{result_type}", limit))
        else:
            # Get all web research results
            cursor.execute("""
                SELECT namespace, key, value, created_at, metadata 
                FROM swarm_memory 
                WHERE namespace LIKE 'web_research_%' 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            try:
                results.append({
                    'namespace': row[0],
                    'key': row[1],
                    'data': json.loads(row[2]),
                    'created_at': row[3],
                    'metadata': json.loads(row[4]) if row[4] else {}
                })
            except json.JSONDecodeError:
                continue
        
        conn.close()
        return results
    
    def search_web_research_content(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search through stored web research content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple text search in web research results
        cursor.execute("""
            SELECT namespace, key, value, created_at 
            FROM swarm_memory 
            WHERE namespace LIKE 'web_research_%' 
            AND (key LIKE ? OR value LIKE ?)
            ORDER BY created_at DESC 
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            try:
                results.append({
                    'namespace': row[0],
                    'key': row[1],
                    'data': json.loads(row[2]),
                    'created_at': row[3]
                })
            except json.JSONDecodeError:
                continue
        
        conn.close()
        return results
    
    def get_research_analytics(self) -> Dict[str, Any]:
        """Get analytics on web research activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count by research type
        cursor.execute("""
            SELECT namespace, COUNT(*) as count
            FROM swarm_memory 
            WHERE namespace LIKE 'web_research_%'
            GROUP BY namespace
        """)
        counts_by_type = {row[0].replace('web_research_', ''): row[1] for row in cursor.fetchall()}
        
        # Total research activities
        cursor.execute("""
            SELECT COUNT(*) FROM swarm_memory 
            WHERE namespace LIKE 'web_research_%'
        """)
        total_count = cursor.fetchone()[0]
        
        # Recent activity (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) FROM swarm_memory 
            WHERE namespace LIKE 'web_research_%'
            AND created_at > datetime('now', '-1 day')
        """)
        recent_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_research_items': total_count,
            'recent_activity_24h': recent_count,
            'activity_by_type': counts_by_type,
            'most_active_type': max(counts_by_type, key=counts_by_type.get) if counts_by_type else None
        }

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

class WebResearchAgent(BaseAgent):
    """Specialized agent for web research, crawling, and data extraction using Firecrawl"""
    
    def __init__(self, memory_system: SwarmMemorySystem, firecrawl_service: Optional[FirecrawlService] = None):
        capabilities = AgentCapabilities(
            research=True,
            web_search=True,
            web_crawling=True,
            data_extraction=True,
            analysis=True,
            api_integration=True,
            domains=["web_research", "competitive_analysis", "market_research", 
                    "content_analysis", "data_mining", "trend_analysis"]
        )
        super().__init__("web-researcher-001", AgentType.RESEARCHER, capabilities, memory_system)
        self.firecrawl_service = firecrawl_service
        
    async def _process_task(self, task: SwarmTask) -> Any:
        """Process web research tasks using Firecrawl capabilities"""
        if not self.firecrawl_service:
            return "Web research service not available - Firecrawl not configured"
        
        task_context = task.context or {}
        research_type = task_context.get('research_type', 'general')
        
        try:
            if research_type == 'crawl_website':
                return await self._handle_website_crawl(task)
            elif research_type == 'scrape_page':
                return await self._handle_page_scrape(task)
            elif research_type == 'web_search':
                return await self._handle_web_search(task)
            elif research_type == 'extract_data':
                return await self._handle_data_extraction(task)
            elif research_type == 'site_map':
                return await self._handle_site_mapping(task)
            elif research_type == 'intelligent_research':
                return await self._handle_intelligent_research(task)
            else:
                # General research - determine best approach based on task description
                return await self._handle_general_research(task)
                
        except Exception as e:
            return f"Web research error: {str(e)}"
    
    async def _handle_website_crawl(self, task: SwarmTask) -> str:
        """Handle website crawling requests"""
        context = task.context or {}
        url = context.get('url', '')
        max_pages = context.get('max_pages', 5)
        
        if not url:
            return "No URL provided for website crawl"
        
        result = await self.firecrawl_service.crawl_website(
            url=url,
            max_pages=max_pages,
            include_paths=context.get('include_paths'),
            exclude_paths=context.get('exclude_paths'),
            wait_for_selector=context.get('wait_for_selector')
        )
        
        if result['success']:
            # Store results in swarm memory
            crawl_id = str(uuid.uuid4())
            self.memory_system.store_memory(
                "web_research_crawls", crawl_id, result,
                access_level="team", ttl_hours=48
            )
            
            return f"Successfully crawled {result['pages_crawled']} pages from {url}. " \
                   f"Results stored with ID: {crawl_id}"
        else:
            return f"Failed to crawl {url}: {result.get('error', 'Unknown error')}"
    
    async def _handle_page_scrape(self, task: SwarmTask) -> str:
        """Handle single page scraping requests"""
        context = task.context or {}
        url = context.get('url', '')
        
        if not url:
            return "No URL provided for page scraping"
        
        result = await self.firecrawl_service.scrape_page(
            url=url,
            format=context.get('format', 'markdown'),
            wait_for_selector=context.get('wait_for_selector'),
            include_tags=context.get('include_tags'),
            exclude_tags=context.get('exclude_tags')
        )
        
        if result['success']:
            # Store results in swarm memory
            scrape_id = str(uuid.uuid4())
            self.memory_system.store_memory(
                "web_research_scrapes", scrape_id, result,
                access_level="team", ttl_hours=24
            )
            
            content_length = len(result.get('content', ''))
            return f"Successfully scraped {url} ({content_length} characters). " \
                   f"Results stored with ID: {scrape_id}"
        else:
            return f"Failed to scrape {url}: {result.get('error', 'Unknown error')}"
    
    async def _handle_web_search(self, task: SwarmTask) -> str:
        """Handle web search requests"""
        context = task.context or {}
        query = context.get('query', task.description)
        
        result = await self.firecrawl_service.search_web(
            query=query,
            num_results=context.get('num_results', 10),
            include_domains=context.get('include_domains'),
            exclude_domains=context.get('exclude_domains')
        )
        
        if result['success']:
            # Store results in swarm memory
            search_id = str(uuid.uuid4())
            self.memory_system.store_memory(
                "web_research_searches", search_id, result,
                access_level="team", ttl_hours=12
            )
            
            return f"Found {result['num_results']} search results for '{query}'. " \
                   f"Results stored with ID: {search_id}"
        else:
            return f"Failed to search for '{query}': {result.get('error', 'Unknown error')}"
    
    async def _handle_data_extraction(self, task: SwarmTask) -> str:
        """Handle structured data extraction requests"""
        context = task.context or {}
        url = context.get('url', '')
        schema_fields = context.get('schema_fields', {})
        
        if not url or not schema_fields:
            return "URL and schema_fields required for data extraction"
        
        result = await self.firecrawl_service.extract_structured_data(
            url=url,
            schema=self.firecrawl_service.create_extraction_schema(schema_fields),
            wait_for_selector=context.get('wait_for_selector')
        )
        
        if result['success']:
            # Store results in swarm memory
            extract_id = str(uuid.uuid4())
            self.memory_system.store_memory(
                "web_research_extractions", extract_id, result,
                access_level="team", ttl_hours=24
            )
            
            extracted_count = len(result.get('extracted_data', {}))
            return f"Successfully extracted {extracted_count} data fields from {url}. " \
                   f"Results stored with ID: {extract_id}"
        else:
            return f"Failed to extract data from {url}: {result.get('error', 'Unknown error')}"
    
    async def _handle_site_mapping(self, task: SwarmTask) -> str:
        """Handle website mapping requests"""
        context = task.context or {}
        url = context.get('url', '')
        
        if not url:
            return "No URL provided for site mapping"
        
        result = await self.firecrawl_service.map_website(
            url=url,
            max_depth=context.get('max_depth', 3),
            include_subdomains=context.get('include_subdomains', False)
        )
        
        if result['success']:
            # Store results in swarm memory
            map_id = str(uuid.uuid4())
            self.memory_system.store_memory(
                "web_research_sitemaps", map_id, result,
                access_level="team", ttl_hours=48
            )
            
            return f"Successfully mapped {result['total_links']} links from {url}. " \
                   f"Site map stored with ID: {map_id}"
        else:
            return f"Failed to map {url}: {result.get('error', 'Unknown error')}"
    
    async def _handle_intelligent_research(self, task: SwarmTask) -> str:
        """Handle intelligent research requests that combine search + analysis"""
        context = task.context or {}
        topic = context.get('topic', task.description)
        max_sources = context.get('max_sources', 5)
        
        result = await self.firecrawl_service.intelligent_research(
            topic=topic,
            max_sources=max_sources,
            extract_facts=context.get('extract_facts', True)
        )
        
        if result['success']:
            # Store results in swarm memory
            research_id = str(uuid.uuid4())
            self.memory_system.store_memory(
                "web_research_intelligence", research_id, result,
                access_level="team", ttl_hours=24
            )
            
            sources_count = result['sources_researched']
            return f"Completed intelligent research on '{topic}' using {sources_count} sources. " \
                   f"Comprehensive analysis stored with ID: {research_id}"
        else:
            return f"Failed to research '{topic}': {result.get('error', 'Unknown error')}"
    
    async def _handle_general_research(self, task: SwarmTask) -> str:
        """Handle general research tasks by analyzing description and choosing best approach"""
        description = task.description.lower()
        
        # Simple keyword-based routing
        if any(keyword in description for keyword in ['crawl', 'spider', 'entire site']):
            # Default crawl context
            task.context = task.context or {}
            if 'research_type' not in task.context:
                task.context['research_type'] = 'crawl_website'
            return await self._handle_website_crawl(task)
        
        elif any(keyword in description for keyword in ['scrape', 'single page', 'specific page']):
            task.context = task.context or {}
            if 'research_type' not in task.context:
                task.context['research_type'] = 'scrape_page'
            return await self._handle_page_scrape(task)
        
        elif any(keyword in description for keyword in ['search', 'find', 'look for']):
            task.context = task.context or {}
            if 'research_type' not in task.context:
                task.context['research_type'] = 'intelligent_research'
                task.context['topic'] = task.description
            return await self._handle_intelligent_research(task)
        
        else:
            # Default to intelligent research
            task.context = task.context or {}
            task.context['topic'] = task.description
            return await self._handle_intelligent_research(task)

class SwarmMCPServer(AutonomousAIPlatformMCPServer):
    """Enhanced MCP server with swarm intelligence capabilities"""
    
    def __init__(self):
        super().__init__()
        self.server = Server("ai-platform-mcp-swarm")
        
        # Initialize swarm components
        self.memory_system = SwarmMemorySystem()
        self.queen_agent = QueenAgent(self.memory_system)
        self.specialized_agents = {}
        
        # Initialize Firecrawl service
        try:
            self.firecrawl_service = FirecrawlService()
            logging.info("Firecrawl service initialized successfully")
        except Exception as e:
            logging.warning(f"Firecrawl service not available: {str(e)}")
            self.firecrawl_service = None
        
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
                web_crawling=True, data_extraction=True,
                domains=["information_gathering", "market_research", "technology_analysis", 
                        "web_scraping", "competitive_analysis", "trend_research"]
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
            
            # Use specialized WebResearchAgent for RESEARCHER type
            if agent_type == AgentType.RESEARCHER:
                agent = WebResearchAgent(self.memory_system, self.firecrawl_service)
            else:
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
                Tool(
                    name="swarm_web_crawl",
                    description="Crawl a website using Firecrawl integration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "Base URL to crawl"
                            },
                            "max_pages": {
                                "type": "number",
                                "description": "Maximum number of pages to crawl",
                                "default": 5
                            },
                            "include_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific paths to include in crawl"
                            },
                            "exclude_paths": {
                                "type": "array", 
                                "items": {"type": "string"},
                                "description": "Paths to exclude from crawl"
                            },
                            "wait_for_selector": {
                                "type": "string",
                                "description": "CSS selector to wait for before scraping"
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="swarm_web_scrape",
                    description="Scrape a single webpage using Firecrawl",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to scrape"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["markdown", "html", "raw-html"],
                                "description": "Output format for scraped content",
                                "default": "markdown"
                            },
                            "wait_for_selector": {
                                "type": "string",
                                "description": "CSS selector to wait for"
                            },
                            "include_tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "HTML tags to include in scraping"
                            },
                            "exclude_tags": {
                                "type": "array",
                                "items": {"type": "string"}, 
                                "description": "HTML tags to exclude from scraping"
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="swarm_web_search",
                    description="Search the web and get results using Firecrawl",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "num_results": {
                                "type": "number",
                                "description": "Number of search results to return",
                                "default": 10
                            },
                            "include_domains": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Domains to include in search results"
                            },
                            "exclude_domains": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Domains to exclude from search results"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="swarm_extract_data",
                    description="Extract structured data from a webpage using schema",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to extract data from"
                            },
                            "schema_fields": {
                                "type": "object",
                                "description": "Fields to extract with descriptions",
                                "additionalProperties": {"type": "string"}
                            },
                            "wait_for_selector": {
                                "type": "string",
                                "description": "CSS selector to wait for"
                            }
                        },
                        "required": ["url", "schema_fields"]
                    }
                ),
                Tool(
                    name="swarm_site_map",
                    description="Create a sitemap of a website using Firecrawl",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "Base URL to map"
                            },
                            "max_depth": {
                                "type": "number",
                                "description": "Maximum crawl depth",
                                "default": 3
                            },
                            "include_subdomains": {
                                "type": "boolean",
                                "description": "Whether to include subdomains",
                                "default": false
                            }
                        },
                        "required": ["url"]
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
                elif name == "swarm_web_crawl":
                    return await self.handle_swarm_web_crawl(arguments)
                elif name == "swarm_web_scrape":
                    return await self.handle_swarm_web_scrape(arguments)
                elif name == "swarm_web_search":
                    return await self.handle_swarm_web_search(arguments)
                elif name == "swarm_extract_data":
                    return await self.handle_swarm_extract_data(arguments)
                elif name == "swarm_site_map":
                    return await self.handle_swarm_site_map(arguments)
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

    async def handle_swarm_web_crawl(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle website crawling using Firecrawl"""
        if not self.firecrawl_service:
            return [TextContent(type="text", text="❌ **Firecrawl service not available**\n\nPlease configure FIRECRAWL_API_KEY in your environment.")]
        
        url = args["url"]
        max_pages = args.get("max_pages", 5)
        include_paths = args.get("include_paths")
        exclude_paths = args.get("exclude_paths")
        wait_for_selector = args.get("wait_for_selector")
        
        try:
            result = await self.firecrawl_service.crawl_website(
                url=url,
                max_pages=max_pages,
                include_paths=include_paths,
                exclude_paths=exclude_paths,
                wait_for_selector=wait_for_selector
            )
            
            if result['success']:
                # Store crawl results in swarm memory
                crawl_id = str(uuid.uuid4())
                self.memory_system.store_memory(
                    "web_crawl_results", crawl_id, result,
                    access_level="team", ttl_hours=48
                )
                
                response = f"🕸️ **Website Crawl Complete**\n\n"
                response += f"**URL**: {url}\n"
                response += f"**Pages Crawled**: {result['pages_crawled']}\n"
                response += f"**Crawl ID**: {crawl_id}\n\n"
                response += "**Summary of crawled content**:\n"
                
                for i, page in enumerate(result['data'][:3]):  # Show first 3 pages
                    page_url = page.get('metadata', {}).get('sourceURL', 'Unknown URL')
                    page_title = page.get('metadata', {}).get('title', 'Untitled')
                    response += f"{i+1}. [{page_title}]({page_url})\n"
                
                if len(result['data']) > 3:
                    response += f"... and {len(result['data']) - 3} more pages\n"
                
                response += f"\n💾 Results stored in swarm memory with ID: {crawl_id}"
            else:
                response = f"❌ **Crawl Failed**\n\n**URL**: {url}\n**Error**: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            response = f"❌ **Crawl Error**\n\n**URL**: {url}\n**Error**: {str(e)}"
        
        return [TextContent(type="text", text=response)]

    async def handle_swarm_web_scrape(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle single webpage scraping using Firecrawl"""
        if not self.firecrawl_service:
            return [TextContent(type="text", text="❌ **Firecrawl service not available**\n\nPlease configure FIRECRAWL_API_KEY in your environment.")]
        
        url = args["url"]
        format = args.get("format", "markdown")
        wait_for_selector = args.get("wait_for_selector")
        include_tags = args.get("include_tags")
        exclude_tags = args.get("exclude_tags")
        
        try:
            result = await self.firecrawl_service.scrape_page(
                url=url,
                format=format,
                wait_for_selector=wait_for_selector,
                include_tags=include_tags,
                exclude_tags=exclude_tags
            )
            
            if result['success']:
                # Store scrape results in swarm memory
                scrape_id = str(uuid.uuid4())
                self.memory_system.store_memory(
                    "web_scrape_results", scrape_id, result,
                    access_level="team", ttl_hours=24
                )
                
                content = result['content'][:1000] + "..." if len(result['content']) > 1000 else result['content']
                
                response = f"📄 **Webpage Scraped**\n\n"
                response += f"**URL**: {url}\n"
                response += f"**Format**: {format}\n"
                response += f"**Scrape ID**: {scrape_id}\n\n"
                response += f"**Content Preview**:\n```\n{content}\n```\n\n"
                response += f"**Metadata**:\n"
                response += f"- Title: {result.get('metadata', {}).get('title', 'N/A')}\n"
                response += f"- Links found: {len(result.get('links', []))}\n"
                response += f"- Images found: {len(result.get('images', []))}\n\n"
                response += f"💾 Full results stored in swarm memory with ID: {scrape_id}"
            else:
                response = f"❌ **Scrape Failed**\n\n**URL**: {url}\n**Error**: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            response = f"❌ **Scrape Error**\n\n**URL**: {url}\n**Error**: {str(e)}"
        
        return [TextContent(type="text", text=response)]

    async def handle_swarm_web_search(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle web search using Firecrawl"""
        if not self.firecrawl_service:
            return [TextContent(type="text", text="❌ **Firecrawl service not available**\n\nPlease configure FIRECRAWL_API_KEY in your environment.")]
        
        query = args["query"]
        num_results = args.get("num_results", 10)
        include_domains = args.get("include_domains")
        exclude_domains = args.get("exclude_domains")
        
        try:
            result = await self.firecrawl_service.search_web(
                query=query,
                num_results=num_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )
            
            if result['success']:
                # Store search results in swarm memory
                search_id = str(uuid.uuid4())
                self.memory_system.store_memory(
                    "web_search_results", search_id, result,
                    access_level="team", ttl_hours=12
                )
                
                response = f"🔍 **Web Search Complete**\n\n"
                response += f"**Query**: {query}\n"
                response += f"**Results Found**: {result['num_results']}\n"
                response += f"**Search ID**: {search_id}\n\n"
                response += "**Top Results**:\n"
                
                for i, search_result in enumerate(result['results'][:5], 1):
                    title = search_result.get('title', 'Untitled')
                    url = search_result.get('url', 'No URL')
                    response += f"{i}. **{title}**\n   {url}\n"
                
                if len(result['results']) > 5:
                    response += f"\n... and {len(result['results']) - 5} more results\n"
                
                response += f"\n💾 Full results stored in swarm memory with ID: {search_id}"
            else:
                response = f"❌ **Search Failed**\n\n**Query**: {query}\n**Error**: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            response = f"❌ **Search Error**\n\n**Query**: {query}\n**Error**: {str(e)}"
        
        return [TextContent(type="text", text=response)]

    async def handle_swarm_extract_data(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle structured data extraction using Firecrawl"""
        if not self.firecrawl_service:
            return [TextContent(type="text", text="❌ **Firecrawl service not available**\n\nPlease configure FIRECRAWL_API_KEY in your environment.")]
        
        url = args["url"]
        schema_fields = args["schema_fields"]
        wait_for_selector = args.get("wait_for_selector")
        
        try:
            # Create extraction schema
            schema = self.firecrawl_service.create_extraction_schema(schema_fields)
            
            result = await self.firecrawl_service.extract_structured_data(
                url=url,
                schema=schema,
                wait_for_selector=wait_for_selector
            )
            
            if result['success']:
                # Store extraction results in swarm memory
                extract_id = str(uuid.uuid4())
                self.memory_system.store_memory(
                    "data_extraction_results", extract_id, result,
                    access_level="team", ttl_hours=24
                )
                
                response = f"📊 **Data Extraction Complete**\n\n"
                response += f"**URL**: {url}\n"
                response += f"**Extract ID**: {extract_id}\n\n"
                response += f"**Extracted Data**:\n```json\n{json.dumps(result['extracted_data'], indent=2)}\n```\n\n"
                response += f"💾 Full results stored in swarm memory with ID: {extract_id}"
            else:
                response = f"❌ **Extraction Failed**\n\n**URL**: {url}\n**Error**: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            response = f"❌ **Extraction Error**\n\n**URL**: {url}\n**Error**: {str(e)}"
        
        return [TextContent(type="text", text=response)]

    async def handle_swarm_site_map(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle website mapping using Firecrawl"""
        if not self.firecrawl_service:
            return [TextContent(type="text", text="❌ **Firecrawl service not available**\n\nPlease configure FIRECRAWL_API_KEY in your environment.")]
        
        url = args["url"]
        max_depth = args.get("max_depth", 3)
        include_subdomains = args.get("include_subdomains", False)
        
        try:
            result = await self.firecrawl_service.map_website(
                url=url,
                max_depth=max_depth,
                include_subdomains=include_subdomains
            )
            
            if result['success']:
                # Store sitemap results in swarm memory
                map_id = str(uuid.uuid4())
                self.memory_system.store_memory(
                    "website_map_results", map_id, result,
                    access_level="team", ttl_hours=48
                )
                
                response = f"🗺️ **Website Map Complete**\n\n"
                response += f"**URL**: {url}\n"
                response += f"**Total Links**: {result['total_links']}\n"
                response += f"**Max Depth**: {max_depth}\n"
                response += f"**Include Subdomains**: {include_subdomains}\n"
                response += f"**Map ID**: {map_id}\n\n"
                
                if result['links']:
                    response += f"**Sample Links**:\n"
                    for link in result['links'][:10]:
                        response += f"- {link}\n"
                    
                    if len(result['links']) > 10:
                        response += f"... and {len(result['links']) - 10} more links\n"
                
                response += f"\n💾 Full sitemap stored in swarm memory with ID: {map_id}"
            else:
                response = f"❌ **Site Mapping Failed**\n\n**URL**: {url}\n**Error**: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            response = f"❌ **Site Mapping Error**\n\n**URL**: {url}\n**Error**: {str(e)}"
        
        return [TextContent(type="text", text=response)]

    async def run(self):
        """Run the swarm MCP server"""
        self.setup_handlers()
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
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
        logging.info("Server shutdown complete")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())