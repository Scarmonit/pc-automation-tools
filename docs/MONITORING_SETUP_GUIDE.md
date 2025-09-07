# 📊 Monitoring and Observability Setup Guide

This guide shows you how to set up comprehensive monitoring for your AI automation tools using Prometheus, Grafana, and other observability tools. Monitor system performance, AI model metrics, and service health across your entire stack.

## 🚀 Quick Start

### Automatic Setup
```bash
# Deploy complete monitoring stack
bash scripts/setup_monitoring.sh

# Access Grafana dashboard
open http://localhost:3003
```

### Manual Setup
```bash
# Start monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Configure Prometheus targets
cp prometheus.yml /etc/prometheus/
```

## 📋 Prerequisites

- **Docker & Docker Compose** - For containerized monitoring
- **8GB+ RAM** - For running monitoring stack
- **Network Access** - Between services and monitoring
- **Storage** - 10GB+ for metrics retention

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Grafana     │    │   Prometheus    │    │   AlertManager  │
│   (Port 3003)   │◄───┤   (Port 9090)   │◄───┤   (Port 9093)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Exporters     │
                    │                 │
                    │ • Node Exporter │
                    │ • GPU Exporter  │
                    │ • Docker Stats  │
                    │ • Custom Metrics│
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Ollama      │    │    Flowise      │    │   OpenHands     │
│  (Port 11434)   │    │  (Port 3001)    │    │  (Port 3002)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Configuration

### 1. Prometheus Configuration

Create or update `prometheus.yml`:

```yaml
# Prometheus configuration
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # System metrics
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # Docker metrics
  - job_name: 'docker'
    static_configs:
      - targets: ['docker-exporter:9323']

  # GPU metrics (if available)
  - job_name: 'gpu-exporter'
    static_configs:
      - targets: ['gpu-exporter:9400']

  # AI Services
  - job_name: 'ollama'
    static_configs:
      - targets: ['host.docker.internal:11434']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'flowise'
    static_configs:
      - targets: ['host.docker.internal:3001']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'openhands'
    static_configs:
      - targets: ['host.docker.internal:3002']
    metrics_path: /health
    scrape_interval: 30s

  # Custom application metrics
  - job_name: 'ai-orchestrator'
    static_configs:
      - targets: ['host.docker.internal:8080']
    metrics_path: /metrics
    scrape_interval: 15s
```

### 2. Docker Compose Configuration

Create `docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3003:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    restart: unless-stopped
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:

networks:
  default:
    name: monitoring
```

### 3. Grafana Dashboard Configuration

Create `grafana/provisioning/datasources/prometheus.yml`:

```yaml
# Grafana datasource configuration
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

Create `grafana/provisioning/dashboards/dashboard.yml`:

```yaml
# Grafana dashboard configuration
apiVersion: 1

providers:
  - name: 'AI Tools Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

## 📈 Custom Metrics Implementation

### 1. AI Service Metrics

Create `llmstack/monitoring/metrics.py`:

