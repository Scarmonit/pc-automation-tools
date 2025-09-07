#!/usr/bin/env python3
"""
Enhanced Swarm API Bridge with Comprehensive Error Handling and Failover
Provides robust REST API and WebSocket endpoints with failover capabilities
"""

import asyncio
import json
import logging
import os
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from aiohttp import web, WSMsgType, ClientSession, ClientTimeout, ClientError
import aiohttp
import weakref
from dataclasses import dataclass
from enum import Enum
import ssl

# Import our error handling system
from error_handling import (
    ErrorHandler, CircuitBreaker, RetryStrategy, RequestValidator,
    RateLimiter, SwarmLogger, GracefulDegradation, SwarmError
)
from health_monitor import HealthMonitor

# Configure enhanced logging
logger = SwarmLogger("api_bridge").get_logger()

class BridgeStatus(Enum):
    """API Bridge status states"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    DEGRADED = "degraded"
    FAILING = "failing"
    RECOVERING = "recovering"
    STOPPED = "stopped"

class ConnectionMode(Enum):
    """Connection mode for failover"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    FALLBACK = "fallback"
    EMERGENCY = "emergency"

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    url: str
    name: str
    priority: int = 1
    timeout: float = 30.0
    max_retries: int = 3
    circuit_breaker_threshold: int = 5
    health_check_interval: int = 30
    is_healthy: bool = True
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0

@dataclass
class TaskMetrics:
    """Task execution metrics"""
    task_id: str
    received_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "queued"
    execution_time: float = 0.0
    retry_count: int = 0
    endpoint_used: Optional[str] = None
    error_message: Optional[str] = None

