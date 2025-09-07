# Monitoring Stack Setup for Windows
Write-Host "Setting up Monitoring with Prometheus and Grafana..." -ForegroundColor Green

$LLMSTACK_HOME = "C:\Users\scarm\llmstack"
$monitoringPath = "$LLMSTACK_HOME\monitoring"

New-Item -Path $monitoringPath -ItemType Directory -Force | Out-Null
Set-Location $monitoringPath

# Create docker-compose for monitoring
$dockerCompose = @"
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
"@

$dockerCompose | Out-File -FilePath "docker-compose.yml" -Encoding UTF8

# Create Prometheus configuration
$prometheusConfig = @"
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'llmstack'
    static_configs:
      - targets: ['host.docker.internal:3000']
  
  - job_name: 'ollama'
    static_configs:
      - targets: ['host.docker.internal:11434']
  
  - job_name: 'flowise'
    static_configs:
      - targets: ['host.docker.internal:3001']
"@

$prometheusConfig | Out-File -FilePath "prometheus.yml" -Encoding UTF8

# Start monitoring stack
Write-Host "Starting monitoring stack..." -ForegroundColor Yellow
docker compose up -d

Write-Host "`nMonitoring setup complete!" -ForegroundColor Green
Write-Host "Access points:" -ForegroundColor Cyan
Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "  Grafana: http://localhost:3003 (admin/admin)" -ForegroundColor White