```python
#!/usr/bin/env python3
"""
AI Tools Metrics Collection
"""

import time
import psutil
import logging
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('ai_requests_total', 'Total AI requests', ['service', 'model', 'status'])
REQUEST_DURATION = Histogram('ai_request_duration_seconds', 'AI request duration', ['service', 'model'])
ACTIVE_SESSIONS = Gauge('ai_active_sessions', 'Active AI sessions', ['service'])
MODEL_MEMORY_USAGE = Gauge('ai_model_memory_bytes', 'Model memory usage', ['service', 'model'])
QUEUE_SIZE = Gauge('ai_queue_size', 'Request queue size', ['service'])
ERROR_RATE = Gauge('ai_error_rate', 'Error rate percentage', ['service'])

@dataclass
class MetricsConfig:
    """Metrics configuration"""
    port: int = 8080
    host: str = "0.0.0.0"
    update_interval: int = 15
    enabled_services: list = None

class AIMetricsCollector:
    """Collect metrics from AI services"""
    
    def __init__(self, config: MetricsConfig = None):
        self.config = config or MetricsConfig()
        self.services = self.config.enabled_services or [
            "ollama", "flowise", "openhands", "autogen", "aider"
        ]
        self.last_update = time.time()
        
    def start_server(self):
        """Start Prometheus metrics server"""
        try:
            start_http_server(self.config.port, addr=self.config.host)
            logger.info(f"Metrics server started on {self.config.host}:{self.config.port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
    
    def collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # GPU metrics (if available)
            gpu_metrics = self.get_gpu_metrics()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_used_bytes": memory_used,
                "disk_percent": disk_percent,
                "gpu_metrics": gpu_metrics
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def get_gpu_metrics(self) -> Dict[str, Any]:
        """Get GPU metrics if available"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            
            if not gpus:
                return {}
            
            gpu_data = {}
            for i, gpu in enumerate(gpus):
                gpu_data[f"gpu_{i}"] = {
                    "utilization": gpu.load * 100,
                    "memory_used": gpu.memoryUsed,
                    "memory_total": gpu.memoryTotal,
                    "memory_percent": (gpu.memoryUsed / gpu.memoryTotal) * 100,
                    "temperature": gpu.temperature
                }
            
            return gpu_data
            
        except ImportError:
            logger.warning("GPUtil not available, skipping GPU metrics")
            return {}
        except Exception as e:
            logger.error(f"Error getting GPU metrics: {e}")
            return {}
    
    def collect_ollama_metrics(self) -> Dict[str, Any]:
        """Collect Ollama-specific metrics"""
        try:
            import requests
            
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/version", timeout=5)
            if response.status_code == 200:
                # Get running models
                models_response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if models_response.status_code == 200:
                    models = models_response.json().get("models", [])
                    
                    return {
                        "status": "running",
                        "models_count": len(models),
                        "models": [model.get("name", "") for model in models]
                    }
            
            return {"status": "not_running"}
            
        except Exception as e:
            logger.error(f"Error collecting Ollama metrics: {e}")
            return {"status": "error", "error": str(e)}
    
    def collect_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Collect metrics for specific service"""
        collectors = {
            "ollama": self.collect_ollama_metrics,
            "flowise": lambda: self.check_service_health("http://localhost:3001"),
            "openhands": lambda: self.check_service_health("http://localhost:3002"),
            "autogen": lambda: {"status": "library"},  # Library, not service
            "aider": lambda: {"status": "library"}     # Library, not service
        }
        
        collector = collectors.get(service_name)
        if collector:
            return collector()
        
        return {"status": "unknown"}
    
    def check_service_health(self, url: str) -> Dict[str, Any]:
        """Check if service is healthy"""
        try:
            import requests
            response = requests.get(f"{url}/health", timeout=5)
            return {
                "status": "running" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code
            }
        except requests.exceptions.ConnectionError:
            return {"status": "not_running"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def update_prometheus_metrics(self):
        """Update Prometheus metrics"""
        try:
            # System metrics
            system_metrics = self.collect_system_metrics()
            
            # Update system gauges (would need additional Prometheus gauges defined)
            
            # Service metrics
            for service in self.services:
                service_metrics = self.collect_service_metrics(service)
                
                # Update service-specific metrics
                if service_metrics.get("status") == "running":
                    ACTIVE_SESSIONS.labels(service=service).set(1)
                else:
                    ACTIVE_SESSIONS.labels(service=service).set(0)
            
            self.last_update = time.time()
            logger.info("Prometheus metrics updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")
    
    def run_collector(self):
        """Run metrics collection loop"""
        logger.info("Starting metrics collection...")
        
        while True:
            try:
                self.update_prometheus_metrics()
                time.sleep(self.config.update_interval)
            except KeyboardInterrupt:
                logger.info("Metrics collection stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                time.sleep(10)  # Wait before retrying

class RequestMetrics:
    """Track individual request metrics"""
    
    @staticmethod
    def track_request(service: str, model: str = "unknown"):
        """Decorator to track request metrics"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    REQUEST_COUNT.labels(service=service, model=model, status=status).inc()
                    REQUEST_DURATION.labels(service=service, model=model).observe(duration)
            
            return wrapper
        return decorator

# Example usage in AI service code
@RequestMetrics.track_request("ollama", "llama3.2")
def ollama_chat_request(prompt: str) -> str:
    """Example function with metrics tracking"""
    # Your AI request logic here
    return "AI response"

def main():
    """Main metrics collection function"""
    config = MetricsConfig(
        port=8080,
        update_interval=15,
        enabled_services=["ollama", "flowise", "openhands"]
    )
    
    collector = AIMetricsCollector(config)
    
    # Start Prometheus metrics server
    collector.start_server()
    
    # Run collection loop
    collector.run_collector()

if __name__ == "__main__":
    main()
```

