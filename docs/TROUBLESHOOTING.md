# 🔧 PC Automation Tools Troubleshooting Guide

Comprehensive troubleshooting guide for the PC Automation Tools repository covering common issues, diagnostics, and solutions.

## 🎯 Quick Diagnostics

### Health Check Command
```bash
# Run comprehensive health check
cd llmstack && python3 health_check.py

# Quick service status check
bash scripts/manage_services.sh status
```

### System Validation
```bash
# Check system requirements
bash scripts/check_system.sh

# Validate deployment
bash scripts/validate_deployment.sh
```

## 🚨 Common Issues & Solutions

### 1. Docker & Service Issues

#### **Problem**: Docker containers won't start
```bash
# Check Docker status
docker --version
systemctl status docker

# Solution: Restart Docker service
sudo systemctl restart docker
docker system prune -f
```

#### **Problem**: Port conflicts (3000, 3001, 3002, 11434)
```bash
# Check port usage
netstat -tulpn | grep -E ':(3000|3001|3002|11434)'

# Solution: Stop conflicting services
sudo fuser -k 3000/tcp
sudo fuser -k 3001/tcp
sudo fuser -k 3002/tcp
sudo fuser -k 11434/tcp
```

#### **Problem**: Container fails to start with permission errors
```bash
# Solution: Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo (not recommended for production)
sudo docker compose up -d
```

### 2. AI Model & Ollama Issues

