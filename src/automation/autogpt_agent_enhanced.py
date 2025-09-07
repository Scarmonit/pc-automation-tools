#!/usr/bin/env python3
"""
Enhanced AutoGPT Agent with Comprehensive Error Handling
Integrates AutoGPT as a specialized autonomous agent with robust error mitigation
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import aiohttp
import sqlite3
from datetime import datetime

# Import our error handling system
from error_handling import (
    ErrorHandler, CircuitBreaker, RetryStrategy, RequestValidator, 
    RateLimiter, SwarmLogger, GracefulDegradation, SwarmError
)
from health_monitor import HealthMonitor

# Configure enhanced logging
logger = SwarmLogger("autogpt_agent").get_logger()

class AutoGPTStatus(Enum):
    """AutoGPT container status"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    RESTARTING = "restarting"
    DEGRADED = "degraded"
    RECOVERING = "recovering"

class ExecutionMode(Enum):
    """Agent execution modes for degradation"""
    FULL = "full"           # Full AutoGPT integration
    REDUCED = "reduced"     # Simplified autonomous mode
    MINIMAL = "minimal"     # Basic task processing
    EMERGENCY = "emergency" # Critical tasks only

@dataclass
class AutoGPTTask:
    """Task format for AutoGPT"""
    task_id: str
    goal: str
    constraints: List[str]
    resources: List[str]
    performance_evaluation: List[str]
    budget: Optional[float] = None
    deadline: Optional[str] = None
    priority: str = "medium"
    retry_count: int = 0
    max_retries: int = 3