### 2. Alert Rules

Create `rules/ai_alerts.yml`:

```yaml
# AI Tools Alert Rules
groups:
  - name: ai_tools_alerts
    rules:
      # Service availability alerts
      - alert: ServiceDown
        expr: up{job=~"ollama|flowise|openhands"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "AI service {{ $labels.job }} is down"
          description: "{{ $labels.job }} has been down for more than 2 minutes"

      # High error rate alert
      - alert: HighErrorRate
        expr: (rate(ai_requests_total{status="error"}[5m]) / rate(ai_requests_total[5m])) > 0.1
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "High error rate for {{ $labels.service }}"
          description: "Error rate is {{ $value | humanizePercentage }} for service {{ $labels.service }}"

      # High response time alert
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(ai_request_duration_seconds_bucket[5m])) > 30
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time for {{ $labels.service }}"
          description: "95th percentile response time is {{ $value }}s for {{ $labels.service }}"

      # Resource usage alerts
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is above 80% for 5 minutes"

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is above 85% for 5 minutes"

      - alert: HighDiskUsage
        expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High disk usage"
          description: "Disk usage is above 90% for 5 minutes"

      # GPU alerts (if applicable)
      - alert: HighGPUMemoryUsage
        expr: (nvidia_ml_py3_device_memory_used_bytes / nvidia_ml_py3_device_memory_total_bytes) * 100 > 90
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "High GPU memory usage"
          description: "GPU memory usage is above 90% for 3 minutes"

      # Queue size alerts
      - alert: HighQueueSize
        expr: ai_queue_size > 100
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High queue size for {{ $labels.service }}"
          description: "Queue size is {{ $value }} for service {{ $labels.service }}"
```

### 3. AlertManager Configuration

Create `alertmanager.yml`:

```yaml
# AlertManager configuration
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@your-domain.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://localhost:5001/alerts'
        
  - name: 'email-alerts'
    email_configs:
      - to: 'admin@your-domain.com'
        subject: 'AI Tools Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
```

## 📊 Pre-built Dashboards

### 1. AI Tools Overview Dashboard

Create `grafana/dashboards/ai_tools_overview.json`:

```json
{
  "dashboard": {
    "id": null,
    "title": "AI Tools Overview",
    "tags": ["ai", "monitoring"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Service Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=~\"ollama|flowise|openhands\"}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ai_requests_total[5m])",
            "refId": "A"
          }
        ]
      },
      {
        "id": 3,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(ai_request_duration_seconds_bucket[5m]))",
            "refId": "A"
          }
        ]
      },
      {
        "id": 4,
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "refId": "A",
            "legendFormat": "CPU Usage %"
          },
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "refId": "B",
            "legendFormat": "Memory Usage %"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
```

## 🧪 Testing Monitoring Setup

### 1. Basic Health Check

