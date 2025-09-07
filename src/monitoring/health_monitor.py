#!/usr/bin/env python3
"""
Health Monitoring System for AI Swarm Platform
Provides real-time health checks, metrics collection, and alerting
"""

import asyncio
import json
import time
import psutil
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging

# Import error handling utilities
from error_handling import ErrorContext, ErrorSeverity, SwarmLogger


class HealthStatus(Enum):
    """System health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class ComponentType(Enum):
    """Types of system components"""
    AGENT = "agent"
    DATABASE = "database"
    API = "api"
    MCP_SERVER = "mcp_server"
    MEMORY = "memory"
    CPU = "cpu"
    DISK = "disk"
    NETWORK = "network"


@dataclass
class HealthMetric:
    """Individual health metric"""
    name: str
    value: float
    unit: str
    threshold_warning: float
    threshold_critical: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def get_status(self) -> HealthStatus:
        """Determine status based on thresholds"""
        if self.value >= self.threshold_critical:
            return HealthStatus.CRITICAL
        elif self.value >= self.threshold_warning:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY


@dataclass
class ComponentHealth:
    """Health status of a system component"""
    component_type: ComponentType
    component_id: str
    status: HealthStatus
    metrics: Dict[str, HealthMetric]
    last_check: datetime
    error_count: int = 0
    uptime_seconds: float = 0
    additional_info: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'component_type': self.component_type.value,
            'component_id': self.component_id,
            'status': self.status.value,
            'metrics': {k: asdict(v) for k, v in self.metrics.items()},
            'last_check': self.last_check.isoformat(),
            'error_count': self.error_count,
            'uptime_seconds': self.uptime_seconds,
            'additional_info': self.additional_info or {}
        }


class SystemMonitor:
    """Monitor system resources"""
    
    def __init__(self):
        self.start_time = time.time()
        
    def get_cpu_metrics(self) -> HealthMetric:
        """Get CPU usage metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        return HealthMetric(
            name="cpu_usage",
            value=cpu_percent,
            unit="percent",
            threshold_warning=70.0,
            threshold_critical=90.0
        )
    
    def get_memory_metrics(self) -> HealthMetric:
        """Get memory usage metrics"""
        memory = psutil.virtual_memory()
        return HealthMetric(
            name="memory_usage",
            value=memory.percent,
            unit="percent",
            threshold_warning=80.0,
            threshold_critical=95.0
        )
    
    def get_disk_metrics(self, path: str = "/") -> HealthMetric:
        """Get disk usage metrics"""
        disk = psutil.disk_usage(path)
        return HealthMetric(
            name="disk_usage",
            value=disk.percent,
            unit="percent",
            threshold_warning=80.0,
            threshold_critical=90.0
        )
    
    def get_network_metrics(self) -> Dict[str, HealthMetric]:
        """Get network metrics"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': HealthMetric(
                name="network_bytes_sent",
                value=net_io.bytes_sent,
                unit="bytes",
                threshold_warning=float('inf'),
                threshold_critical=float('inf')
            ),
            'bytes_recv': HealthMetric(
                name="network_bytes_received",
                value=net_io.bytes_recv,
                unit="bytes",
                threshold_warning=float('inf'),
                threshold_critical=float('inf')
            ),
            'errors': HealthMetric(
                name="network_errors",
                value=net_io.errin + net_io.errout,
                unit="count",
                threshold_warning=100,
                threshold_critical=1000
            )
        }
    
    def get_system_uptime(self) -> float:
        """Get system uptime in seconds"""
        return time.time() - self.start_time
    
    def check_system_health(self) -> ComponentHealth:
        """Check overall system health"""
        cpu_metric = self.get_cpu_metrics()
        memory_metric = self.get_memory_metrics()
        disk_metric = self.get_disk_metrics()
        network_metrics = self.get_network_metrics()
        
        # Determine overall status
        metrics_list = [cpu_metric, memory_metric, disk_metric] + list(network_metrics.values())
        statuses = [m.get_status() for m in metrics_list]
        
        if HealthStatus.CRITICAL in statuses:
            overall_status = HealthStatus.CRITICAL
        elif HealthStatus.DEGRADED in statuses:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        return ComponentHealth(
            component_type=ComponentType.CPU,
            component_id="system",
            status=overall_status,
            metrics={
                'cpu': cpu_metric,
                'memory': memory_metric,
                'disk': disk_metric,
                **network_metrics
            },
            last_check=datetime.now(),
            uptime_seconds=self.get_system_uptime()
        )


class DatabaseMonitor:
    """Monitor database health"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def check_database_health(self) -> ComponentHealth:
        """Check database health and metrics"""
        metrics = {}
        status = HealthStatus.HEALTHY
        error_count = 0
        additional_info = {}
        
        try:
            # Check if database file exists
            if not Path(self.db_path).exists():
                status = HealthStatus.CRITICAL
                error_count += 1
                additional_info['error'] = "Database file not found"
            else:
                # Check database size
                db_size = Path(self.db_path).stat().st_size / (1024 * 1024)  # MB
                metrics['size'] = HealthMetric(
                    name="database_size",
                    value=db_size,
                    unit="MB",
                    threshold_warning=100,
                    threshold_critical=500
                )
                
                # Test database connection
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get table counts
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                metrics['tables'] = HealthMetric(
                    name="table_count",
                    value=table_count,
                    unit="count",
                    threshold_warning=float('inf'),
                    threshold_critical=float('inf')
                )
                
                # Check for locks (simplified check)
                try:
                    cursor.execute("BEGIN EXCLUSIVE")
                    cursor.execute("ROLLBACK")
                    metrics['locks'] = HealthMetric(
                        name="database_locks",
                        value=0,
                        unit="count",
                        threshold_warning=1,
                        threshold_critical=5
                    )
                except sqlite3.OperationalError:
                    metrics['locks'] = HealthMetric(
                        name="database_locks",
                        value=1,
                        unit="count",
                        threshold_warning=1,
                        threshold_critical=5
                    )
                    status = HealthStatus.DEGRADED
                
                conn.close()
                
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            error_count += 1
            additional_info['error'] = str(e)
        
        # Determine overall status from metrics
        if metrics:
            metric_statuses = [m.get_status() for m in metrics.values()]
            if HealthStatus.CRITICAL in metric_statuses:
                status = HealthStatus.CRITICAL
            elif HealthStatus.DEGRADED in metric_statuses:
                status = HealthStatus.DEGRADED
        
        return ComponentHealth(
            component_type=ComponentType.DATABASE,
            component_id=self.db_path,
            status=status,
            metrics=metrics,
            last_check=datetime.now(),
            error_count=error_count,
            additional_info=additional_info
        )


