#!/usr/bin/env python3
"""
Enhanced Monitoring and Alerting System for AI Swarm Intelligence
Provides comprehensive monitoring, alerting, and notification capabilities
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import aiohttp
from pathlib import Path
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Import our error handling system
from error_handling import ErrorHandler, SwarmLogger

# Configure enhanced logging
logger = SwarmLogger("monitoring_alerts").get_logger()

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SILENCED = "silenced"

@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    source: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None
    resolution_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
        if self.annotations is None:
            self.annotations = {}

@dataclass
class MetricThreshold:
    """Metric threshold configuration"""
    metric_name: str
    threshold_value: float
    comparison: str  # 'gt', 'lt', 'eq', 'gte', 'lte'
    duration: int  # seconds
    severity: AlertSeverity
    description: str

class NotificationChannel:
    """Base class for notification channels"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", True)
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send notification for alert"""
        raise NotImplementedError

class EmailNotifier(NotificationChannel):
    """Email notification channel"""
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send email notification"""
        try:
            if not self.enabled:
                return True
            
            smtp_server = self.config.get("smtp_server", "localhost")
            smtp_port = self.config.get("smtp_port", 587)
            username = self.config.get("username")
            password = self.config.get("password")
            from_email = self.config.get("from_email")
            to_emails = self.config.get("to_emails", [])
            
            if not to_emails:
                logger.warning("No email recipients configured")
                return False
            
            # Create message
            msg = MimeMultipart()
            msg['From'] = from_email
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            # Create email body
            body = f"""
Alert Details:
--------------
Title: {alert.title}
Severity: {alert.severity.value.upper()}
Source: {alert.source}
Timestamp: {alert.timestamp.isoformat()}
Status: {alert.status.value}

Description:
{alert.description}

Labels:
{json.dumps(alert.labels, indent=2)}

Annotations:
{json.dumps(alert.annotations, indent=2)}
"""
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if username and password:
                    server.starttls()
                    server.login(username, password)
                
                server.send_message(msg)
            
            logger.info(f"Email alert sent for {alert.alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False

class SlackNotifier(NotificationChannel):
    """Slack notification channel"""
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send Slack notification"""
        try:
            if not self.enabled:
                return True
            
            webhook_url = self.config.get("webhook_url")
            if not webhook_url:
                logger.warning("Slack webhook URL not configured")
                return False
            
            # Color coding based on severity
            color_map = {
                AlertSeverity.INFO: "#36a64f",      # green
                AlertSeverity.WARNING: "#ff9900",   # orange
                AlertSeverity.ERROR: "#ff4d4d",     # red
                AlertSeverity.CRITICAL: "#990000"   # dark red
            }
            
            # Create Slack message
            message = {
                "username": "AI Swarm Monitor",
                "icon_emoji": ":robot_face:",
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, "#36a64f"),
                        "title": f"{alert.severity.value.upper()}: {alert.title}",
                        "text": alert.description,
                        "fields": [
                            {
                                "title": "Source",
                                "value": alert.source,
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": alert.timestamp.isoformat(),
                                "short": True
                            },
                            {
                                "title": "Status",
                                "value": alert.status.value,
                                "short": True
                            },
                            {
                                "title": "Alert ID",
                                "value": alert.alert_id,
                                "short": True
                            }
                        ],
                        "footer": "AI Swarm Intelligence",
                        "ts": int(alert.timestamp.timestamp())
                    }
                ]
            }
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    if response.status == 200:
                        logger.info(f"Slack alert sent for {alert.alert_id}")
                        return True
                    else:
                        logger.error(f"Slack webhook failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False

class WebhookNotifier(NotificationChannel):
    """Generic webhook notification channel"""
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send webhook notification"""
        try:
            if not self.enabled:
                return True
            
            webhook_url = self.config.get("url")
            if not webhook_url:
                logger.warning("Webhook URL not configured")
                return False
            
            # Prepare webhook payload
            payload = {
                "alert_id": alert.alert_id,
                "title": alert.title,
                "description": alert.description,
                "severity": alert.severity.value,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
                "status": alert.status.value,
                "labels": alert.labels,
                "annotations": alert.annotations
            }
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status in [200, 201, 202]:
                        logger.info(f"Webhook alert sent for {alert.alert_id}")
                        return True
                    else:
                        logger.error(f"Webhook failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False

class MonitoringSystem:
    """Comprehensive monitoring and alerting system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize monitoring system"""
        self.config_path = config_path or "monitoring_config.json"
        self.config = self._load_config()
        
        # Initialize error handler
        self.error_handler = ErrorHandler()
        
        # Monitoring state
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.metrics_cache: Dict[str, Any] = {}
        self.last_metrics_update = datetime.min
        
        # Notification channels
        self.notification_channels: List[NotificationChannel] = []
        self._setup_notification_channels()
        
        # Metric thresholds
        self.metric_thresholds: List[MetricThreshold] = []
        self._setup_metric_thresholds()
        
        # Background tasks
        self.background_tasks = set()
        
        # Services to monitor
        self.services = self.config.get("services", {})
        
        logger.info("Monitoring system initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        if Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "check_interval": 30,
                "metric_retention_hours": 24,
                "alert_cooldown_minutes": 15,
                "services": {
                    "swarm-api": {
                        "url": "http://localhost:8001",
                        "health_endpoint": "/health",
                        "metrics_endpoint": "/metrics"
                    },
                    "api-bridge": {
                        "url": "http://localhost:8002",
                        "health_endpoint": "/health",
                        "metrics_endpoint": "/metrics"
                    },
                    "autogpt-primary": {
                        "url": "http://localhost:3000",
                        "health_endpoint": "/health",
                        "metrics_endpoint": "/metrics"
                    }
                },
                "notifications": {
                    "email": {
                        "enabled": False,
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587,
                        "from_email": "swarm@example.com",
                        "to_emails": ["admin@example.com"]
                    },
                    "slack": {
                        "enabled": False,
                        "webhook_url": os.getenv("SLACK_WEBHOOK_URL", "")
                    }
                },
                "thresholds": {
                    "response_time_ms": {
                        "warning": 5000,
                        "error": 10000,
                        "critical": 30000
                    },
                    "error_rate_percent": {
                        "warning": 5,
                        "error": 10,
                        "critical": 25
                    },
                    "memory_usage_percent": {
                        "warning": 80,
                        "error": 90,
                        "critical": 95
                    },
                    "cpu_usage_percent": {
                        "warning": 80,
                        "error": 90,
                        "critical": 95
                    }
                }
            }
    
    def _setup_notification_channels(self):
        """Setup notification channels"""
        notifications_config = self.config.get("notifications", {})
        
        # Email notifications
        email_config = notifications_config.get("email", {})
        if email_config.get("enabled"):
            self.notification_channels.append(EmailNotifier("email", email_config))
        
        # Slack notifications
        slack_config = notifications_config.get("slack", {})
        if slack_config.get("enabled") and slack_config.get("webhook_url"):
            self.notification_channels.append(SlackNotifier("slack", slack_config))
        
        # Webhook notifications
        webhook_config = notifications_config.get("webhook", {})
        if webhook_config.get("enabled") and webhook_config.get("url"):
            self.notification_channels.append(WebhookNotifier("webhook", webhook_config))
        
        logger.info(f"Setup {len(self.notification_channels)} notification channels")
    
    def _setup_metric_thresholds(self):
        """Setup metric thresholds for alerting"""
        thresholds_config = self.config.get("thresholds", {})
        
        # Response time thresholds
        response_thresholds = thresholds_config.get("response_time_ms", {})
        for severity_name, threshold_value in response_thresholds.items():
            self.metric_thresholds.append(MetricThreshold(
                metric_name="response_time_ms",
                threshold_value=float(threshold_value),
                comparison="gt",
                duration=60,  # 1 minute
                severity=AlertSeverity(severity_name),
                description=f"Response time exceeded {threshold_value}ms"
            ))
        
        # Error rate thresholds
        error_thresholds = thresholds_config.get("error_rate_percent", {})
        for severity_name, threshold_value in error_thresholds.items():
            self.metric_thresholds.append(MetricThreshold(
                metric_name="error_rate_percent",
                threshold_value=float(threshold_value),
                comparison="gt",
                duration=300,  # 5 minutes
                severity=AlertSeverity(severity_name),
                description=f"Error rate exceeded {threshold_value}%"
            ))
        
        # Memory usage thresholds
        memory_thresholds = thresholds_config.get("memory_usage_percent", {})
        for severity_name, threshold_value in memory_thresholds.items():
            self.metric_thresholds.append(MetricThreshold(
                metric_name="memory_usage_percent",
                threshold_value=float(threshold_value),
                comparison="gt",
                duration=180,  # 3 minutes
                severity=AlertSeverity(severity_name),
                description=f"Memory usage exceeded {threshold_value}%"
            ))
        
        # CPU usage thresholds
        cpu_thresholds = thresholds_config.get("cpu_usage_percent", {})
        for severity_name, threshold_value in cpu_thresholds.items():
            self.metric_thresholds.append(MetricThreshold(
                metric_name="cpu_usage_percent",
                threshold_value=float(threshold_value),
                comparison="gt",
                duration=180,  # 3 minutes
                severity=AlertSeverity(severity_name),
                description=f"CPU usage exceeded {threshold_value}%"
            ))
        
        logger.info(f"Setup {len(self.metric_thresholds)} metric thresholds")
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        logger.info("Starting monitoring system")
        
        # Initialize error handler
        await self.error_handler.initialize()
        
        # Start background monitoring tasks
        monitor_task = asyncio.create_task(self._monitoring_loop())
        self.background_tasks.add(monitor_task)
        monitor_task.add_done_callback(self.background_tasks.discard)
        
        alert_task = asyncio.create_task(self._alert_processing_loop())
        self.background_tasks.add(alert_task)
        alert_task.add_done_callback(self.background_tasks.discard)
        
        cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.background_tasks.add(cleanup_task)
        cleanup_task.add_done_callback(self.background_tasks.discard)
        
        logger.info("Monitoring system started")
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        logger.info("Stopping monitoring system")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("Monitoring system stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        check_interval = self.config.get("check_interval", 30)
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                await self._collect_metrics()
                await self._evaluate_thresholds()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _collect_metrics(self):
        """Collect metrics from all monitored services"""
        logger.debug("Collecting metrics from services")
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for service_name, service_config in self.services.items():
                try:
                    # Health check
                    health_url = f"{service_config['url']}{service_config['health_endpoint']}"
                    async with session.get(health_url) as response:
                        if response.status == 200:
                            health_data = await response.json()
                            self.metrics_cache[f"{service_name}_health"] = {
                                "status": "healthy",
                                "data": health_data,
                                "timestamp": datetime.now()
                            }
                        else:
                            await self._create_alert(
                                f"{service_name}_health_check_failed",
                                f"{service_name} health check failed",
                                f"Health check returned status {response.status}",
                                AlertSeverity.ERROR,
                                service_name
                            )
                
                except asyncio.TimeoutError:
                    await self._create_alert(
                        f"{service_name}_timeout",
                        f"{service_name} timeout",
                        f"Service {service_name} timed out during health check",
                        AlertSeverity.WARNING,
                        service_name
                    )
                
                except Exception as e:
                    await self._create_alert(
                        f"{service_name}_connection_error",
                        f"{service_name} connection error",
                        f"Failed to connect to {service_name}: {e}",
                        AlertSeverity.ERROR,
                        service_name
                    )
                
                try:
                    # Metrics collection
                    if "metrics_endpoint" in service_config:
                        metrics_url = f"{service_config['url']}{service_config['metrics_endpoint']}"
                        async with session.get(metrics_url) as response:
                            if response.status == 200:
                                metrics_data = await response.json()
                                self.metrics_cache[f"{service_name}_metrics"] = {
                                    "data": metrics_data,
                                    "timestamp": datetime.now()
                                }
                
                except Exception as e:
                    logger.debug(f"Failed to collect metrics from {service_name}: {e}")
        
        self.last_metrics_update = datetime.now()
    
    async def _evaluate_thresholds(self):
        """Evaluate metric thresholds and create alerts"""
        for threshold in self.metric_thresholds:
            try:
                # Find metrics that match this threshold
                for cache_key, cache_data in self.metrics_cache.items():
                    if "metrics" in cache_key and "data" in cache_data:
                        metric_value = self._extract_metric_value(
                            cache_data["data"], 
                            threshold.metric_name
                        )
                        
                        if metric_value is not None:
                            if self._threshold_exceeded(metric_value, threshold):
                                service_name = cache_key.split("_metrics")[0]
                                alert_id = f"{service_name}_{threshold.metric_name}_{threshold.severity.value}"
                                
                                await self._create_alert(
                                    alert_id,
                                    f"{threshold.metric_name} threshold exceeded",
                                    f"{threshold.description}. Current value: {metric_value}",
                                    threshold.severity,
                                    service_name,
                                    labels={"metric": threshold.metric_name, "threshold": str(threshold.threshold_value)}
                                )
            
            except Exception as e:
                logger.error(f"Error evaluating threshold {threshold.metric_name}: {e}")
    
    def _extract_metric_value(self, metrics_data: Dict[str, Any], metric_name: str) -> Optional[float]:
        """Extract metric value from metrics data"""
        # Simple extraction - can be extended for complex metrics
        if metric_name in metrics_data:
            return float(metrics_data[metric_name])
        
        # Look for nested metrics
        for key, value in metrics_data.items():
            if isinstance(value, dict) and metric_name in value:
                return float(value[metric_name])
        
        return None
    
    def _threshold_exceeded(self, value: float, threshold: MetricThreshold) -> bool:
        """Check if threshold is exceeded"""
        if threshold.comparison == "gt":
            return value > threshold.threshold_value
        elif threshold.comparison == "gte":
            return value >= threshold.threshold_value
        elif threshold.comparison == "lt":
            return value < threshold.threshold_value
        elif threshold.comparison == "lte":
            return value <= threshold.threshold_value
        elif threshold.comparison == "eq":
            return value == threshold.threshold_value
        return False
    
    async def _create_alert(
        self, 
        alert_id: str, 
        title: str, 
        description: str, 
        severity: AlertSeverity,
        source: str,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None
    ):
        """Create and process an alert"""
        # Check if alert already exists and is active
        if alert_id in self.active_alerts:
            # Update existing alert
            existing_alert = self.active_alerts[alert_id]
            existing_alert.timestamp = datetime.now()
            return
        
        # Check cooldown period
        cooldown_minutes = self.config.get("alert_cooldown_minutes", 15)
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.alert_id == alert_id and 
            datetime.now() - alert.timestamp < timedelta(minutes=cooldown_minutes)
        ]
        
        if recent_alerts:
            logger.debug(f"Alert {alert_id} in cooldown period")
            return
        
        # Create new alert
        alert = Alert(
            alert_id=alert_id,
            title=title,
            description=description,
            severity=severity,
            source=source,
            timestamp=datetime.now(),
            labels=labels or {},
            annotations=annotations or {}
        )
        
        # Add to active alerts
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        logger.info(f"Created {severity.value} alert: {title}")
        
        # Send notifications
        await self._send_alert_notifications(alert)
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications through all configured channels"""
        notification_tasks = []
        
        for channel in self.notification_channels:
            task = asyncio.create_task(channel.send_notification(alert))
            notification_tasks.append(task)
        
        if notification_tasks:
            results = await asyncio.gather(*notification_tasks, return_exceptions=True)
            
            successful_notifications = sum(1 for result in results if result is True)
            logger.info(f"Sent {successful_notifications}/{len(notification_tasks)} notifications for alert {alert.alert_id}")
    
    async def resolve_alert(self, alert_id: str, resolution_note: Optional[str] = None):
        """Resolve an active alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolution_time = datetime.now()
            
            if resolution_note:
                alert.annotations["resolution_note"] = resolution_note
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            logger.info(f"Resolved alert: {alert_id}")
            
            # Send resolution notification
            alert.title = f"RESOLVED: {alert.title}"
            await self._send_alert_notifications(alert)
    
    async def _alert_processing_loop(self):
        """Process and manage alerts"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Auto-resolve alerts for recovered services
                await self._check_alert_recovery()
                
            except Exception as e:
                logger.error(f"Error in alert processing loop: {e}")
                await asyncio.sleep(5)
    
    async def _check_alert_recovery(self):
        """Check if any active alerts can be auto-resolved"""
        alerts_to_resolve = []
        
        for alert_id, alert in self.active_alerts.items():
            # Check if the condition that triggered the alert has been resolved
            if await self._is_alert_condition_resolved(alert):
                alerts_to_resolve.append(alert_id)
        
        # Resolve recovered alerts
        for alert_id in alerts_to_resolve:
            await self.resolve_alert(alert_id, "Auto-resolved: condition no longer met")
    
    async def _is_alert_condition_resolved(self, alert: Alert) -> bool:
        """Check if the condition that triggered an alert has been resolved"""
        # Health check alerts
        if "health_check_failed" in alert.alert_id:
            health_key = f"{alert.source}_health"
            if health_key in self.metrics_cache:
                return self.metrics_cache[health_key].get("status") == "healthy"
        
        # Timeout alerts
        if "timeout" in alert.alert_id:
            health_key = f"{alert.source}_health"
            if health_key in self.metrics_cache:
                # If we have recent health data, the timeout is resolved
                last_update = self.metrics_cache[health_key].get("timestamp", datetime.min)
                return datetime.now() - last_update < timedelta(minutes=5)
        
        # Metric threshold alerts
        metric_name = alert.labels.get("metric")
        if metric_name:
            threshold_str = alert.labels.get("threshold")
            if threshold_str:
                threshold_value = float(threshold_str)
                metrics_key = f"{alert.source}_metrics"
                
                if metrics_key in self.metrics_cache:
                    current_value = self._extract_metric_value(
                        self.metrics_cache[metrics_key]["data"], 
                        metric_name
                    )
                    
                    if current_value is not None:
                        # For "greater than" thresholds, resolved if value is now below threshold
                        return current_value <= threshold_value
        
        return False
    
    async def _cleanup_loop(self):
        """Cleanup old metrics and alerts"""
        retention_hours = self.config.get("metric_retention_hours", 24)
        
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                cutoff_time = datetime.now() - timedelta(hours=retention_hours)
                
                # Clean up old metrics
                keys_to_remove = []
                for key, data in self.metrics_cache.items():
                    if isinstance(data, dict) and "timestamp" in data:
                        if data["timestamp"] < cutoff_time:
                            keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self.metrics_cache[key]
                
                # Clean up old alert history
                self.alert_history = [
                    alert for alert in self.alert_history
                    if alert.timestamp > cutoff_time
                ]
                
                logger.info(f"Cleaned up {len(keys_to_remove)} old metrics and {len(self.alert_history)} old alerts")
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        active_alerts_by_severity = {}
        for alert in self.active_alerts.values():
            severity = alert.severity.value
            if severity not in active_alerts_by_severity:
                active_alerts_by_severity[severity] = 0
            active_alerts_by_severity[severity] += 1
        
        return {
            "monitoring_status": "active",
            "last_metrics_update": self.last_metrics_update.isoformat(),
            "active_alerts": len(self.active_alerts),
            "alerts_by_severity": active_alerts_by_severity,
            "monitored_services": list(self.services.keys()),
            "notification_channels": len(self.notification_channels),
            "metric_thresholds": len(self.metric_thresholds),
            "metrics_cache_size": len(self.metrics_cache)
        }
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary"""
        return {
            "active_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "title": alert.title,
                    "severity": alert.severity.value,
                    "source": alert.source,
                    "timestamp": alert.timestamp.isoformat(),
                    "status": alert.status.value
                }
                for alert in self.active_alerts.values()
            ],
            "recent_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "title": alert.title,
                    "severity": alert.severity.value,
                    "source": alert.source,
                    "timestamp": alert.timestamp.isoformat(),
                    "status": alert.status.value,
                    "resolution_time": alert.resolution_time.isoformat() if alert.resolution_time else None
                }
                for alert in sorted(self.alert_history[-50:], key=lambda x: x.timestamp, reverse=True)
            ]
        }