```bash
# test_monitoring.sh
#!/bin/bash

echo "Testing monitoring stack..."

# Check Prometheus
echo "Checking Prometheus..."
curl -s http://localhost:9090/-/healthy && echo "✓ Prometheus is healthy" || echo "✗ Prometheus is not responding"

# Check Grafana
echo "Checking Grafana..."
curl -s http://localhost:3003/api/health && echo "✓ Grafana is healthy" || echo "✗ Grafana is not responding"

# Check metrics endpoint
echo "Checking custom metrics..."
curl -s http://localhost:8080/metrics | head -5 && echo "✓ Custom metrics available" || echo "✗ Custom metrics not available"

# Check specific metrics
echo "Checking AI service metrics..."
curl -s "http://localhost:9090/api/v1/query?query=up" | jq '.data.result[0].value[1]' && echo "✓ Service metrics available" || echo "✗ Service metrics not available"
```

### 2. Load Testing

```python
# load_test_monitoring.py
import asyncio
import aiohttp
import time
import random
from concurrent.futures import ThreadPoolExecutor

async def simulate_ai_requests():
    """Simulate AI service requests for monitoring"""
    
    services = [
        "http://localhost:11434/api/generate",
        "http://localhost:3001/api/v1/health",
        "http://localhost:3002/health"
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for _ in range(100):  # 100 concurrent requests
            service = random.choice(services)
            task = asyncio.create_task(make_request(session, service))
            tasks.append(task)
            
            # Random delay between requests
            await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Wait for all requests to complete
        await asyncio.gather(*tasks, return_exceptions=True)

async def make_request(session, url):
    """Make a single request"""
    try:
        async with session.get(url, timeout=10) as response:
            await response.text()
            return response.status
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def run_load_test():
    """Run load test to generate metrics"""
    print("Starting load test...")
    start_time = time.time()
    
    asyncio.run(simulate_ai_requests())
    
    duration = time.time() - start_time
    print(f"Load test completed in {duration:.2f} seconds")

if __name__ == "__main__":
    run_load_test()
```

## 🛟 Troubleshooting

### Common Issues

#### 1. Prometheus Not Scraping Targets
```bash
# Check Prometheus configuration
docker exec prometheus promtool check config /etc/prometheus/prometheus.yml

# Check target status
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Reload configuration
curl -X POST http://localhost:9090/-/reload
```

#### 2. Grafana Dashboard Issues
```bash
# Check Grafana logs
docker logs grafana

# Reset admin password
docker exec -it grafana grafana-cli admin reset-admin-password admin

# Check datasource connection
curl -u admin:admin http://localhost:3003/api/datasources
```

#### 3. Missing Metrics
```bash
# Check metrics server
curl http://localhost:8080/metrics

# Check service endpoints
curl http://localhost:11434/api/version
curl http://localhost:3001/health
curl http://localhost:3002/health

# Restart metrics collector
python3 llmstack/monitoring/metrics.py
```

#### 4. Alert Not Firing
```bash
# Check alert rules
curl http://localhost:9090/api/v1/rules

# Check AlertManager
curl http://localhost:9093/api/v1/alerts

# Test alert rule
curl -G http://localhost:9090/api/v1/query --data-urlencode 'query=up{job="ollama"} == 0'
```

### Performance Optimization

#### 1. Reduce Metric Collection Frequency
```yaml
# In prometheus.yml
scrape_interval: 30s  # Increase from 15s
evaluation_interval: 30s
```

#### 2. Optimize Retention
```yaml
# In docker-compose
command:
  - '--storage.tsdb.retention.time=7d'  # Reduce from 30d
  - '--storage.tsdb.retention.size=10GB'
```

#### 3. Filter Unnecessary Metrics
```yaml
# In prometheus.yml
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'unwanted_metric_.*'
    action: drop
```

## 🚀 Advanced Features

### 1. Custom Alerting Webhook