class AgentMonitor:
    """Monitor agent health"""
    
    def __init__(self, memory_system):
        self.memory_system = memory_system
        
    async def check_agent_health(self, agent_id: str) -> ComponentHealth:
        """Check individual agent health"""
        metrics = {}
        status = HealthStatus.HEALTHY
        error_count = 0
        additional_info = {}
        
        try:
            # Get agent state from memory system
            agents = self.memory_system.get_active_agents()
            agent = next((a for a in agents if a.id == agent_id), None)
            
            if not agent:
                status = HealthStatus.CRITICAL
                additional_info['error'] = f"Agent {agent_id} not found"
            else:
                # Check workload
                metrics['workload'] = HealthMetric(
                    name="agent_workload",
                    value=agent.workload,
                    unit="tasks",
                    threshold_warning=0.8,
                    threshold_critical=1.0
                )
                
                # Check error rate
                metrics['errors'] = HealthMetric(
                    name="agent_errors",
                    value=agent.error_count,
                    unit="count",
                    threshold_warning=5,
                    threshold_critical=10
                )
                
                # Check last heartbeat
                time_since_heartbeat = (datetime.now() - agent.last_heartbeat).total_seconds()
                metrics['heartbeat'] = HealthMetric(
                    name="time_since_heartbeat",
                    value=time_since_heartbeat,
                    unit="seconds",
                    threshold_warning=60,
                    threshold_critical=300
                )
                
                # Determine status from agent state
                if agent.status.value == "error":
                    status = HealthStatus.UNHEALTHY
                elif agent.status.value == "blocked":
                    status = HealthStatus.DEGRADED
                
                additional_info['agent_type'] = agent.type.value
                additional_info['current_tasks'] = len(agent.current_tasks)
                
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            error_count += 1
            additional_info['error'] = str(e)
        
        return ComponentHealth(
            component_type=ComponentType.AGENT,
            component_id=agent_id,
            status=status,
            metrics=metrics,
            last_check=datetime.now(),
            error_count=error_count,
            additional_info=additional_info
        )


