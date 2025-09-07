# Monitoring Your AI Stack

## Access Dashboards

### Grafana (Main Dashboard)
- **URL**: http://localhost:3003
- **Login**: admin / admin
- **Purpose**: Visualize metrics and create dashboards

### Prometheus (Metrics)
- **URL**: http://localhost:9090
- **Purpose**: Query raw metrics and alerts

## Setting Up Dashboards

### Step 1: Add Prometheus Data Source in Grafana
1. Open http://localhost:3003
2. Login with admin/admin
3. Go to Configuration → Data Sources
4. Click "Add data source"
5. Choose "Prometheus"
6. URL: `http://prometheus:9090`
7. Click "Save & Test"

### Step 2: Import Pre-built Dashboards

#### System Monitoring Dashboard
1. Click "+" → "Import"
2. Dashboard ID: `1860` (Node Exporter Full)
3. Select Prometheus data source
4. Click "Import"

#### Docker Monitoring
1. Import Dashboard ID: `893`
2. Monitor all containers

### Step 3: Create Custom AI Dashboard

1. Click "+" → "Create Dashboard"
2. Add panels for:

#### Panel 1: AI Model Request Rate
```promql
rate(ollama_request_total[5m])
```

#### Panel 2: Response Times
```promql
histogram_quantile(0.95, rate(ollama_request_duration_seconds_bucket[5m]))
```

#### Panel 3: Active Containers
```promql
count(container_last_seen{name=~"flowise|openhands|monitoring.*"})
```

#### Panel 4: Memory Usage
```promql
container_memory_usage_bytes{name=~"flowise|openhands"} / 1024 / 1024 / 1024
```

## Key Metrics to Monitor

### Ollama Metrics
```bash
# Check model loading times
curl http://localhost:11434/api/tags

# Monitor active models
curl http://localhost:11434/api/ps
```

### Container Health
```bash
# Check all containers
docker stats --no-stream

# Specific container logs
docker logs flowise --tail 100
docker logs openhands --tail 100
```

### System Resources
```promql
# CPU Usage
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory Usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk Usage
100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"})
```

## Creating Alerts

### In Prometheus (prometheus.yml)
```yaml
groups:
  - name: ai-stack
    rules:
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
        for: 5m
        annotations:
          summary: "High memory usage detected"
          
      - alert: ServiceDown
        expr: up{job=~"flowise|openhands|ollama"} == 0
        for: 1m
        annotations:
          summary: "Service {{ $labels.job }} is down"
          
      - alert: SlowResponse
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
        for: 5m
        annotations:
          summary: "Slow API responses detected"
```

## Performance Optimization Tips

### 1. Monitor Model Memory
```python
import psutil
import docker

def check_ai_resources():
    # System memory
    mem = psutil.virtual_memory()
    print(f"System Memory: {mem.percent}%")
    
    # Docker containers
    client = docker.from_env()
    for container in client.containers.list():
        stats = container.stats(stream=False)
        mem_usage = stats['memory_stats']['usage'] / 1024 / 1024 / 1024
        print(f"{container.name}: {mem_usage:.2f} GB")

check_ai_resources()
```

### 2. Track Model Performance
```python
import time
import requests

def benchmark_model(model, prompt, iterations=10):
    times = []
    for _ in range(iterations):
        start = time.time()
        response = requests.post(
            "http://localhost:11434/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100
            }
        )
        times.append(time.time() - start)
    
    print(f"Model: {model}")
    print(f"Avg Response Time: {sum(times)/len(times):.2f}s")
    print(f"Min: {min(times):.2f}s, Max: {max(times):.2f}s")

# Test different models
benchmark_model("llama3.1:8b", "Hello")
benchmark_model("deepseek-r1:8b", "Hello")
```

### 3. Resource Usage Query
```bash
# Real-time monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
    clear
    echo "=== AI Stack Monitor ==="
    echo
    echo "Docker Containers:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    echo
    echo "Ollama Models:"
    curl -s http://localhost:11434/api/ps | jq '.models[].name' 2>/dev/null || echo "No active models"
    echo
    echo "Port Status:"
    netstat -tuln | grep -E ":(3001|3002|3003|9090|11434)"
    sleep 5
done
EOF

chmod +x monitor.sh
./monitor.sh
```

## Troubleshooting Guide

### Service Not Responding
```bash
# Check container status
docker ps -a

# Restart service
docker restart flowise
docker restart openhands

# Check logs
docker logs flowise --tail 50
```

### High Memory Usage
```bash
# Unload unused models
curl -X DELETE http://localhost:11434/api/models/unused-model

# Clear Docker cache
docker system prune -a

# Restart Ollama
systemctl restart ollama  # Linux
# or just restart the Ollama app on Windows
```

### Slow Responses
```bash
# Check active models
curl http://localhost:11434/api/ps

# Use smaller models
ollama run llama3.2:3b  # Instead of larger models

# Reduce context size
echo '{"num_ctx": 2048}' > ~/.ollama/config.json
```