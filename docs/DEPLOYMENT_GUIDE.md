# Enhanced AI Swarm Intelligence Deployment Guide

This guide covers the deployment of the enhanced AI Swarm Intelligence system with comprehensive error handling, failover capabilities, and monitoring.

## Overview

The enhanced system includes:
- **Multiple AutoGPT instances** with automatic failover
- **Enhanced API Bridge** with circuit breakers and load balancing
- **Database Synchronization Layer** for distributed data consistency
- **Comprehensive Monitoring** with Prometheus, Grafana, and AlertManager
- **Load Balancing** with Nginx
- **Automated Backup Services**
- **Health Checking and Recovery**

## Prerequisites

### System Requirements
- **Docker**: Version 20.10+ with Docker Compose V2
- **Memory**: Minimum 16GB RAM (32GB recommended for production)
- **CPU**: 8+ cores (16+ cores recommended for production)
- **Storage**: 100GB+ free space (SSD recommended)
- **Network**: Stable internet connection for API calls

### API Keys Required
```bash
# Required API keys
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here

# Optional but recommended
PERPLEXITY_API_KEY=your_perplexity_key_here
GOOGLE_API_KEY=your_google_key_here

# Optional for backup
AWS_ACCESS_KEY_ID=your_aws_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
BACKUP_S3_BUCKET=your_backup_bucket_name
```

## Quick Start

### 1. Environment Setup
```bash
# Clone or copy the enhanced configuration files
mkdir -p swarm-intelligence/enhanced
cd swarm-intelligence/enhanced

# Copy the enhanced files
cp path/to/docker-compose.enhanced.yml ./docker-compose.yml
cp path/to/src/ai_platform/*.py ./src/ai_platform/
cp path/to/requirements-*.txt ./
cp path/to/*.conf ./config/
```

### 2. Create Environment File
```bash
cat > .env << EOF
# Core API Keys (REQUIRED)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here

# Optional API Keys
PERPLEXITY_API_KEY=your_perplexity_key_here
GOOGLE_API_KEY=your_google_key_here

# Security Settings
GRAFANA_PASSWORD=secure_admin_password
REDIS_PASSWORD=secure_redis_password
GRAFANA_SECRET_KEY=your_grafana_secret_key

# Backup Settings (Optional)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
BACKUP_S3_BUCKET=your_backup_bucket

# Notification Settings (Optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url
EOF
```

### 3. Create Required Directories
```bash
mkdir -p {data,logs,backups,config,monitoring}
mkdir -p data/{redis,prometheus,grafana,alertmanager}
mkdir -p agents/autogpt/{workspace,workspace-secondary,workspace-fallback}
mkdir -p agents/autogpt/{logs,logs-secondary,logs-fallback}
mkdir -p monitoring/{grafana/dashboards,rules}
```

### 4. Deploy the Enhanced System
```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f --tail=50
```

## Service Architecture

### Core Services
- **swarm-api** (Port 8001): Primary Swarm API with enhanced error handling
- **api-bridge** (Port 8002): Enhanced API bridge with failover capabilities
- **autogpt-primary** (Port 3000): Primary AutoGPT instance
- **autogpt-secondary** (Port 3001): Secondary AutoGPT instance (backup)
- **autogpt-fallback** (Port 3002): Minimal AutoGPT instance (emergency)
- **database-sync**: Database synchronization service
- **queen**: Enhanced Queen agent with error recovery

### Monitoring Stack
- **prometheus** (Port 9090): Metrics collection and alerting
- **grafana** (Port 3001): Visualization and dashboards
- **alertmanager** (Port 9093): Alert routing and notification
- **node-exporter** (Port 9100): System metrics collection

### Supporting Services
- **nginx-loadbalancer** (Port 80/443): Load balancing and SSL termination
- **redis** (Port 6379): Distributed caching and session storage
- **integration-validator**: Continuous system validation
- **backup-service**: Automated data backup

## Health Monitoring

### Service Health Endpoints
```bash
# Check individual service health
curl http://localhost:8001/health          # Swarm API
curl http://localhost:8002/health          # API Bridge
curl http://localhost:3000/health          # AutoGPT Primary
curl http://localhost:80/nginx-health      # Nginx Load Balancer

# Check overall system health
curl http://localhost:8002/endpoints       # All endpoints status
```

### Monitoring Dashboards
- **Grafana**: http://localhost:3001 (admin/your_password)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093