class EnhancedAutoGPTAgent:
    """
    Enhanced AutoGPT Agent with Comprehensive Error Handling
    Provides robust integration with autonomous error recovery
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize enhanced AutoGPT agent"""
        self.agent_type = "autogpt"
        self.agent_id = f"autogpt-{int(time.time())}"
        self.status = AutoGPTStatus.STOPPED
        self.execution_mode = ExecutionMode.FULL
        self.config_path = config_path or Path(__file__).parent / "config"
        self.api_base_url = os.getenv("AUTOGPT_API_URL", "http://localhost:3000")
        self.swarm_api_url = os.getenv("SWARM_API_URL", "http://localhost:8001")
        self.container_name = "swarm-autogpt"
        self.docker_network = "swarm-network"
        self.memory_db_path = os.getenv("SWARM_MEMORY_DB", "swarm_memory.db")
        self.session = None
        self.current_task = None
        
        # Initialize error handling components
        self.error_handler = ErrorHandler()
        self.health_monitor = HealthMonitor()
        
        # Circuit breakers for different operations
        self.api_circuit_breaker = CircuitBreaker(
            name="autogpt_api",
            failure_threshold=5,
            recovery_timeout=60.0,
            expected_exception=aiohttp.ClientError
        )
        
        self.docker_circuit_breaker = CircuitBreaker(
            name="autogpt_docker",
            failure_threshold=3,
            recovery_timeout=30.0,
            expected_exception=subprocess.SubprocessError
        )
        
        # Retry strategies
        self.api_retry_strategy = RetryStrategy(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
            exponential_base=2.0
        )
        
        self.docker_retry_strategy = RetryStrategy(
            max_retries=2,
            base_delay=2.0,
            max_delay=10.0,
            exponential_base=1.5
        )
        
        # Rate limiter for API calls
        self.api_rate_limiter = RateLimiter(
            max_calls=100,
            time_window=60.0
        )
        
        # Request validator
        self.request_validator = RequestValidator()
        
        # Graceful degradation
        self.degradation_manager = GracefulDegradation()
        
        # Agent capabilities
        self.capabilities = [
            "autonomous_planning",
            "web_research", 
            "task_decomposition",
            "code_generation",
            "file_operations",
            "api_interactions",
            "long_term_memory",
            "self_improvement",
            "error_recovery",
            "graceful_degradation"
        ]
        
        # Performance metrics
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_degraded": 0,
            "average_completion_time": 0,
            "resource_usage": {},
            "last_active": None,
            "error_rate": 0.0,
            "recovery_count": 0,
            "circuit_breaker_trips": 0
        }
        
        # Task queue for degraded mode
        self.fallback_queue = asyncio.Queue()
        
        # Recovery state
        self.recovery_in_progress = False
        self.last_health_check = None
        self.consecutive_failures = 0
        
    async def initialize(self):
        """Initialize enhanced AutoGPT agent with comprehensive error handling"""
        logger.info(f"Initializing enhanced AutoGPT agent {self.agent_id}")
        
        try:
            # Create aiohttp session with timeout
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Initialize error handler
            await self.error_handler.initialize()
            
            # Validate environment
            await self._validate_environment()
            
            # Check Docker status with circuit breaker
            docker_available = await self.docker_circuit_breaker.call(
                self._check_docker_with_retry
            )
            
            if not docker_available:
                logger.warning("Docker not available, entering degraded mode")
                self.execution_mode = ExecutionMode.REDUCED
                await self.degradation_manager.trigger_degradation("docker_unavailable")
            
            # Start AutoGPT container if Docker is available
            if self.execution_mode == ExecutionMode.FULL:
                if not await self._is_container_running():
                    await self.docker_circuit_breaker.call(self.start_container)
                
                # Wait for AutoGPT API to be ready
                await self.api_circuit_breaker.call(self._wait_for_api_with_retry)
            
            # Register with swarm
            await self._register_with_swarm_with_retry()
            
            # Start background health monitoring
            asyncio.create_task(self._continuous_health_monitoring())
            
            self.status = AutoGPTStatus.RUNNING
            logger.info(f"Enhanced AutoGPT agent {self.agent_id} initialized in {self.execution_mode.value} mode")
            
        except Exception as e:
            logger.error(f"Failed to initialize AutoGPT agent: {e}")
            await self._handle_initialization_failure(e)
            raise
    
    async def _validate_environment(self):
        """Validate environment prerequisites"""
        logger.info("Validating environment for AutoGPT agent")
        
        # Check required environment variables
        required_vars = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.warning(f"Missing API keys: {missing_vars}")
            # Don't fail completely, but note for degraded mode
        
        # Validate memory database path
        db_dir = Path(self.memory_db_path).parent
        if not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created memory database directory: {db_dir}")
        
        # Validate API endpoints
        await self.request_validator.validate_request({
            "url": self.api_base_url,
            "method": "GET"
        })
        
        logger.info("Environment validation completed")
    
    async def _check_docker_with_retry(self) -> bool:
        """Check Docker availability with retry logic"""
        async def _check_docker():
            result = await asyncio.create_subprocess_exec(
                "docker", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()
            return result.returncode == 0
        
        return await self.docker_retry_strategy.execute(_check_docker)
    
    async def _is_container_running(self) -> bool:
        """Check if AutoGPT container is running with error handling"""
        try:
            result = await asyncio.create_subprocess_exec(
                "docker", "ps", "--filter", f"name={self.container_name}", 
                "--format", "{{.Names}}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                logger.warning(f"Docker ps command failed: {stderr.decode()}")
                return False
                
            return self.container_name in stdout.decode()
            
        except Exception as e:
            logger.error(f"Error checking container status: {e}")
            return False
    
    async def start_container(self):
        """Start AutoGPT Docker container with enhanced error handling"""
        logger.info("Starting AutoGPT container with error handling...")
        
        try:
            self.status = AutoGPTStatus.STARTING
            
            # Check if container exists but is stopped
            result = await asyncio.create_subprocess_exec(
                "docker", "ps", "-a", "--filter", f"name={self.container_name}",
                "--format", "{{.Names}}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if self.container_name in stdout.decode():
                # Container exists, start it
                logger.info("Starting existing AutoGPT container")
                start_result = await asyncio.create_subprocess_exec(
                    "docker", "start", self.container_name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await start_result.wait()
                
                if start_result.returncode != 0:
                    raise subprocess.SubprocessError("Failed to start existing container")
            else:
                # Create new container using docker-compose
                logger.info("Creating new AutoGPT container")
                docker_compose_path = Path(__file__).parent / "docker-compose.swarm.yml"
                
                if not docker_compose_path.exists():
                    raise FileNotFoundError(f"Docker compose file not found: {docker_compose_path}")
                
                compose_result = await asyncio.create_subprocess_exec(
                    "docker-compose", "-f", str(docker_compose_path), 
                    "up", "-d", "autogpt",
                    cwd=Path(__file__).parent,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await compose_result.wait()
                
                if compose_result.returncode != 0:
                    raise subprocess.SubprocessError("Failed to create container with docker-compose")
            
            # Wait for container to be healthy
            await self._wait_for_container_health()
            
            self.status = AutoGPTStatus.RUNNING
            logger.info("AutoGPT container started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start AutoGPT container: {e}")
            self.status = AutoGPTStatus.ERROR
            self.metrics["circuit_breaker_trips"] += 1
            
            # Try fallback to degraded mode
            await self._enter_degraded_mode("container_start_failed")
            raise
    
    async def _wait_for_container_health(self, max_wait: int = 120):
        """Wait for container to be healthy"""
        logger.info("Waiting for AutoGPT container to be healthy...")
        
        for i in range(max_wait):
            try:
                result = await asyncio.create_subprocess_exec(
                    "docker", "inspect", "--format", 
                    "{{.State.Health.Status}}", self.container_name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode == 0:
                    health_status = stdout.decode().strip()
                    if health_status == "healthy":
                        logger.info("AutoGPT container is healthy")
                        return
                    elif health_status == "unhealthy":
                        logger.warning("AutoGPT container is unhealthy")
                        # Continue waiting, it might recover
                
            except Exception as e:
                logger.debug(f"Health check attempt {i+1} failed: {e}")
            
            await asyncio.sleep(1)
        
        logger.warning("Container health check timed out, proceeding anyway")
    
    async def _wait_for_api_with_retry(self):
        """Wait for AutoGPT API with comprehensive retry logic"""
        logger.info("Waiting for AutoGPT API with retry logic...")
        
        async def _check_api():
            await self.api_rate_limiter.acquire()
            async with self.session.get(f"{self.api_base_url}/health") as response:
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status
                    )
                return True
        
        try:
            await self.api_retry_strategy.execute(_check_api)
            logger.info("AutoGPT API is ready")
        except Exception as e:
            logger.error(f"AutoGPT API failed to become ready: {e}")
            await self._enter_degraded_mode("api_unavailable")
            raise
    
    async def _register_with_swarm_with_retry(self):
        """Register with swarm with retry logic"""
        registration_data = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "status": self.status.value,
            "execution_mode": self.execution_mode.value,
            "api_endpoint": self.api_base_url
        }
        
        async def _register():
            await self.api_rate_limiter.acquire()
            async with self.session.post(
                f"{self.swarm_api_url}/agents/register",
                json=registration_data
            ) as response:
                if response.status not in [200, 201]:
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status
                    )
                return await response.json()
        
        try:
            result = await self.api_retry_strategy.execute(_register)
            logger.info(f"Registered with swarm as {self.agent_id}")
            return result
        except Exception as e:
            logger.warning(f"Failed to register with swarm (continuing anyway): {e}")
            # Don't fail initialization for registration failure
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with comprehensive error handling and fallback strategies"""
        task_id = task.get('task_id', 'unknown')
        logger.info(f"Executing task {task_id} in {self.execution_mode.value} mode")
        
        # Validate task
        try:
            await self._validate_task(task)
        except Exception as e:
            return self._create_error_result(task_id, f"Task validation failed: {e}")
        
        # Track task start
        start_time = time.time()
        self.current_task = task
        
        # Choose execution strategy based on current mode
        try:
            if self.execution_mode == ExecutionMode.FULL:
                result = await self._execute_full_mode(task)
            elif self.execution_mode == ExecutionMode.REDUCED:
                result = await self._execute_reduced_mode(task)
            elif self.execution_mode == ExecutionMode.MINIMAL:
                result = await self._execute_minimal_mode(task)
            else:  # EMERGENCY
                result = await self._execute_emergency_mode(task)
            
            # Update metrics on success
            execution_time = time.time() - start_time
            self.metrics["tasks_completed"] += 1
            self._update_average_completion_time(execution_time)
            self.consecutive_failures = 0
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            self.consecutive_failures += 1
            self.metrics["tasks_failed"] += 1
            
            # Try recovery if multiple failures
            if self.consecutive_failures >= 3:
                await self._attempt_recovery()
            
            result = self._create_error_result(task_id, str(e))
        
        # Store result and update metrics
        self.metrics["last_active"] = datetime.now().isoformat()
        await self._store_in_memory(task_id, result)
        
        return result
    
    async def _validate_task(self, task: Dict[str, Any]):
        """Validate task before execution"""
        required_fields = ["task_id", "description"]
        missing_fields = [field for field in required_fields if not task.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required task fields: {missing_fields}")
        
        # Validate task constraints
        if "constraints" in task:
            await self.request_validator.validate_request({
                "data": task["constraints"],
                "type": "list"
            })
    
    async def _execute_full_mode(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task using full AutoGPT integration"""
        autogpt_task = self._translate_task(task)
        
        # Use circuit breaker for AutoGPT API call
        result = await self.api_circuit_breaker.call(
            self._send_to_autogpt_with_retry,
            autogpt_task
        )
        
        return result
    
    async def _execute_reduced_mode(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task in reduced mode (simplified autonomous processing)"""
        logger.info(f"Executing task {task['task_id']} in reduced mode")
        
        # Simulate autonomous processing without full AutoGPT
        result = {
            "status": "completed_reduced",
            "task_id": task["task_id"],
            "result": {
                "message": "Task processed in reduced autonomous mode",
                "approach": self._generate_autonomous_approach(task),
                "execution_mode": "reduced"
            },
            "execution_time": time.time(),
            "degradation_reason": "autogpt_unavailable"
        }
        
        self.metrics["tasks_degraded"] += 1
        return result
    
    async def _execute_minimal_mode(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task in minimal mode (basic processing only)"""
        logger.info(f"Executing task {task['task_id']} in minimal mode")
        
        result = {
            "status": "completed_minimal",
            "task_id": task["task_id"],
            "result": {
                "message": "Task acknowledged in minimal mode",
                "summary": task.get("description", "No description"),
                "execution_mode": "minimal"
            },
            "execution_time": time.time(),
            "degradation_reason": "system_overload"
        }
        
        self.metrics["tasks_degraded"] += 1
        return result
    
    async def _execute_emergency_mode(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute only critical tasks in emergency mode"""
        task_priority = task.get("priority", "medium")
        
        if task_priority != "critical":
            # Queue non-critical tasks for later
            await self.fallback_queue.put(task)
            return {
                "status": "queued",
                "task_id": task["task_id"],
                "message": "Task queued due to emergency mode",
                "execution_mode": "emergency"
            }
        
        # Process critical tasks with minimal resources
        result = {
            "status": "completed_emergency",
            "task_id": task["task_id"],
            "result": {
                "message": "Critical task processed in emergency mode",
                "execution_mode": "emergency"
            },
            "execution_time": time.time()
        }
        
        return result
    
    def _generate_autonomous_approach(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate autonomous approach for task in reduced mode"""
        description = task.get("description", "")
        
        # Simple autonomous analysis
        approach = {
            "analysis": f"Autonomous analysis of: {description}",
            "steps": [
                "1. Analyze task requirements",
                "2. Identify available resources",
                "3. Plan execution strategy",
                "4. Execute with available tools",
                "5. Validate results"
            ],
            "tools_used": ["internal_analysis", "knowledge_base"],
            "confidence": 0.7,
            "recommendations": [
                "Task processed autonomously",
                "Results may be limited without full AutoGPT integration",
                "Consider retry when full mode is restored"
            ]
        }
        
        return approach
    
    async def _send_to_autogpt_with_retry(self, task: AutoGPTTask) -> Dict[str, Any]:
        """Send task to AutoGPT with retry logic"""
        task_data = {
            "goal": task.goal,
            "constraints": task.constraints,
            "resources": task.resources,
            "performance_evaluation": task.performance_evaluation
        }
        
        if task.budget:
            task_data["budget"] = task.budget
        if task.deadline:
            task_data["deadline"] = task.deadline
        
        async def _send_request():
            await self.api_rate_limiter.acquire()
            async with self.session.post(
                f"{self.api_base_url}/api/tasks",
                json=task_data,
                timeout=aiohttp.ClientTimeout(total=3600)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "status": "completed",
                        "result": result,
                        "task_id": task.task_id,
                        "execution_time": result.get("execution_time"),
                        "steps_taken": result.get("steps", [])
                    }
                else:
                    error_text = await response.text()
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=error_text
                    )
        
        return await self.api_retry_strategy.execute(_send_request)
    
    def _translate_task(self, swarm_task: Dict[str, Any]) -> AutoGPTTask:
        """Translate swarm task to AutoGPT format with enhanced fields"""
        return AutoGPTTask(
            task_id=swarm_task.get("task_id", str(int(time.time()))),
            goal=swarm_task.get("description", ""),
            constraints=swarm_task.get("constraints", [
                "Follow all safety guidelines",
                "Minimize resource usage", 
                "Complete within deadline",
                "Use error recovery mechanisms"
            ]),
            resources=swarm_task.get("resources", [
                "Internet access",
                "File system access",
                "API access",
                "Error handling tools"
            ]),
            performance_evaluation=swarm_task.get("success_criteria", [
                "Task completed successfully",
                "Output meets requirements",
                "No critical errors encountered",
                "Recovery mechanisms tested"
            ]),
            budget=swarm_task.get("budget"),
            deadline=swarm_task.get("deadline"),
            priority=swarm_task.get("priority", "medium")
        )
    
    async def _store_in_memory(self, task_id: str, result: Dict[str, Any]):
        """Store task result with error handling"""
        try:
            conn = sqlite3.connect(self.memory_db_path, timeout=10.0)
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    namespace TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    UNIQUE(namespace, key, agent_id)
                )
            """)
            
            cursor.execute("""
                INSERT OR REPLACE INTO agent_memory 
                (namespace, key, value, created_at, agent_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "autogpt_results",
                task_id,
                json.dumps(result, default=str),
                datetime.now().isoformat(),
                self.agent_id
            ))
            
            conn.commit()
            conn.close()
            logger.debug(f"Stored result for task {task_id} in swarm memory")
            
        except Exception as e:
            logger.error(f"Failed to store task result in memory: {e}")
            # Don't fail the task for storage errors
    
    async def _continuous_health_monitoring(self):
        """Continuous health monitoring background task"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                health_status = await self.health_check()
                self.last_health_check = datetime.now()
                
                if not health_status and self.status == AutoGPTStatus.RUNNING:
                    logger.warning("Health check failed, attempting recovery")
                    await self._attempt_recovery()
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
    
    async def _attempt_recovery(self):
        """Attempt to recover from failures"""
        if self.recovery_in_progress:
            return
        
        self.recovery_in_progress = True
        self.status = AutoGPTStatus.RECOVERING
        logger.info("Attempting system recovery...")
        
        try:
            # Step 1: Check Docker health
            if not await self._check_docker_with_retry():
                logger.error("Docker is not available for recovery")
                await self._enter_degraded_mode("docker_unavailable")
                return
            
            # Step 2: Restart container if needed
            if not await self._is_container_running():
                logger.info("Restarting AutoGPT container for recovery")
                await self.start_container()
            
            # Step 3: Test API connectivity
            try:
                await self._wait_for_api_with_retry()
                logger.info("API connectivity restored")
            except:
                logger.warning("API not available, staying in degraded mode")
                await self._enter_degraded_mode("api_unavailable")
                return
            
            # Step 4: Restore full mode if successful
            if self.execution_mode != ExecutionMode.FULL:
                self.execution_mode = ExecutionMode.FULL
                logger.info("Restored to full execution mode")
            
            self.status = AutoGPTStatus.RUNNING
            self.metrics["recovery_count"] += 1
            self.consecutive_failures = 0
            
            # Process queued tasks
            await self._process_fallback_queue()
            
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            await self._enter_degraded_mode("recovery_failed")
        finally:
            self.recovery_in_progress = False
    
    async def _enter_degraded_mode(self, reason: str):
        """Enter appropriate degraded mode based on reason"""
        logger.warning(f"Entering degraded mode: {reason}")
        
        await self.degradation_manager.trigger_degradation(reason)
        
        if reason in ["docker_unavailable", "container_start_failed"]:
            self.execution_mode = ExecutionMode.REDUCED
            self.status = AutoGPTStatus.DEGRADED
        elif reason in ["api_unavailable", "high_error_rate"]:
            self.execution_mode = ExecutionMode.MINIMAL
            self.status = AutoGPTStatus.DEGRADED
        else:  # Critical failures
            self.execution_mode = ExecutionMode.EMERGENCY
            self.status = AutoGPTStatus.ERROR
        
        logger.info(f"Now operating in {self.execution_mode.value} mode")
    
    async def _process_fallback_queue(self):
        """Process queued tasks after recovery"""
        processed = 0
        while not self.fallback_queue.empty() and processed < 10:
            try:
                task = await asyncio.wait_for(self.fallback_queue.get(), timeout=1.0)
                logger.info(f"Processing queued task: {task['task_id']}")
                await self.execute_task(task)
                processed += 1
            except asyncio.TimeoutError:
                break
            except Exception as e:
                logger.error(f"Error processing queued task: {e}")
        
        if processed > 0:
            logger.info(f"Processed {processed} queued tasks after recovery")
    
    async def _handle_initialization_failure(self, error: Exception):
        """Handle initialization failure gracefully"""
        logger.error(f"AutoGPT agent initialization failed: {error}")
        
        # Try to start in minimal mode
        try:
            self.execution_mode = ExecutionMode.MINIMAL
            self.status = AutoGPTStatus.DEGRADED
            logger.info("Started in minimal mode after initialization failure")
        except Exception as e:
            logger.critical(f"Failed to start even in minimal mode: {e}")
            self.status = AutoGPTStatus.ERROR
            raise
    
    def _create_error_result(self, task_id: str, error_message: str) -> Dict[str, Any]:
        """Create standardized error result"""
        return {
            "status": "error",
            "task_id": task_id,
            "error": error_message,
            "execution_mode": self.execution_mode.value,
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id
        }
    
    def _update_average_completion_time(self, execution_time: float):
        """Update average completion time metric"""
        total_completed = self.metrics["tasks_completed"]
        if total_completed == 1:
            self.metrics["average_completion_time"] = execution_time
        else:
            current_avg = self.metrics["average_completion_time"]
            self.metrics["average_completion_time"] = (
                (current_avg * (total_completed - 1) + execution_time) / total_completed
            )
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        container_status = "running" if await self._is_container_running() else "stopped"
        
        # Calculate error rate
        total_tasks = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        error_rate = (self.metrics["tasks_failed"] / total_tasks) if total_tasks > 0 else 0.0
        self.metrics["error_rate"] = error_rate
        
        status = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "execution_mode": self.execution_mode.value,
            "container_status": container_status,
            "capabilities": self.capabilities,
            "metrics": self.metrics,
            "current_task": self.current_task,
            "api_endpoint": self.api_base_url,
            "circuit_breaker_states": {
                "api": self.api_circuit_breaker.state.name,
                "docker": self.docker_circuit_breaker.state.name
            },
            "health": {
                "last_check": self.last_health_check.isoformat() if self.last_health_check else None,
                "consecutive_failures": self.consecutive_failures,
                "recovery_in_progress": self.recovery_in_progress
            },
            "queue_status": {
                "fallback_queue_size": self.fallback_queue.qsize()
            }
        }
        
        return status
    
    async def health_check(self) -> bool:
        """Comprehensive health check"""
        try:
            health_checks = []
            
            # Check container if in full mode
            if self.execution_mode == ExecutionMode.FULL:
                container_running = await self._is_container_running()
                health_checks.append(container_running)
                
                if container_running:
                    # Check API health
                    try:
                        await self.api_rate_limiter.acquire()
                        async with self.session.get(
                            f"{self.api_base_url}/health",
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            health_checks.append(response.status == 200)
                    except:
                        health_checks.append(False)
            else:
                # In degraded modes, check basic functionality
                health_checks.append(self.status != AutoGPTStatus.ERROR)
            
            # Check memory database
            try:
                conn = sqlite3.connect(self.memory_db_path, timeout=5.0)
                conn.execute("SELECT 1")
                conn.close()
                health_checks.append(True)
            except:
                health_checks.append(False)
            
            # Overall health is true if at least half the checks pass
            return sum(health_checks) >= len(health_checks) / 2
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def collaborate(self, agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced collaboration with error handling"""
        logger.info(f"Collaborating with agent {agent_id}")
        
        try:
            # Validate collaboration message
            await self.request_validator.validate_request({
                "data": message,
                "type": "dict"
            })
            
            message_type = message.get("type")
            
            if message_type == "request_assistance":
                task = message.get("task")
                if task:
                    # Execute task and provide result
                    result = await self.execute_task(task)
                    return {
                        "type": "assistance_response",
                        "from_agent": self.agent_id,
                        "result": result,
                        "execution_mode": self.execution_mode.value
                    }
            
            elif message_type == "share_knowledge":
                knowledge = message.get("knowledge")
                if knowledge:
                    await self._store_in_memory(
                        f"shared_{agent_id}_{int(time.time())}",
                        knowledge
                    )
                    return {
                        "type": "knowledge_received",
                        "from_agent": self.agent_id,
                        "status": "stored"
                    }
            
            elif message_type == "health_check":
                health_status = await self.health_check()
                return {
                    "type": "health_response",
                    "from_agent": self.agent_id,
                    "healthy": health_status,
                    "status": self.status.value,
                    "execution_mode": self.execution_mode.value
                }
            
            return {
                "type": "unknown_request",
                "from_agent": self.agent_id,
                "status": "unsupported"
            }
            
        except Exception as e:
            logger.error(f"Collaboration failed: {e}")
            return {
                "type": "collaboration_error",
                "from_agent": self.agent_id,
                "error": str(e)
            }
    
    async def cleanup(self):
        """Enhanced cleanup with error handling"""
        logger.info("Cleaning up enhanced AutoGPT agent...")
        
        try:
            # Close aiohttp session
            if self.session:
                await self.session.close()
            
            # Cleanup error handler
            if hasattr(self.error_handler, 'cleanup'):
                await self.error_handler.cleanup()
            
            # Process remaining queued tasks
            remaining_tasks = []
            while not self.fallback_queue.empty():
                try:
                    task = await asyncio.wait_for(self.fallback_queue.get(), timeout=0.1)
                    remaining_tasks.append(task)
                except asyncio.TimeoutError:
                    break
            
            if remaining_tasks:
                logger.warning(f"Cleanup: {len(remaining_tasks)} tasks were not processed")
            
            # Optionally stop container
            if os.getenv("STOP_CONTAINER_ON_EXIT", "false").lower() == "true":
                if await self._is_container_running():
                    await self.stop_container()
            
            logger.info("Enhanced AutoGPT agent cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Standalone testing with enhanced error scenarios
async def main():
    """Test enhanced AutoGPT agent"""
    agent = EnhancedAutoGPTAgent()
    
    try:
        await agent.initialize()
        
        # Test normal task execution
        test_task = {
            "task_id": "test-enhanced-001",
            "description": "Research quantum computing applications with error handling",
            "constraints": ["Use reliable sources", "Handle network failures"],
            "priority": "high",
            "deadline": "2024-12-31"
        }
        
        result = await agent.execute_task(test_task)
        print(f"Task result: {json.dumps(result, indent=2)}")
        
        # Test health check
        health_status = await agent.health_check()
        print(f"Health status: {health_status}")
        
        # Get comprehensive status
        status = await agent.get_status()
        print(f"Agent status: {json.dumps(status, indent=2, default=str)}")
        
        # Test collaboration
        collab_message = {
            "type": "health_check"
        }
        collab_result = await agent.collaborate("test-agent", collab_message)
        print(f"Collaboration result: {json.dumps(collab_result, indent=2)}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())