# Configuration file generator
def create_monitoring_config():
    """Create default monitoring configuration file"""
    config = {
        "check_interval": 30,
        "metric_retention_hours": 24,
        "alert_cooldown_minutes": 15,
        "services": {
            "swarm-api": {
                "url": "http://localhost:8001",
                "health_endpoint": "/health",
                "metrics_endpoint": "/metrics"
            },
            "api-bridge": {
                "url": "http://localhost:8002", 
                "health_endpoint": "/health",
                "metrics_endpoint": "/metrics"
            },
            "autogpt-primary": {
                "url": "http://localhost:3000",
                "health_endpoint": "/health",
                "metrics_endpoint": "/metrics"
            },
            "autogpt-secondary": {
                "url": "http://localhost:3001",
                "health_endpoint": "/health",
                "metrics_endpoint": "/metrics"
            }
        },
        "notifications": {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your_email@gmail.com",
                "password": "your_app_password",
                "from_email": "swarm@yourcompany.com",
                "to_emails": ["admin@yourcompany.com", "devops@yourcompany.com"]
            },
            "slack": {
                "enabled": True,
                "webhook_url": "${SLACK_WEBHOOK_URL}"
            },
            "webhook": {
                "enabled": False,
                "url": "https://your-webhook-endpoint.com/alerts",
                "headers": {
                    "Authorization": "Bearer ${WEBHOOK_TOKEN}"
                }
            }
        },
        "thresholds": {
            "response_time_ms": {
                "warning": 5000,
                "error": 10000,
                "critical": 30000
            },
            "error_rate_percent": {
                "warning": 5,
                "error": 10,
                "critical": 25
            },
            "memory_usage_percent": {
                "warning": 80,
                "error": 90,
                "critical": 95
            },
            "cpu_usage_percent": {
                "warning": 80,
                "error": 90,
                "critical": 95
            },
            "disk_usage_percent": {
                "warning": 85,
                "error": 90,
                "critical": 95
            },
            "queue_depth": {
                "warning": 100,
                "error": 500,
                "critical": 1000
            },
            "circuit_breaker_trips": {
                "warning": 5,
                "error": 10,
                "critical": 20
            }
        }
    }
    
    with open("monitoring_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("Created monitoring_config.json")
    print("Please update the configuration with your actual values before running.")

# Standalone monitoring service
async def main():
    """Main monitoring service entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Swarm Intelligence Monitoring System")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--create-config", action="store_true", help="Create default configuration file")
    
    args = parser.parse_args()
    
    if args.create_config:
        create_monitoring_config()
        return
    
    # Initialize monitoring system
    monitoring = MonitoringSystem(args.config)
    
    try:
        await monitoring.start_monitoring()
        
        logger.info("Monitoring system is running. Press Ctrl+C to stop.")
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(60)
            status = monitoring.get_system_status()
            logger.info(f"System status: {status['active_alerts']} active alerts, "
                       f"{len(status['monitored_services'])} services monitored")
    
    except KeyboardInterrupt:
        logger.info("Shutting down monitoring system...")
    
    finally:
        await monitoring.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())