### Key Metrics to Monitor
- **Response Time**: API response times across all services
- **Error Rate**: 4xx/5xx error rates
- **Circuit Breaker Status**: Open/closed circuit breaker states
- **Database Sync Status**: Synchronization lag and conflicts
- **Resource Usage**: CPU, memory, and disk usage
- **Task Success Rate**: Percentage of successful task completions

## Failover Mechanisms

### AutoGPT Failover Chain
1. **Primary** (autogpt-primary): Main instance with full capabilities
2. **Secondary** (autogpt-secondary): Standby instance, activated on primary failure
3. **Fallback** (autogpt-fallback): Minimal instance for emergency operation

### API Bridge Failover
- **Circuit Breakers**: Automatically isolate failing services
- **Retry Logic**: Exponential backoff with maximum retry limits
- **Load Balancing**: Distribute requests across healthy instances
- **Health Monitoring**: Continuous endpoint health checking

### Database Synchronization
- **Conflict Resolution**: Automatic conflict resolution strategies
- **Data Integrity**: Hash-based change detection
- **Backup Recovery**: Automatic backup and restore capabilities
- **Multi-Node Sync**: Distributed synchronization across nodes

## Production Deployment

### Scaling Configuration
```yaml
# In docker-compose.yml, adjust resource limits:
deploy:
  resources:
    limits:
      memory: 8G      # Increase for production
      cpus: '4'       # Increase based on load
    reservations:
      memory: 2G
      cpus: '1'
```

### Security Hardening
1. **SSL/TLS**: Configure SSL certificates in nginx
2. **API Keys**: Use Docker secrets for sensitive data
3. **Network Isolation**: Implement proper network segmentation
4. **Access Control**: Configure firewall rules
5. **Monitoring**: Set up comprehensive logging and alerting

### Backup Strategy
```bash
# Database backups (automated via backup-service)
# - Hourly snapshots with 24-hour retention
# - Daily backups with 30-day retention
# - Optional S3 upload for offsite storage

# Manual backup
docker exec swarm-backup-service python /app/backup.py --immediate
```

## Troubleshooting

### Common Issues

#### Service Startup Failures
```bash
# Check logs
docker-compose logs service_name

# Restart specific service
docker-compose restart service_name

# Check resource usage
docker stats
```

#### API Connection Issues
```bash
# Check network connectivity
docker-compose exec api-bridge ping autogpt-primary

# Check circuit breaker status
curl http://localhost:8002/admin/circuit-breakers

# Force recovery
curl -X POST http://localhost:8002/admin/recovery
```

#### Database Sync Issues
```bash
# Check sync status
docker-compose logs database-sync

# Force synchronization
docker-compose exec database-sync python database_sync_layer.py --force-sync

# Check database integrity
sqlite3 data/swarm_memory.db "PRAGMA integrity_check;"
```

### Recovery Procedures

#### Complete System Recovery
```bash
# Stop all services
docker-compose down

# Restore from backup
cp backups/latest_backup.db data/swarm_memory.db

# Start with validation
docker-compose up -d integration-validator
docker-compose up -d
```

#### Individual Service Recovery
```bash
# Restart failed service
docker-compose restart service_name

# Force failover (for AutoGPT)
curl -X POST http://localhost:8002/admin/failover

# Reset circuit breakers
curl -X POST http://localhost:8002/admin/reset-circuit-breaker
```

## Maintenance

### Regular Tasks
- **Weekly**: Review error logs and performance metrics
- **Monthly**: Update Docker images and security patches
- **Quarterly**: Review and update API keys
- **Semi-annually**: Review and optimize resource allocation

### Monitoring Alerts
Configure alerts for:
- High error rates (>5%)
- Slow response times (>30s)
- Circuit breaker trips
- Database sync failures
- Resource exhaustion (>80% CPU/Memory)

## Support

For issues and questions:
1. Check service logs: `docker-compose logs service_name`
2. Review health endpoints and metrics
3. Consult the troubleshooting guide above
4. Check system resources and network connectivity

## Advanced Configuration

### Custom Error Handling
Modify `error_handling.py` to customize:
- Retry strategies and backoff algorithms
- Circuit breaker thresholds and timeouts
- Logging levels and formats
- Recovery mechanisms

### Performance Tuning
Adjust configuration based on workload:
- Increase resource limits for high-throughput scenarios
- Tune database sync intervals for consistency vs. performance
- Configure circuit breaker thresholds based on SLA requirements
- Optimize load balancer settings for request distribution

This enhanced deployment provides enterprise-grade reliability, monitoring, and error recovery capabilities for the AI Swarm Intelligence system.