#### **Problem**: Ollama not responding at localhost:11434
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Solution: Restart Ollama
killall ollama
bash install_ollama.sh
ollama serve &
```

#### **Problem**: Models not downloading or corrupted
```bash
# Clear Ollama cache
rm -rf ~/.ollama/models/*

# Re-download models
ollama pull llama3.2:3b
ollama pull mistral:7b
ollama pull codellama:7b
```

#### **Problem**: Out of memory when running models
```bash
# Check available memory
free -h
htop

# Solution: Use smaller models
ollama pull llama3.2:1b
ollama pull gemma:2b

# Or increase swap space
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 3. LLMStack & UI Issues

#### **Problem**: LLMStack UI not accessible at localhost:3000
```bash
# Check container logs
docker logs llmstack-ui

# Solution: Restart LLMStack
docker compose -f docker-compose.llmstack.yml restart
```

#### **Problem**: Database connection errors
```bash
# Check PostgreSQL container
docker logs llmstack-db

# Solution: Reset database
docker compose -f docker-compose.llmstack.yml down -v
docker compose -f docker-compose.llmstack.yml up -d
```

#### **Problem**: Provider configuration not saving
```bash
# Check admin token
grep ADMIN_TOKEN .env

# Solution: Generate new admin token
python3 scripts/configure_providers.py --generate-token
```

### 4. AI Agent Integration Issues

#### **Problem**: AutoGen agents not responding
```bash
# Check AutoGen configuration
cat ~/.autogen/config.json

# Solution: Update AutoGen config
python3 -c "
import json
config = {
    'model_list': [{
        'model': 'llama3.2',
        'base_url': 'http://localhost:11434/v1',
        'api_key': 'ollama',
        'api_type': 'openai'
    }]
}
with open('~/.autogen/config.json', 'w') as f:
    json.dump(config, f, indent=2)
"
```

#### **Problem**: Flowise workflows failing
```bash
# Check Flowise logs
docker logs flowise

# Solution: Reset Flowise database
docker compose -f docker-compose.flowise.yml down -v
rm -rf flowise_data/*
docker compose -f docker-compose.flowise.yml up -d
```

#### **Problem**: OpenHands not starting
```bash
# Check OpenHands configuration
docker logs openhands

# Solution: Update OpenHands image
docker pull ghcr.io/all-hands-ai/openhands:latest
docker compose -f docker-compose.openhands.yml up -d --force-recreate
```

### 5. GitHub Automation Issues

#### **Problem**: GitHub API rate limiting
```bash
# Check rate limit status
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/rate_limit

# Solution: Use GitHub App token or wait
export GITHUB_TOKEN="your_new_token_here"
```

#### **Problem**: Auto-submit failing
```bash
# Check GitHub token permissions
python3 -c "
import requests
headers = {'Authorization': f'token {os.getenv(\"GITHUB_TOKEN\")}'}
r = requests.get('https://api.github.com/user', headers=headers)
print(r.status_code, r.json())
"

# Solution: Update token scopes (repo, issues, pull_requests)
```

#### **Problem**: Merge automation not working
```bash
# Check git configuration
git config --list | grep user
git status

# Solution: Configure git
git config user.name "GitHub Actions"
git config user.email "actions@github.com"
```

### 6. Performance & Resource Issues

#### **Problem**: System running slowly
```bash
# Check system resources
htop
df -h
iotop

# Solution: Optimize Docker
docker system prune -a
docker volume prune

# Optimize models
ollama list
ollama rm unused_model_name
```

#### **Problem**: High CPU usage
```bash
# Identify resource-hungry processes
ps aux --sort=-%cpu | head -10

# Solution: Limit Docker CPU
echo 'DOCKER_OPTS="--cpu-period=100000 --cpu-quota=50000"' >> /etc/default/docker
systemctl restart docker
```

#### **Problem**: Disk space running low
```bash
# Check disk usage
du -h --max-depth=1 ~/.ollama/
du -h --max-depth=1 /var/lib/docker/

# Solution: Clean up
docker system prune -a --volumes
rm -rf ~/.ollama/models/unused_*
```

## 🔍 Advanced Diagnostics

### Network Connectivity Tests
```bash
# Test internal connectivity
curl -f http://localhost:3000/health || echo "LLMStack offline"
curl -f http://localhost:3001/api/v1/ping || echo "Flowise offline"  
curl -f http://localhost:11434/api/tags || echo "Ollama offline"

# Test external connectivity
curl -f https://api.github.com/zen || echo "GitHub unreachable"
curl -f https://registry.ollama.ai || echo "Ollama registry unreachable"
```

### Log Analysis
```bash
# Collect all logs
mkdir -p /tmp/debug-logs
docker logs llmstack-ui > /tmp/debug-logs/llmstack.log 2>&1
docker logs flowise > /tmp/debug-logs/flowise.log 2>&1
docker logs openhands > /tmp/debug-logs/openhands.log 2>&1
journalctl -u docker > /tmp/debug-logs/docker.log

# Analyze logs for errors
grep -i error /tmp/debug-logs/*.log
grep -i "connection refused" /tmp/debug-logs/*.log
```

### Configuration Validation
```bash
# Validate all config files
python3 -c "
import json, yaml
from pathlib import Path

configs = [
    ('autogen_config.json', json),
    ('ollama_config.json', json),
    ('continue_config.json', json),
    ('prometheus.yml', yaml),
]

for file, parser in configs:
    if Path(file).exists():
        try:
            with open(file) as f:
                parser.safe_load(f)
            print(f'✓ {file}')
        except Exception as e:
            print(f'✗ {file}: {e}')
    else:
        print(f'- {file}: not found')
"
```

## 🚀 Recovery Procedures

### Complete System Reset
```bash
# WARNING: This will remove all data
bash scripts/manage_services.sh stop
docker system prune -a --volumes
rm -rf ~/.ollama/models/*
rm -rf flowise_data/*
bash deploy.sh
```

### Selective Service Recovery
```bash
# Restart only failed services
docker compose -f docker-compose.llmstack.yml restart llmstack-ui
docker compose -f docker-compose.monitoring.yml restart prometheus grafana
```

### Emergency Rollback
```bash
# Rollback to last known good configuration
git log --oneline -10
git checkout HEAD~1 -- docker-compose.*.yml
docker compose down && docker compose up -d
```

## 📞 Getting Help

### Information to Collect
When reporting issues, please include:

```bash
# System information
uname -a
docker --version
python3 --version

# Service status
cd llmstack && python3 health_check.py > system-health.txt

# Recent logs (last 100 lines)
docker logs --tail=100 llmstack-ui > llmstack-recent.log
```

### Community Resources
- **Repository Issues**: [GitHub Issues](https://github.com/Scarmonit/pc-automation-tools/issues)
- **Documentation**: [Full Documentation](../README.md)
- **Configuration Guides**: [AI Agent Setup](../llmstack/README.md)

### Quick Support Commands
```bash
# Generate support bundle
bash scripts/generate_support_bundle.sh

# Test all components
bash scripts/validate_deployment.sh --verbose

# Performance benchmark
python3 scripts/benchmark_system.py --full-report
```

---

**💡 Pro Tip**: Run `cd llmstack && python3 health_check.py` regularly to catch issues early!

**⚠️ Remember**: Always backup your configurations before making major changes.