```python
# alert_webhook.py
from flask import Flask, request, jsonify
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/alerts', methods=['POST'])
def handle_alert():
    """Handle incoming alerts from AlertManager"""
    try:
        data = request.get_json()
        
        for alert in data.get('alerts', []):
            alert_name = alert.get('labels', {}).get('alertname')
            status = alert.get('status')
            summary = alert.get('annotations', {}).get('summary')
            
            logging.info(f"Alert: {alert_name} - Status: {status} - {summary}")
            
            # Add custom alert handling logic here
            # - Send to Slack/Discord
            # - Create tickets
            # - Auto-remediation
            
        return jsonify({"status": "success"})
        
    except Exception as e:
        logging.error(f"Error handling alert: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

### 2. Automated Scaling

```python
# auto_scaler.py
import requests
import time
import logging
from typing import Dict, Any

class AIServiceAutoScaler:
    """Auto-scale AI services based on metrics"""
    
    def __init__(self, prometheus_url="http://localhost:9090"):
        self.prometheus_url = prometheus_url
        self.scaling_rules = {
            "ollama": {
                "cpu_threshold": 80,
                "memory_threshold": 85,
                "queue_threshold": 50
            }
        }
    
    def get_metric_value(self, query: str) -> float:
        """Get metric value from Prometheus"""
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("data", {}).get("result", [])
                
                if result:
                    return float(result[0]["value"][1])
                    
            return 0.0
            
        except Exception as e:
            logging.error(f"Error getting metric {query}: {e}")
            return 0.0
    
    def check_scaling_conditions(self, service: str) -> Dict[str, Any]:
        """Check if service needs scaling"""
        rules = self.scaling_rules.get(service, {})
        
        cpu_usage = self.get_metric_value(
            f'100 - (avg(rate(node_cpu_seconds_total{{mode="idle"}}[5m])) * 100)'
        )
        
        memory_usage = self.get_metric_value(
            f'(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100'
        )
        
        queue_size = self.get_metric_value(f'ai_queue_size{{service="{service}"}}')
        
        should_scale = (
            cpu_usage > rules.get("cpu_threshold", 80) or
            memory_usage > rules.get("memory_threshold", 85) or
            queue_size > rules.get("queue_threshold", 50)
        )
        
        return {
            "should_scale": should_scale,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "queue_size": queue_size,
            "thresholds": rules
        }
    
    def scale_service(self, service: str, action: str):
        """Scale service up or down"""
        if action == "up":
            logging.info(f"Scaling up {service}")
            # Implement scaling logic (Docker Swarm, Kubernetes, etc.)
        elif action == "down":
            logging.info(f"Scaling down {service}")
            # Implement scaling logic
    
    def run_autoscaler(self):
        """Run auto-scaling loop"""
        while True:
            try:
                for service in self.scaling_rules.keys():
                    conditions = self.check_scaling_conditions(service)
                    
                    if conditions["should_scale"]:
                        self.scale_service(service, "up")
                    
                    logging.info(f"Service {service}: {conditions}")
                
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logging.info("Auto-scaler stopped")
                break
            except Exception as e:
                logging.error(f"Auto-scaler error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    scaler = AIServiceAutoScaler()
    scaler.run_autoscaler()
```

## 📈 Next Steps

1. **Explore Advanced Dashboards**: Create service-specific dashboards
2. **Implement Custom Alerts**: Add business-logic alerts
3. **Add Log Aggregation**: Integrate ELK stack or Loki
4. **Performance Optimization**: Tune retention and collection
5. **Automated Remediation**: Build self-healing systems

## 🎓 Learning Resources

### Official Documentation
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [AlertManager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)

### Repository Examples
- [Monitoring Scripts](scripts/setup_monitoring.sh)
- [Custom Metrics](llmstack/monitoring/metrics.py)

---

**📊 Your AI automation tools are now fully monitored and observable!**

Track performance, identify issues, and optimize your AI infrastructure with comprehensive monitoring.