class HealthMonitor:
    """Central health monitoring system"""
    
    def __init__(self, memory_system=None, db_path: str = "swarm_memory.db"):
        self.system_monitor = SystemMonitor()
        self.database_monitor = DatabaseMonitor(db_path)
        self.agent_monitor = AgentMonitor(memory_system) if memory_system else None
        self.logger = SwarmLogger()
        self.health_history = []
        self.max_history_size = 1000
        self.alert_callbacks = []
        
    def register_alert_callback(self, callback):
        """Register callback for health alerts"""
        self.alert_callbacks.append(callback)
        
    async def check_all_health(self) -> Dict[str, ComponentHealth]:
        """Check health of all components"""
        health_status = {}
        
        # Check system health
        health_status['system'] = self.system_monitor.check_system_health()
        
        # Check database health
        health_status['database'] = self.database_monitor.check_database_health()
        
        # Check agent health if available
        if self.agent_monitor and self.agent_monitor.memory_system:
            agents = self.agent_monitor.memory_system.get_active_agents()
            for agent in agents:
                agent_health = await self.agent_monitor.check_agent_health(agent.id)
                health_status[f'agent_{agent.id}'] = agent_health
        
        # Store in history
        self.health_history.append({
            'timestamp': datetime.now().isoformat(),
            'status': {k: v.to_dict() for k, v in health_status.items()}
        })
        
        # Trim history if needed
        if len(self.health_history) > self.max_history_size:
            self.health_history = self.health_history[-self.max_history_size:]
        
        # Check for alerts
        await self.check_alerts(health_status)
        
        return health_status
    
    async def check_alerts(self, health_status: Dict[str, ComponentHealth]):
        """Check for conditions that require alerts"""
        for component_id, health in health_status.items():
            if health.status in [HealthStatus.CRITICAL, HealthStatus.UNHEALTHY]:
                alert_data = {
                    'component': component_id,
                    'status': health.status.value,
                    'metrics': {k: v.value for k, v in health.metrics.items()},
                    'timestamp': datetime.now().isoformat()
                }
                
                # Log alert
                self.logger.loggers['error'].critical(
                    f"HEALTH ALERT: {component_id} is {health.status.value}",
                    extra=alert_data
                )
                
                # Call registered callbacks
                for callback in self.alert_callbacks:
                    try:
                        await callback(alert_data)
                    except Exception as e:
                        logging.error(f"Alert callback failed: {str(e)}")
    
    def get_overall_status(self, health_status: Dict[str, ComponentHealth]) -> HealthStatus:
        """Determine overall system health status"""
        statuses = [h.status for h in health_status.values()]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of current health status"""
        if not self.health_history:
            return {"status": "No health data available"}
        
        latest = self.health_history[-1]
        health_status = {}
        for k, v in latest['status'].items():
            # Reconstruct ComponentHealth from dict
            comp = ComponentHealth(
                component_type=ComponentType(v['component_type']),
                component_id=v['component_id'],
                status=HealthStatus(v['status']),
                metrics={},  # Skip metrics reconstruction for now
                last_check=datetime.fromisoformat(v['last_check']),
                error_count=v['error_count'],
                uptime_seconds=v.get('uptime_seconds', 0),
                additional_info=v.get('additional_info')
            )
            health_status[k] = comp
        
        overall_status = self.get_overall_status(health_status)
        
        return {
            'overall_status': overall_status.value,
            'timestamp': latest['timestamp'],
            'components': {
                k: {
                    'status': v.status.value,
                    'error_count': v.error_count,
                    'metrics_summary': {
                        m_name: {
                            'value': m.value,
                            'status': m.get_status().value
                        } for m_name, m in v.metrics.items()
                    }
                } for k, v in health_status.items()
            },
            'system_metrics': {
                'cpu': health_status['system'].metrics.get('cpu', HealthMetric('cpu', 0, '%', 70, 90)).value if 'system' in health_status and hasattr(health_status['system'], 'metrics') else 0,
                'memory': health_status['system'].metrics.get('memory', HealthMetric('memory', 0, '%', 80, 95)).value if 'system' in health_status and hasattr(health_status['system'], 'metrics') else 0,
                'disk': health_status['system'].metrics.get('disk', HealthMetric('disk', 0, '%', 80, 90)).value if 'system' in health_status and hasattr(health_status['system'], 'metrics') else 0,
            } if 'system' in health_status else {}
        }
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous health monitoring"""
        logging.info(f"Starting health monitoring with {interval_seconds}s interval")
        
        while True:
            try:
                await self.check_all_health()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logging.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(interval_seconds)


class HealthEndpoint:
    """Health check endpoint for external monitoring"""
    
    def __init__(self, health_monitor: HealthMonitor):
        self.health_monitor = health_monitor
        
    async def get_health(self) -> Tuple[int, Dict[str, Any]]:
        """Get health status for HTTP endpoint"""
        summary = self.health_monitor.get_health_summary()
        
        # Map health status to HTTP codes
        status_codes = {
            'healthy': 200,
            'degraded': 200,  # Still operational
            'unhealthy': 503,
            'critical': 503,
        }
        
        status_code = status_codes.get(
            summary.get('overall_status', 'unhealthy'),
            503
        )
        
        return status_code, summary
    
    async def get_readiness(self) -> Tuple[int, Dict[str, Any]]:
        """Check if system is ready to accept requests"""
        summary = self.health_monitor.get_health_summary()
        overall_status = summary.get('overall_status', 'unhealthy')
        
        if overall_status in ['healthy', 'degraded']:
            return 200, {'ready': True, 'status': overall_status}
        else:
            return 503, {'ready': False, 'status': overall_status}
    
    async def get_liveness(self) -> Tuple[int, Dict[str, Any]]:
        """Check if system is alive (for container orchestration)"""
        try:
            # Simple check - can we access system metrics?
            cpu_metric = self.health_monitor.system_monitor.get_cpu_metrics()
            return 200, {'alive': True, 'cpu': cpu_metric.value}
        except Exception as e:
            return 503, {'alive': False, 'error': str(e)}


# Example alert callback
async def example_alert_handler(alert_data: Dict[str, Any]):
    """Example handler for health alerts"""
    logging.critical(f"ALERT: {alert_data['component']} is {alert_data['status']}")
    # Could send email, SMS, webhook, etc.