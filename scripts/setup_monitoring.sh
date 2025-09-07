#!/bin/bash
# Setup monitoring stack with Prometheus and Grafana

echo "Setting up monitoring stack..."

# Create monitoring directory
mkdir -p ~/llmstack/monitoring

# Create monitoring docker-compose
cat > ~/llmstack/monitoring/docker-compose.yml << 'EOF'
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=7d'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3003:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=redis-datasource
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
EOF

# Create Prometheus config
cat > ~/llmstack/monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'llmstack'
    static_configs:
      - targets: ['host.docker.internal:3000']
  
  - job_name: 'ollama'
    static_configs:
      - targets: ['host.docker.internal:11434']
EOF

# Start monitoring
cd ~/llmstack/monitoring
docker compose up -d

echo "✓ Monitoring started"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3003 (admin/admin)"