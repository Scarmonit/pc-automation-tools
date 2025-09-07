#!/usr/bin/env python3
"""
Docker Health Checker for AutoGPT Integration
Monitors Docker containers and handles recovery
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import psutil

# Try to import docker, but handle case where it's not installed
try:
    import docker
    from docker.errors import DockerException, APIError, NotFound
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    DockerException = Exception
    APIError = Exception
    NotFound = Exception

# Import from our error handling system
try:
    from error_handling import ErrorHandler, CircuitBreaker, RetryStrategy
except ImportError:
    # Fallback if error_handling not available
    class ErrorHandler:
        pass
    class CircuitBreaker:
        pass
    class RetryStrategy:
        pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContainerStatus(Enum):
    """Container status states"""
    RUNNING = "running"
    STARTING = "starting"
    STOPPED = "stopped"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    EXITED = "exited"
    DEAD = "dead"
    UNKNOWN = "unknown"


@dataclass
class ContainerHealth:
    """Container health information"""
    name: str
    container_id: str
    status: ContainerStatus
    health_status: Optional[str]  # healthy, unhealthy, starting, none
    cpu_percent: float
    memory_mb: float
    memory_limit_mb: float
    network_rx_mb: float
    network_tx_mb: float
    restart_count: int
    uptime_seconds: int
    error_message: Optional[str]
    last_check: datetime
    
    def is_healthy(self) -> bool:
        """Check if container is healthy"""
        return (self.status == ContainerStatus.RUNNING and 
                self.health_status in ['healthy', 'none', None])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'container_id': self.container_id,
            'status': self.status.value,
            'health_status': self.health_status,
            'cpu_percent': self.cpu_percent,
            'memory_mb': self.memory_mb,
            'memory_limit_mb': self.memory_limit_mb,
            'memory_usage_percent': (self.memory_mb / self.memory_limit_mb * 100) if self.memory_limit_mb > 0 else 0,
            'network_rx_mb': self.network_rx_mb,
            'network_tx_mb': self.network_tx_mb,
            'restart_count': self.restart_count,
            'uptime_seconds': self.uptime_seconds,
            'is_healthy': self.is_healthy(),
            'error_message': self.error_message,
            'last_check': self.last_check.isoformat()
        }


class DockerHealthChecker:
    """Monitor and manage Docker container health"""
    
    def __init__(self, 
                 containers_to_monitor: Optional[List[str]] = None,
                 check_interval: int = 30):
        """
        Initialize Docker health checker
        
        Args:
            containers_to_monitor: List of container names to monitor
            check_interval: Seconds between health checks
        """
        self.containers_to_monitor = containers_to_monitor or [
            'swarm-autogpt',
            'swarm-api',
            'swarm-queen',
            'swarm-redis'
        ]
        self.check_interval = check_interval
        self.docker_client = None
        self.is_docker_available = DOCKER_AVAILABLE
        self.container_health_history = {}
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
        self.monitoring_active = False
        
        # Circuit breaker for Docker operations
        self.docker_circuit_breaker = CircuitBreaker(
            name="docker_health",
            failure_threshold=5,
            timeout=60
        ) if CircuitBreaker else None
        
        # Initialize Docker client if available
        if self.is_docker_available:
            try:
                self.docker_client = docker.from_env()
                self._test_docker_connection()
            except Exception as e:
                logger.error(f"Failed to initialize Docker client: {e}")
                self.is_docker_available = False
    
    def _test_docker_connection(self) -> bool:
        """Test Docker connection"""
        try:
            self.docker_client.ping()
            return True
        except Exception as e:
            logger.error(f"Docker connection test failed: {e}")
            return False
    
    async def check_docker_availability(self) -> Tuple[bool, str]:
        """Check if Docker is available and running"""
        issues = []
        
        # Check if Docker module is installed
        if not DOCKER_AVAILABLE:
            issues.append("Docker Python module not installed (pip install docker)")
        
        # Check if Docker Desktop is running (Windows)
        if os.name == 'nt':
            try:
                result = subprocess.run(
                    ['docker', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    issues.append("Docker CLI not available")
            except FileNotFoundError:
                issues.append("Docker not installed")
            except subprocess.TimeoutExpired:
                issues.append("Docker CLI timeout")
            
            # Check if Docker Desktop process is running
            docker_running = any(
                'Docker Desktop' in p.name() 
                for p in psutil.process_iter(['name'])
            )
            if not docker_running:
                issues.append("Docker Desktop not running")
        
        # Test Docker daemon connection
        if self.docker_client:
            try:
                self.docker_client.ping()
            except Exception as e:
                issues.append(f"Docker daemon not responding: {str(e)}")
        else:
            issues.append("Docker client not initialized")
        
        is_available = len(issues) == 0
        message = "Docker is available" if is_available else "; ".join(issues)
        
        return is_available, message
    
    async def get_container_health(self, container_name: str) -> Optional[ContainerHealth]:
        """Get health status of a specific container"""
        if not self.docker_client:
            return None
        
        try:
            container = self.docker_client.containers.get(container_name)
            stats = container.stats(stream=False)
            
            # Parse container status
            status = ContainerStatus(container.status.lower())
            
            # Get health check status if available
            health_status = None
            if container.attrs.get('State', {}).get('Health'):
                health_status = container.attrs['State']['Health']['Status']
            
            # Calculate resource usage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0
            
            memory_usage = stats['memory_stats'].get('usage', 0) / (1024 * 1024)  # MB
            memory_limit = stats['memory_stats'].get('limit', 0) / (1024 * 1024)  # MB
            
            # Network stats
            networks = stats.get('networks', {})
            network_rx = sum(n.get('rx_bytes', 0) for n in networks.values()) / (1024 * 1024)  # MB
            network_tx = sum(n.get('tx_bytes', 0) for n in networks.values()) / (1024 * 1024)  # MB
            
            # Restart count
            restart_count = container.attrs['RestartCount']
            
            # Calculate uptime
            started_at = container.attrs['State'].get('StartedAt', '')
            if started_at:
                from dateutil import parser
                start_time = parser.parse(started_at)
                uptime = (datetime.now(start_time.tzinfo) - start_time).total_seconds()
            else:
                uptime = 0
            
            return ContainerHealth(
                name=container.name,
                container_id=container.short_id,
                status=status,
                health_status=health_status,
                cpu_percent=cpu_percent,
                memory_mb=memory_usage,
                memory_limit_mb=memory_limit,
                network_rx_mb=network_rx,
                network_tx_mb=network_tx,
                restart_count=restart_count,
                uptime_seconds=int(uptime),
                error_message=None,
                last_check=datetime.now()
            )
            
        except NotFound:
            return ContainerHealth(
                name=container_name,
                container_id="not_found",
                status=ContainerStatus.STOPPED,
                health_status="none",
                cpu_percent=0,
                memory_mb=0,
                memory_limit_mb=0,
                network_rx_mb=0,
                network_tx_mb=0,
                restart_count=0,
                uptime_seconds=0,
                error_message=f"Container {container_name} not found",
                last_check=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error checking container {container_name}: {e}")
            return ContainerHealth(
                name=container_name,
                container_id="error",
                status=ContainerStatus.UNKNOWN,
                health_status="unknown",
                cpu_percent=0,
                memory_mb=0,
                memory_limit_mb=0,
                network_rx_mb=0,
                network_tx_mb=0,
                restart_count=0,
                uptime_seconds=0,
                error_message=str(e),
                last_check=datetime.now()
            )
    
    async def check_all_containers(self) -> Dict[str, ContainerHealth]:
        """Check health of all monitored containers"""
        health_status = {}
        
        for container_name in self.containers_to_monitor:
            health = await self.get_container_health(container_name)
            if health:
                health_status[container_name] = health
                
                # Store in history
                if container_name not in self.container_health_history:
                    self.container_health_history[container_name] = []
                self.container_health_history[container_name].append(health)
                
                # Keep only last 100 entries
                if len(self.container_health_history[container_name]) > 100:
                    self.container_health_history[container_name] = \
                        self.container_health_history[container_name][-100:]
        
        return health_status
    
    async def recover_container(self, container_name: str) -> bool:
        """Attempt to recover an unhealthy container"""
        if not self.docker_client:
            logger.error("Docker client not available for recovery")
            return False
        
        # Check recovery attempts
        if container_name not in self.recovery_attempts:
            self.recovery_attempts[container_name] = 0
        
        if self.recovery_attempts[container_name] >= self.max_recovery_attempts:
            logger.error(f"Max recovery attempts reached for {container_name}")
            return False
        
        self.recovery_attempts[container_name] += 1
        
        try:
            container = self.docker_client.containers.get(container_name)
            
            # Recovery strategy based on container state
            if container.status == 'exited':
                logger.info(f"Starting stopped container {container_name}")
                container.start()
                await asyncio.sleep(5)  # Wait for startup
                
            elif container.status == 'running':
                # Check if container is unhealthy
                health = container.attrs.get('State', {}).get('Health', {})
                if health.get('Status') == 'unhealthy':
                    logger.info(f"Restarting unhealthy container {container_name}")
                    container.restart(timeout=30)
                    await asyncio.sleep(10)  # Wait for restart
                    
            elif container.status == 'paused':
                logger.info(f"Unpausing container {container_name}")
                container.unpause()
                
            elif container.status == 'dead':
                logger.info(f"Removing dead container {container_name}")
                container.remove(force=True)
                # Would need docker-compose to recreate
                return False
            
            # Verify recovery
            await asyncio.sleep(5)
            health = await self.get_container_health(container_name)
            if health and health.is_healthy():
                logger.info(f"Successfully recovered {container_name}")
                self.recovery_attempts[container_name] = 0  # Reset counter
                return True
            else:
                logger.warning(f"Recovery of {container_name} not successful")
                return False
                
        except Exception as e:
            logger.error(f"Failed to recover container {container_name}: {e}")
            return False
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        self.monitoring_active = True
        logger.info("Starting Docker health monitoring...")
        
        while self.monitoring_active:
            try:
                # Check Docker availability first
                is_available, message = await self.check_docker_availability()
                if not is_available:
                    logger.error(f"Docker not available: {message}")
                    await asyncio.sleep(self.check_interval)
                    continue
                
                # Check all containers
                health_status = await self.check_all_containers()
                
                # Log status
                for name, health in health_status.items():
                    if health.is_healthy():
                        logger.debug(f"{name}: Healthy (CPU: {health.cpu_percent:.1f}%, "
                                   f"Memory: {health.memory_mb:.1f}MB)")
                    else:
                        logger.warning(f"{name}: Unhealthy - {health.status.value} "
                                     f"({health.error_message})")
                        
                        # Attempt recovery
                        if health.status != ContainerStatus.RUNNING:
                            await self.recover_container(name)
                
                # Check for resource issues
                await self.check_resource_issues(health_status)
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def check_resource_issues(self, health_status: Dict[str, ContainerHealth]):
        """Check for resource-related issues"""
        for name, health in health_status.items():
            # Check CPU usage
            if health.cpu_percent > 80:
                logger.warning(f"{name}: High CPU usage ({health.cpu_percent:.1f}%)")
            
            # Check memory usage
            if health.memory_limit_mb > 0:
                memory_percent = (health.memory_mb / health.memory_limit_mb) * 100
                if memory_percent > 80:
                    logger.warning(f"{name}: High memory usage ({memory_percent:.1f}%)")
            
            # Check restart count
            if health.restart_count > 5:
                logger.error(f"{name}: High restart count ({health.restart_count})")
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False
        logger.info("Stopping Docker health monitoring")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of container health"""
        summary = {
            'docker_available': self.is_docker_available,
            'containers_monitored': len(self.containers_to_monitor),
            'last_check': datetime.now().isoformat(),
            'container_status': {}
        }
        
        for container_name in self.containers_to_monitor:
            if container_name in self.container_health_history:
                latest = self.container_health_history[container_name][-1]
                summary['container_status'][container_name] = {
                    'status': latest.status.value,
                    'is_healthy': latest.is_healthy(),
                    'uptime': latest.uptime_seconds,
                    'restart_count': latest.restart_count,
                    'cpu_percent': latest.cpu_percent,
                    'memory_mb': latest.memory_mb
                }
            else:
                summary['container_status'][container_name] = {
                    'status': 'not_found',
                    'is_healthy': False
                }
        
        # Overall health
        all_healthy = all(
            s.get('is_healthy', False) 
            for s in summary['container_status'].values()
        )
        summary['overall_healthy'] = all_healthy
        
        return summary
    
    async def ensure_containers_running(self, compose_file: str) -> bool:
        """Ensure all containers are running using docker-compose"""
        try:
            # Check if docker-compose file exists
            if not Path(compose_file).exists():
                logger.error(f"Docker compose file not found: {compose_file}")
                return False
            
            # Start containers
            logger.info(f"Starting containers from {compose_file}")
            result = subprocess.run(
                ['docker-compose', '-f', compose_file, 'up', '-d'],
                capture_output=True,
                text=True,
                cwd=Path(compose_file).parent
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to start containers: {result.stderr}")
                return False
            
            logger.info("Containers started successfully")
            
            # Wait for containers to be healthy
            await asyncio.sleep(10)
            
            # Check health
            health_status = await self.check_all_containers()
            all_healthy = all(h.is_healthy() for h in health_status.values())
            
            return all_healthy
            
        except FileNotFoundError:
            logger.error("docker-compose not found. Please install Docker Compose.")
            return False
        except Exception as e:
            logger.error(f"Failed to ensure containers running: {e}")
            return False
    
    def print_health_report(self):
        """Print health report to console"""
        summary = self.get_health_summary()
        
        print("\n" + "="*60)
        print("DOCKER HEALTH REPORT")
        print("="*60)
        
        if not summary['docker_available']:
            print("[ERROR] Docker is not available!")
            print("Please ensure Docker Desktop is installed and running.")
        else:
            print(f"Docker Status: Available")
            print(f"Monitored Containers: {summary['containers_monitored']}")
            print(f"Overall Health: {'[OK]' if summary['overall_healthy'] else '[ISSUES]'}")
            
            print("\nContainer Status:")
            print("-"*40)
            
            for name, status in summary['container_status'].items():
                health_indicator = "[OK]" if status['is_healthy'] else "[FAIL]"
                print(f"{health_indicator} {name}: {status['status']}")
                if status.get('uptime'):
                    uptime_hours = status['uptime'] / 3600
                    print(f"    Uptime: {uptime_hours:.1f} hours")
                if status.get('cpu_percent'):
                    print(f"    CPU: {status['cpu_percent']:.1f}%")
                if status.get('memory_mb'):
                    print(f"    Memory: {status['memory_mb']:.1f} MB")
                if status.get('restart_count', 0) > 0:
                    print(f"    Restarts: {status['restart_count']}")
        
        print("="*60)


async def main():
    """Main function for testing"""
    checker = DockerHealthChecker()
    
    # Check Docker availability
    is_available, message = await checker.check_docker_availability()
    print(f"Docker Available: {is_available}")
    if not is_available:
        print(f"Issues: {message}")
        return
    
    # Check container health
    health_status = await checker.check_all_containers()
    
    # Print report
    checker.print_health_report()
    
    # Start monitoring (for 1 minute)
    monitor_task = asyncio.create_task(checker.start_monitoring())
    await asyncio.sleep(60)
    checker.stop_monitoring()
    await monitor_task


if __name__ == "__main__":
    asyncio.run(main())