class EnhancedSwarmAPIBridge:
    """
    Enhanced API Bridge with Failover and Comprehensive Error Handling
    Provides robust communication between AutoGPT and Swarm Intelligence
    """
    
    def __init__(self, port: int = 8002):
        """Initialize the enhanced API bridge"""
        self.port = port
        self.app = web.Application()
        self.bridge_id = f"bridge-enhanced-{int(time.time())}"
        self.status = BridgeStatus.INITIALIZING
        
        # Initialize error handling components
        self.error_handler = ErrorHandler()
        self.health_monitor = HealthMonitor()
        
        # Service endpoints with failover
        self.autogpt_endpoints = self._initialize_autogpt_endpoints()
        self.swarm_endpoints = self._initialize_swarm_endpoints()
        
        # Circuit breakers for each service
        self.autogpt_circuit_breakers = {
            endpoint.name: CircuitBreaker(
                name=f"autogpt_{endpoint.name}",
                failure_threshold=endpoint.circuit_breaker_threshold,
                recovery_timeout=60.0,
                expected_exception=ClientError
            )
            for endpoint in self.autogpt_endpoints
        }
        
        self.swarm_circuit_breakers = {
            endpoint.name: CircuitBreaker(
                name=f"swarm_{endpoint.name}",
                failure_threshold=endpoint.circuit_breaker_threshold,
                recovery_timeout=60.0,
                expected_exception=ClientError
            )
            for endpoint in self.swarm_endpoints
        }
        
        # Retry strategies
        self.api_retry_strategy = RetryStrategy(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
            exponential_base=2.0
        )
        
        # Rate limiters
        self.global_rate_limiter = RateLimiter(max_calls=1000, time_window=60.0)
        self.per_endpoint_rate_limiters = {
            endpoint.name: RateLimiter(max_calls=200, time_window=60.0)
            for endpoint in self.autogpt_endpoints + self.swarm_endpoints
        }
        
        # Request validator
        self.request_validator = RequestValidator()
        
        # Graceful degradation
        self.degradation_manager = GracefulDegradation()
        
        # Connection management
        self.websockets = weakref.WeakSet()
        self.active_tasks: Dict[str, TaskMetrics] = {}
        self.task_queue = asyncio.PriorityQueue()  # Priority queue for task handling
        self.session_pool: Dict[str, ClientSession] = {}
        self.connection_mode = ConnectionMode.PRIMARY
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        
        # Enhanced metrics
        self.metrics = {
            "tasks_received": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_retried": 0,
            "messages_relayed": 0,
            "active_connections": 0,
            "failovers_executed": 0,
            "circuit_breaker_trips": 0,
            "recovery_attempts": 0,
            "start_time": datetime.now().isoformat(),
            "endpoints_healthy": 0,
            "endpoints_total": len(self.autogpt_endpoints) + len(self.swarm_endpoints)
        }
        
        # Load balancing
        self.last_autogpt_endpoint = 0
        self.endpoint_weights = {}  # Performance-based weights
        
        # Setup routes
        self.setup_routes()
    
    def _initialize_autogpt_endpoints(self) -> List[ServiceEndpoint]:
        """Initialize AutoGPT service endpoints with failover"""
        endpoints = []
        
        # Primary AutoGPT endpoint
        primary_url = os.getenv("AUTOGPT_API_URL", "http://localhost:3000")
        endpoints.append(ServiceEndpoint(
            url=primary_url,
            name="primary",
            priority=1,
            timeout=60.0,
            max_retries=3,
            circuit_breaker_threshold=5
        ))
        
        # Secondary endpoints (if configured)
        secondary_urls = os.getenv("AUTOGPT_SECONDARY_URLS", "").split(",")
        for i, url in enumerate(secondary_urls):
            if url.strip():
                endpoints.append(ServiceEndpoint(
                    url=url.strip(),
                    name=f"secondary_{i}",
                    priority=2,
                    timeout=45.0,
                    max_retries=2,
                    circuit_breaker_threshold=3
                ))
        
        # Docker Swarm endpoints (if available)
        if os.getenv("DOCKER_SWARM_MODE", "false").lower() == "true":
            swarm_services = os.getenv("AUTOGPT_SWARM_SERVICES", "").split(",")
            for i, service in enumerate(swarm_services):
                if service.strip():
                    endpoints.append(ServiceEndpoint(
                        url=f"http://{service.strip()}:3000",
                        name=f"swarm_{i}",
                        priority=3,
                        timeout=30.0,
                        max_retries=1,
                        circuit_breaker_threshold=2
                    ))
        
        # Emergency local endpoint
        if primary_url != "http://localhost:3001":
            endpoints.append(ServiceEndpoint(
                url="http://localhost:3001",
                name="emergency",
                priority=99,
                timeout=15.0,
                max_retries=1,
                circuit_breaker_threshold=1
            ))
        
        return endpoints
    
    def _initialize_swarm_endpoints(self) -> List[ServiceEndpoint]:
        """Initialize Swarm API endpoints with failover"""
        endpoints = []
        
        # Primary Swarm API endpoint
        primary_url = os.getenv("SWARM_API_ENDPOINT", "http://swarm-api:8001")
        endpoints.append(ServiceEndpoint(
            url=primary_url,
            name="primary",
            priority=1,
            timeout=30.0,
            max_retries=2,
            circuit_breaker_threshold=3
        ))
        
        # Backup Swarm endpoints
        backup_urls = os.getenv("SWARM_BACKUP_ENDPOINTS", "").split(",")
        for i, url in enumerate(backup_urls):
            if url.strip():
                endpoints.append(ServiceEndpoint(
                    url=url.strip(),
                    name=f"backup_{i}",
                    priority=2,
                    timeout=20.0,
                    max_retries=1,
                    circuit_breaker_threshold=2
                ))
        
        return endpoints
    
    def setup_routes(self):
        """Setup enhanced API routes"""
        # Health and status
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/status', self.get_status)
        self.app.router.add_get('/metrics', self.get_metrics)
        self.app.router.add_get('/endpoints', self.get_endpoints_status)
        
        # Task management
        self.app.router.add_post('/tasks', self.receive_task)
        self.app.router.add_get('/tasks/{task_id}', self.get_task_status)
        self.app.router.add_delete('/tasks/{task_id}', self.cancel_task)
        self.app.router.add_get('/tasks', self.list_tasks)
        self.app.router.add_post('/tasks/{task_id}/retry', self.retry_task)
        
        # Collaboration
        self.app.router.add_post('/collaborate', self.handle_collaboration)
        self.app.router.add_post('/memory/store', self.store_memory)
        self.app.router.add_get('/memory/retrieve', self.retrieve_memory)
        
        # WebSocket for real-time updates
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # AutoGPT specific endpoints with failover
        self.app.router.add_post('/autogpt/configure', self.configure_autogpt)
        self.app.router.add_get('/autogpt/status', self.get_autogpt_status)
        self.app.router.add_post('/autogpt/execute', self.execute_autogpt_task)
        
        # Administrative endpoints
        self.app.router.add_post('/admin/failover', self.force_failover)
        self.app.router.add_post('/admin/recovery', self.force_recovery)
        self.app.router.add_get('/admin/circuit-breakers', self.get_circuit_breaker_status)
        self.app.router.add_post('/admin/reset-circuit-breaker', self.reset_circuit_breaker)
    
    async def initialize(self):
        """Initialize the enhanced API bridge"""
        logger.info("Initializing enhanced API bridge...")
        
        try:
            # Initialize error handler
            await self.error_handler.initialize()
            
            # Create session pool
            await self._create_session_pool()
            
            # Start health monitoring for all endpoints
            await self._start_endpoint_monitoring()
            
            # Initialize endpoint weights
            self._initialize_endpoint_weights()
            
            self.status = BridgeStatus.RUNNING
            logger.info(f"Enhanced API bridge {self.bridge_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize API bridge: {e}")
            self.status = BridgeStatus.FAILING
            raise
    
    async def _create_session_pool(self):
        """Create HTTP session pool for different endpoints"""
        # Create SSL context for secure connections
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            ttl_dns_cache=300,
            use_dns_cache=True,
            ssl=ssl_context
        )
        
        timeout = ClientTimeout(total=60, connect=10)
        
        # Create sessions for AutoGPT endpoints
        for endpoint in self.autogpt_endpoints:
            self.session_pool[f"autogpt_{endpoint.name}"] = ClientSession(
                connector=connector,
                timeout=ClientTimeout(total=endpoint.timeout, connect=10),
                headers={"User-Agent": f"SwarmBridge/{self.bridge_id}"}
            )
        
        # Create sessions for Swarm endpoints
        for endpoint in self.swarm_endpoints:
            self.session_pool[f"swarm_{endpoint.name}"] = ClientSession(
                connector=connector,
                timeout=ClientTimeout(total=endpoint.timeout, connect=5),
                headers={"User-Agent": f"SwarmBridge/{self.bridge_id}"}
            )
    
    async def _start_endpoint_monitoring(self):
        """Start background monitoring of all endpoints"""
        # Monitor AutoGPT endpoints
        for endpoint in self.autogpt_endpoints:
            task = asyncio.create_task(
                self._monitor_endpoint(endpoint, "autogpt")
            )
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
        
        # Monitor Swarm endpoints
        for endpoint in self.swarm_endpoints:
            task = asyncio.create_task(
                self._monitor_endpoint(endpoint, "swarm")
            )
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
        
        # Start overall health monitoring
        task = asyncio.create_task(self._overall_health_monitor())
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
    
    async def _monitor_endpoint(self, endpoint: ServiceEndpoint, service_type: str):
        """Monitor individual endpoint health"""
        while True:
            try:
                await asyncio.sleep(endpoint.health_check_interval)
                
                # Perform health check
                session_key = f"{service_type}_{endpoint.name}"
                session = self.session_pool.get(session_key)
                
                if not session:
                    continue
                
                health_url = f"{endpoint.url}/health"
                
                try:
                    async with session.get(health_url) as response:
                        if response.status == 200:
                            # Endpoint is healthy
                            if not endpoint.is_healthy:
                                logger.info(f"Endpoint {endpoint.name} recovered")
                                endpoint.is_healthy = True
                                endpoint.consecutive_failures = 0
                                self.metrics["recovery_attempts"] += 1
                        else:
                            endpoint.consecutive_failures += 1
                            if endpoint.consecutive_failures >= 3:
                                endpoint.is_healthy = False
                
                except Exception as e:
                    endpoint.consecutive_failures += 1
                    if endpoint.consecutive_failures >= 3:
                        if endpoint.is_healthy:
                            logger.warning(f"Endpoint {endpoint.name} marked unhealthy: {e}")
                        endpoint.is_healthy = False
                
                endpoint.last_health_check = datetime.now()
                
            except Exception as e:
                logger.error(f"Error monitoring endpoint {endpoint.name}: {e}")
    
    async def _overall_health_monitor(self):
        """Monitor overall system health and trigger failovers"""
        while True:
            try:
                await asyncio.sleep(30)
                
                # Count healthy endpoints
                healthy_autogpt = sum(1 for ep in self.autogpt_endpoints if ep.is_healthy)
                healthy_swarm = sum(1 for ep in self.swarm_endpoints if ep.is_healthy)
                
                total_healthy = healthy_autogpt + healthy_swarm
                self.metrics["endpoints_healthy"] = total_healthy
                
                # Determine system status
                if total_healthy == 0:
                    if self.status != BridgeStatus.FAILING:
                        logger.error("All endpoints unhealthy, entering failing mode")
                        self.status = BridgeStatus.FAILING
                        await self.degradation_manager.trigger_degradation("all_endpoints_failed")
                        
                elif total_healthy < self.metrics["endpoints_total"] * 0.5:
                    if self.status != BridgeStatus.DEGRADED:
                        logger.warning("System degraded, less than 50% endpoints healthy")
                        self.status = BridgeStatus.DEGRADED
                        await self._trigger_failover()
                        
                else:
                    if self.status in [BridgeStatus.DEGRADED, BridgeStatus.FAILING]:
                        logger.info("System health restored")
                        self.status = BridgeStatus.RUNNING
                        self.connection_mode = ConnectionMode.PRIMARY
                
            except Exception as e:
                logger.error(f"Error in overall health monitor: {e}")
    
    def _initialize_endpoint_weights(self):
        """Initialize performance-based endpoint weights"""
        for endpoint in self.autogpt_endpoints + self.swarm_endpoints:
            self.endpoint_weights[endpoint.name] = {
                "weight": 1.0,
                "response_time": 0.0,
                "success_rate": 1.0,
                "requests": 0
            }
    
    def _select_best_endpoint(self, endpoints: List[ServiceEndpoint], service_type: str) -> Optional[ServiceEndpoint]:
        """Select the best available endpoint based on health and performance"""
        # Filter healthy endpoints
        healthy_endpoints = [ep for ep in endpoints if ep.is_healthy]
        
        if not healthy_endpoints:
            # No healthy endpoints, try primary anyway as fallback
            primary_endpoints = [ep for ep in endpoints if ep.priority == 1]
            if primary_endpoints:
                logger.warning(f"No healthy {service_type} endpoints, using primary as fallback")
                return primary_endpoints[0]
            return None
        
        # Sort by priority first, then by performance weight
        healthy_endpoints.sort(key=lambda ep: (
            ep.priority,
            -self.endpoint_weights.get(ep.name, {}).get("weight", 0)
        ))
        
        # Round-robin among endpoints with same priority
        same_priority = [ep for ep in healthy_endpoints if ep.priority == healthy_endpoints[0].priority]
        
        if len(same_priority) == 1:
            return same_priority[0]
        
        # Use weighted selection for load balancing
        total_weight = sum(
            self.endpoint_weights.get(ep.name, {}).get("weight", 1.0)
            for ep in same_priority
        )
        
        if total_weight <= 0:
            return same_priority[0]
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for endpoint in same_priority:
            cumulative += self.endpoint_weights.get(endpoint.name, {}).get("weight", 1.0)
            if cumulative >= r:
                return endpoint
        
        return same_priority[0]
    
    def _update_endpoint_performance(self, endpoint_name: str, response_time: float, success: bool):
        """Update endpoint performance metrics"""
        if endpoint_name not in self.endpoint_weights:
            return
        
        weight_info = self.endpoint_weights[endpoint_name]
        weight_info["requests"] += 1
        
        # Update response time (exponential moving average)
        alpha = 0.3
        weight_info["response_time"] = (
            alpha * response_time + (1 - alpha) * weight_info["response_time"]
        )
        
        # Update success rate (exponential moving average)
        success_value = 1.0 if success else 0.0
        weight_info["success_rate"] = (
            alpha * success_value + (1 - alpha) * weight_info["success_rate"]
        )
        
        # Calculate composite weight (inverse of response time * success rate)
        if weight_info["response_time"] > 0:
            weight_info["weight"] = (
                weight_info["success_rate"] / weight_info["response_time"]
            ) * 1000  # Scale for better distribution
        else:
            weight_info["weight"] = weight_info["success_rate"]
    
    async def _make_request_with_failover(
        self,
        endpoints: List[ServiceEndpoint],
        service_type: str,
        path: str,
        method: str = "GET",
        data: Any = None,
        **kwargs
    ) -> Tuple[Any, str]:
        """Make HTTP request with automatic failover"""
        last_exception = None
        attempted_endpoints = []
        
        for attempt in range(len(endpoints)):
            endpoint = self._select_best_endpoint(
                [ep for ep in endpoints if ep.name not in attempted_endpoints],
                service_type
            )
            
            if not endpoint:
                break
            
            attempted_endpoints.append(endpoint.name)
            session_key = f"{service_type}_{endpoint.name}"
            session = self.session_pool.get(session_key)
            
            if not session:
                continue
            
            # Apply rate limiting
            rate_limiter = self.per_endpoint_rate_limiters.get(endpoint.name)
            if rate_limiter:
                await rate_limiter.acquire()
            
            # Get circuit breaker
            circuit_breakers = (
                self.autogpt_circuit_breakers if service_type == "autogpt"
                else self.swarm_circuit_breakers
            )
            circuit_breaker = circuit_breakers.get(endpoint.name)
            
            try:
                start_time = time.time()
                
                async def _make_request():
                    url = f"{endpoint.url}{path}"
                    if method == "GET":
                        async with session.get(url, **kwargs) as response:
                            result = await response.json() if response.content_type == 'application/json' else await response.text()
                            return result, response.status
                    elif method == "POST":
                        async with session.post(url, json=data, **kwargs) as response:
                            result = await response.json() if response.content_type == 'application/json' else await response.text()
                            return result, response.status
                    elif method == "DELETE":
                        async with session.delete(url, **kwargs) as response:
                            result = await response.json() if response.content_type == 'application/json' else await response.text()
                            return result, response.status
                
                # Use circuit breaker if available
                if circuit_breaker:
                    result, status_code = await circuit_breaker.call(_make_request)
                else:
                    result, status_code = await _make_request()
                
                response_time = time.time() - start_time
                
                # Update performance metrics
                self._update_endpoint_performance(endpoint.name, response_time, status_code < 400)
                
                if status_code < 400:
                    return result, endpoint.name
                else:
                    logger.warning(f"Request to {endpoint.name} failed with status {status_code}")
                    last_exception = Exception(f"HTTP {status_code}")
                    
            except Exception as e:
                response_time = time.time() - start_time
                self._update_endpoint_performance(endpoint.name, response_time, False)
                
                logger.warning(f"Request to {endpoint.name} failed: {e}")
                last_exception = e
                
                # Mark endpoint as potentially unhealthy
                endpoint.consecutive_failures += 1
                if endpoint.consecutive_failures >= endpoint.circuit_breaker_threshold:
                    endpoint.is_healthy = False
                    if circuit_breaker:
                        self.metrics["circuit_breaker_trips"] += 1
        
        # All endpoints failed
        if last_exception:
            raise last_exception
        else:
            raise Exception("No available endpoints")
    
    async def _trigger_failover(self):
        """Trigger failover to secondary endpoints"""
        logger.info("Triggering failover to secondary endpoints")
        
        self.metrics["failovers_executed"] += 1
        
        # Switch to secondary connection mode
        if self.connection_mode == ConnectionMode.PRIMARY:
            self.connection_mode = ConnectionMode.SECONDARY
        elif self.connection_mode == ConnectionMode.SECONDARY:
            self.connection_mode = ConnectionMode.FALLBACK
        else:
            self.connection_mode = ConnectionMode.EMERGENCY
        
        # Broadcast failover event
        await self.broadcast_update({
            "type": "failover_triggered",
            "connection_mode": self.connection_mode.value,
            "bridge_status": self.status.value
        })
    
    async def health_check(self, request):
        """Enhanced health check endpoint"""
        try:
            # Check global rate limiter
            await self.global_rate_limiter.acquire()
            
            # Get health status of all endpoints
            autogpt_healthy = any(ep.is_healthy for ep in self.autogpt_endpoints)
            swarm_healthy = any(ep.is_healthy for ep in self.swarm_endpoints)
            
            # Overall system health
            if self.status == BridgeStatus.RUNNING and autogpt_healthy and swarm_healthy:
                status = "healthy"
            elif self.status == BridgeStatus.DEGRADED or (autogpt_healthy or swarm_healthy):
                status = "degraded"
            else:
                status = "unhealthy"
            
            return web.json_response({
                "status": status,
                "bridge_id": self.bridge_id,
                "bridge_status": self.status.value,
                "connection_mode": self.connection_mode.value,
                "autogpt": {
                    "healthy_endpoints": sum(1 for ep in self.autogpt_endpoints if ep.is_healthy),
                    "total_endpoints": len(self.autogpt_endpoints),
                    "status": "healthy" if autogpt_healthy else "unhealthy"
                },
                "swarm": {
                    "healthy_endpoints": sum(1 for ep in self.swarm_endpoints if ep.is_healthy),
                    "total_endpoints": len(self.swarm_endpoints),
                    "status": "healthy" if swarm_healthy else "unhealthy"
                },
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - datetime.fromisoformat(self.metrics["start_time"])).total_seconds()
            })
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return web.json_response(
                {"error": str(e), "status": "error"},
                status=500
            )
    
    async def get_endpoints_status(self, request):
        """Get detailed status of all endpoints"""
        try:
            endpoints_status = {
                "autogpt": [
                    {
                        "name": ep.name,
                        "url": ep.url,
                        "priority": ep.priority,
                        "is_healthy": ep.is_healthy,
                        "consecutive_failures": ep.consecutive_failures,
                        "last_health_check": ep.last_health_check.isoformat() if ep.last_health_check else None,
                        "performance": self.endpoint_weights.get(ep.name, {}),
                        "circuit_breaker_state": self.autogpt_circuit_breakers.get(ep.name, {}).state.name if self.autogpt_circuit_breakers.get(ep.name) else "UNKNOWN"
                    }
                    for ep in self.autogpt_endpoints
                ],
                "swarm": [
                    {
                        "name": ep.name,
                        "url": ep.url,
                        "priority": ep.priority,
                        "is_healthy": ep.is_healthy,
                        "consecutive_failures": ep.consecutive_failures,
                        "last_health_check": ep.last_health_check.isoformat() if ep.last_health_check else None,
                        "performance": self.endpoint_weights.get(ep.name, {}),
                        "circuit_breaker_state": self.swarm_circuit_breakers.get(ep.name, {}).state.name if self.swarm_circuit_breakers.get(ep.name) else "UNKNOWN"
                    }
                    for ep in self.swarm_endpoints
                ]
            }
            
            return web.json_response(endpoints_status)
            
        except Exception as e:
            logger.error(f"Error getting endpoints status: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def receive_task(self, request):
        """Receive task with enhanced error handling and validation"""
        try:
            # Apply global rate limiting
            await self.global_rate_limiter.acquire()
            
            # Validate request
            data = await request.json()
            await self.request_validator.validate_request({
                "data": data,
                "type": "dict"
            })
            
            task_id = data.get("task_id", f"task-{int(time.time())}-{random.randint(1000, 9999)}")
            priority = data.get("priority", "medium")
            
            # Convert priority to numeric value for queue
            priority_map = {"critical": 1, "high": 2, "medium": 3, "low": 4}
            priority_value = priority_map.get(priority, 3)
            
            self.metrics["tasks_received"] += 1
            
            # Create task metrics
            task_metrics = TaskMetrics(
                task_id=task_id,
                received_at=datetime.now(),
                status="queued"
            )
            self.active_tasks[task_id] = task_metrics
            
            # Queue with priority
            await self.task_queue.put((priority_value, time.time(), task_id, data))
            
            # Broadcast update
            await self.broadcast_update({
                "type": "task_received",
                "task_id": task_id,
                "status": "queued",
                "priority": priority
            })
            
            return web.json_response({
                "task_id": task_id,
                "status": "queued",
                "priority": priority,
                "position": self.task_queue.qsize(),
                "bridge_status": self.status.value
            })
            
        except Exception as e:
            logger.error(f"Error receiving task: {e}")
            return web.json_response(
                {"error": str(e)},
                status=400
            )
    
    async def retry_task(self, request):
        """Retry a failed task"""
        try:
            task_id = request.match_info['task_id']
            
            if task_id not in self.active_tasks:
                return web.json_response(
                    {"error": "Task not found"},
                    status=404
                )
            
            task_metrics = self.active_tasks[task_id]
            
            if task_metrics.status not in ["failed", "error", "timeout"]:
                return web.json_response(
                    {"error": "Task is not in a retryable state"},
                    status=400
                )
            
            # Reset task metrics
            task_metrics.status = "queued"
            task_metrics.retry_count += 1
            task_metrics.started_at = None
            task_metrics.completed_at = None
            task_metrics.execution_time = 0.0
            task_metrics.error_message = None
            
            # Re-queue with high priority
            data = await request.json() if request.content_type == 'application/json' else {}
            await self.task_queue.put((1, time.time(), task_id, data))
            
            self.metrics["tasks_retried"] += 1
            
            # Broadcast update
            await self.broadcast_update({
                "type": "task_retried",
                "task_id": task_id,
                "retry_count": task_metrics.retry_count
            })
            
            return web.json_response({
                "task_id": task_id,
                "status": "queued",
                "retry_count": task_metrics.retry_count
            })
            
        except Exception as e:
            logger.error(f"Error retrying task: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def execute_autogpt_task(self, request):
        """Execute task on AutoGPT with failover"""
        try:
            data = await request.json()
            
            # Execute with failover
            result, endpoint_used = await self._make_request_with_failover(
                self.autogpt_endpoints,
                "autogpt",
                "/api/tasks",
                method="POST",
                data=data,
                timeout=ClientTimeout(total=3600)
            )
            
            self.metrics["tasks_completed"] += 1
            
            return web.json_response({
                "result": result,
                "endpoint_used": endpoint_used,
                "bridge_status": self.status.value
            })
            
        except Exception as e:
            logger.error(f"AutoGPT execution error: {e}")
            self.metrics["tasks_failed"] += 1
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def get_autogpt_status(self, request):
        """Get AutoGPT status with failover"""
        try:
            result, endpoint_used = await self._make_request_with_failover(
                self.autogpt_endpoints,
                "autogpt",
                "/api/status",
                method="GET"
            )
            
            return web.json_response({
                "result": result,
                "endpoint_used": endpoint_used
            })
            
        except Exception as e:
            logger.error(f"AutoGPT status error: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def get_metrics(self, request):
        """Get comprehensive bridge metrics"""
        try:
            uptime = (datetime.now() - datetime.fromisoformat(self.metrics["start_time"])).total_seconds()
            
            # Calculate success rate
            total_tasks = self.metrics["tasks_received"]
            success_rate = (
                (self.metrics["tasks_completed"] / total_tasks * 100) if total_tasks > 0 else 0
            )
            
            # Calculate average task time
            completed_tasks = [
                task for task in self.active_tasks.values()
                if task.status == "completed" and task.execution_time > 0
            ]
            avg_task_time = (
                sum(task.execution_time for task in completed_tasks) / len(completed_tasks)
                if completed_tasks else 0.0
            )
            
            return web.json_response({
                "bridge_id": self.bridge_id,
                "bridge_status": self.status.value,
                "connection_mode": self.connection_mode.value,
                "uptime_seconds": uptime,
                "tasks": {
                    "received": self.metrics["tasks_received"],
                    "completed": self.metrics["tasks_completed"],
                    "failed": self.metrics["tasks_failed"],
                    "retried": self.metrics["tasks_retried"],
                    "active": len([t for t in self.active_tasks.values() if t.status in ["processing", "queued"]]),
                    "queued": self.task_queue.qsize()
                },
                "messages_relayed": self.metrics["messages_relayed"],
                "connections": {
                    "websockets": len(self.websockets),
                    "active": self.metrics["active_connections"]
                },
                "performance": {
                    "success_rate": success_rate,
                    "avg_task_time": avg_task_time,
                    "failovers_executed": self.metrics["failovers_executed"],
                    "circuit_breaker_trips": self.metrics["circuit_breaker_trips"],
                    "recovery_attempts": self.metrics["recovery_attempts"]
                },
                "endpoints": {
                    "healthy": self.metrics["endpoints_healthy"],
                    "total": self.metrics["endpoints_total"]
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def websocket_handler(self, request):
        """Enhanced WebSocket handler with error recovery"""
        ws = web.WebSocketResponse(heartbeat=30)
        await ws.prepare(request)
        
        self.websockets.add(ws)
        self.metrics["active_connections"] += 1
        
        try:
            # Send initial connection message
            await ws.send_json({
                "type": "connected",
                "bridge_id": self.bridge_id,
                "bridge_status": self.status.value,
                "connection_mode": self.connection_mode.value,
                "timestamp": datetime.now().isoformat()
            })
            
            # Handle incoming messages
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self.handle_websocket_message(ws, data)
                    except Exception as e:
                        await ws.send_json({
                            "type": "error",
                            "error": str(e)
                        })
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        
        finally:
            self.websockets.discard(ws)
            self.metrics["active_connections"] -= 1
        
        return ws
    
    async def handle_websocket_message(self, ws, data):
        """Handle WebSocket message with enhanced features"""
        msg_type = data.get("type")
        
        if msg_type == "ping":
            await ws.send_json({
                "type": "pong",
                "timestamp": datetime.now().isoformat(),
                "bridge_status": self.status.value
            })
        
        elif msg_type == "get_status":
            status = {
                "bridge_id": self.bridge_id,
                "bridge_status": self.status.value,
                "connection_mode": self.connection_mode.value,
                "healthy_endpoints": self.metrics["endpoints_healthy"],
                "total_endpoints": self.metrics["endpoints_total"],
                "active_tasks": len(self.active_tasks),
                "timestamp": datetime.now().isoformat()
            }
            await ws.send_json({"type": "status", "data": status})
        
        elif msg_type == "subscribe":
            # Enhanced subscription handling
            subscription_type = data.get("subscription_type", "all")
            await ws.send_json({
                "type": "subscribed",
                "subscription_type": subscription_type,
                "bridge_id": self.bridge_id
            })
    
    async def broadcast_update(self, update: Dict[str, Any]):
        """Broadcast update to all WebSocket clients with error handling"""
        if not self.websockets:
            return
        
        update["timestamp"] = datetime.now().isoformat()
        update["bridge_id"] = self.bridge_id
        
        # Send to all connected clients
        tasks = []
        for ws in self.websockets.copy():  # Copy to avoid modification during iteration
            try:
                tasks.append(ws.send_json(update))
            except Exception as e:
                logger.debug(f"Failed to send to WebSocket client: {e}")
                # Remove broken connection
                self.websockets.discard(ws)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    # Administrative endpoints
    async def force_failover(self, request):
        """Force failover to next tier endpoints"""
        try:
            await self._trigger_failover()
            return web.json_response({
                "message": "Failover triggered",
                "new_mode": self.connection_mode.value,
                "bridge_status": self.status.value
            })
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def force_recovery(self, request):
        """Force recovery attempt"""
        try:
            self.status = BridgeStatus.RECOVERING
            
            # Reset all endpoint failure counts
            for endpoint in self.autogpt_endpoints + self.swarm_endpoints:
                endpoint.consecutive_failures = 0
                endpoint.is_healthy = True
            
            # Reset circuit breakers
            for cb in list(self.autogpt_circuit_breakers.values()) + list(self.swarm_circuit_breakers.values()):
                if hasattr(cb, 'reset'):
                    cb.reset()
            
            self.connection_mode = ConnectionMode.PRIMARY
            self.status = BridgeStatus.RUNNING
            
            return web.json_response({
                "message": "Recovery completed",
                "bridge_status": self.status.value,
                "connection_mode": self.connection_mode.value
            })
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_circuit_breaker_status(self, request):
        """Get circuit breaker status"""
        try:
            status = {
                "autogpt": {
                    name: {
                        "state": cb.state.name,
                        "failure_count": cb.failure_count,
                        "last_failure": cb.last_failure_time.isoformat() if cb.last_failure_time else None
                    }
                    for name, cb in self.autogpt_circuit_breakers.items()
                },
                "swarm": {
                    name: {
                        "state": cb.state.name,
                        "failure_count": cb.failure_count,
                        "last_failure": cb.last_failure_time.isoformat() if cb.last_failure_time else None
                    }
                    for name, cb in self.swarm_circuit_breakers.items()
                }
            }
            return web.json_response(status)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def start(self):
        """Start the enhanced API bridge"""
        await self.initialize()
        
        # Start background task processor
        processor_task = asyncio.create_task(self.task_processor())
        self.background_tasks.add(processor_task)
        processor_task.add_done_callback(self.background_tasks.discard)
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        logger.info(f"Enhanced Swarm API Bridge running on port {self.port}")
        logger.info(f"WebSocket endpoint: ws://localhost:{self.port}/ws")
        logger.info(f"Bridge ID: {self.bridge_id}")
        logger.info(f"AutoGPT endpoints: {len(self.autogpt_endpoints)}")
        logger.info(f"Swarm endpoints: {len(self.swarm_endpoints)}")
        logger.info(f"Status: {self.status.value}")
    
    async def stop(self):
        """Stop the enhanced API bridge"""
        logger.info("Stopping enhanced API bridge...")
        
        # Cancel all background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close all sessions
        for session in self.session_pool.values():
            await session.close()
        
        # Close all WebSocket connections
        for ws in self.websockets.copy():
            await ws.close()
        
        # Cleanup error handler
        if hasattr(self.error_handler, 'cleanup'):
            await self.error_handler.cleanup()
        
        logger.info("Enhanced API bridge stopped")
    
    async def task_processor(self):
        """Enhanced background task processor with failover"""
        while True:
            try:
                # Get task from priority queue
                priority, timestamp, task_id, data = await self.task_queue.get()
                
                if task_id in self.active_tasks:
                    task_metrics = self.active_tasks[task_id]
                    
                    # Update task status
                    task_metrics.status = "processing"
                    task_metrics.started_at = datetime.now()
                    
                    # Broadcast update
                    await self.broadcast_update({
                        "type": "task_started",
                        "task_id": task_id,
                        "priority": priority
                    })
                    
                    try:
                        # Process task with failover
                        result, endpoint_used = await self._make_request_with_failover(
                            self.autogpt_endpoints,
                            "autogpt",
                            "/api/tasks",
                            method="POST",
                            data=data,
                            timeout=ClientTimeout(total=3600)
                        )
                        
                        # Update task metrics
                        task_metrics.status = "completed"
                        task_metrics.completed_at = datetime.now()
                        task_metrics.execution_time = (
                            task_metrics.completed_at - task_metrics.started_at
                        ).total_seconds()
                        task_metrics.endpoint_used = endpoint_used
                        
                        self.metrics["tasks_completed"] += 1
                        
                        # Broadcast completion
                        await self.broadcast_update({
                            "type": "task_completed",
                            "task_id": task_id,
                            "status": "completed",
                            "execution_time": task_metrics.execution_time,
                            "endpoint_used": endpoint_used
                        })
                        
                    except Exception as e:
                        # Task failed
                        task_metrics.status = "failed"
                        task_metrics.completed_at = datetime.now()
                        task_metrics.error_message = str(e)
                        
                        self.metrics["tasks_failed"] += 1
                        
                        logger.error(f"Task {task_id} failed: {e}")
                        
                        # Broadcast failure
                        await self.broadcast_update({
                            "type": "task_failed",
                            "task_id": task_id,
                            "error": str(e)
                        })
            
            except Exception as e:
                logger.error(f"Task processor error: {e}")
                await asyncio.sleep(1)

# Enhanced standalone testing
async def main():
    """Test enhanced API bridge"""
    bridge = EnhancedSwarmAPIBridge(port=8003)  # Use different port for testing
    
    try:
        await bridge.start()
        logger.info("Enhanced API bridge started successfully")
        
        # Keep running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("Shutting down enhanced API bridge...")
    except Exception as e:
        logger.error(f"Bridge error: {e}")
    finally:
        await bridge.stop()

if __name__ == "__main__":
    asyncio.run(main())