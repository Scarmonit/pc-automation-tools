# 🛠️ Comprehensive Troubleshooting Guide

This guide helps you diagnose and resolve common issues with your AI automation tools setup. Follow the systematic approach to quickly identify and fix problems.

## 🚀 Quick Diagnostic

### One-Command Health Check
```bash
# Run comprehensive system check
bash scripts/troubleshoot.sh

# Or use the Python diagnostics
python3 scripts/troubleshoot.py --all
```

### Manual Quick Check
```bash
# Check all services status
docker ps
curl http://localhost:11434/api/version  # Ollama
curl http://localhost:3001/health        # Flowise
curl http://localhost:3002/health        # OpenHands
curl http://localhost:3003/api/health    # Grafana
```

## 📋 Common Issue Categories

1. [🔧 Installation Issues](#installation-issues)
2. [🐳 Docker & Container Issues](#docker--container-issues)
3. [🧠 AI Model Issues](#ai-model-issues)
4. [🌐 Network & Connectivity Issues](#network--connectivity-issues)
5. [💾 Resource & Performance Issues](#resource--performance-issues)
6. [🔒 Security & Permissions Issues](#security--permissions-issues)
7. [📊 Monitoring & Metrics Issues](#monitoring--metrics-issues)

## 🔧 Installation Issues

### Python Package Conflicts

**Symptoms:**
- Import errors for AI frameworks
- Version conflicts between packages
- Module not found errors

**Solutions:**
```bash
# Create clean virtual environment
python3 -m venv venv_ai_tools
source venv_ai_tools/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt

# For specific framework issues
pip uninstall autogen-agentchat
pip install --no-cache-dir pyautogen

# Check for conflicts
pip check
```

### Missing System Dependencies

**Symptoms:**
- Build failures during installation
- Missing headers or libraries
- Compilation errors

**Solutions:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y build-essential python3-dev python3-pip git curl

# macOS
brew install python git

# Install Docker if missing
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Permission Issues

**Symptoms:**
- Permission denied errors
- Cannot write to directories
- Docker socket access denied

**Solutions:**
```bash
# Fix Python package permissions
sudo chown -R $USER:$USER ~/.local/

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Fix directory permissions
sudo chown -R $USER:$USER $PWD
chmod +x scripts/*.sh
```

## 🐳 Docker & Container Issues

### Container Won't Start

**Symptoms:**
- Container exits immediately
- "Container is not running" errors
- Port binding failures

**Diagnosis:**
```bash
# Check container logs
docker logs container_name

# Check container status
docker ps -a

# Inspect container configuration
docker inspect container_name
```

**Solutions:**
```bash
# Common fixes
docker system prune -a  # Clean up
docker-compose down && docker-compose up -d

# Fix port conflicts
sudo netstat -tulpn | grep :3001
sudo kill -9 $(sudo lsof -t -i:3001)

# Fix volume permissions
sudo chown -R $USER:$USER ./data/
```

### Memory/Resource Issues

**Symptoms:**
- Container killed (OOMKilled)
- Slow performance
- Host system becomes unresponsive

**Solutions:**
```bash
# Check resource usage
docker stats

# Increase Docker memory limits
# Edit ~/.docker/daemon.json
{
  "default-runtime": "runc",
  "runtimes": {
    "runc": {
      "path": "runc"
    }
  },
  "storage-driver": "overlay2",
  "default-ulimits": {
    "memlock": {
      "Hard": -1,
      "Name": "memlock",
      "Soft": -1
    }
  }
}

# Restart Docker
sudo systemctl restart docker
```

### Network Issues

**Symptoms:**
- Services can't communicate
- Connection refused errors
- Timeout errors

**Solutions:**
```bash
# Check Docker networks
docker network ls
docker network inspect bridge

# Recreate network
docker-compose down
docker network prune
docker-compose up -d

# Use host networking if needed
docker run --network host image_name
```

## 🧠 AI Model Issues

### Ollama Model Problems

**Symptoms:**
- Model not found errors
- Slow model loading
- Out of memory errors

**Diagnosis:**
```bash
# Check Ollama status
curl http://localhost:11434/api/version

# List available models
ollama list

# Check model details
ollama show llama3.2

# Monitor resource usage
nvidia-smi  # For GPU
htop        # For CPU/Memory
```

**Solutions:**
```bash
# Pull missing models
ollama pull llama3.2
ollama pull mistral:7b
ollama pull codellama:7b

# Remove and re-pull corrupted models
ollama rm llama3.2
ollama pull llama3.2

# Use smaller models for limited resources
ollama pull llama3.2:1b  # Smaller version

# Configure Ollama memory settings
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS=*
export OLLAMA_MAX_LOADED_MODELS=2
```

### Model Performance Issues

**Symptoms:**
- Extremely slow responses
- High CPU/GPU usage
- Model crashes

**Solutions:**
```bash
# Monitor model performance
ollama ps

# Use appropriate model sizes
# For 8GB RAM: llama3.2:1b or llama3.2:3b
# For 16GB RAM: llama3.2:7b or mistral:7b
# For 32GB+ RAM: llama3.2:8b or larger models

# Optimize Ollama settings
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_QUEUE=4

# Use GPU acceleration if available
export CUDA_VISIBLE_DEVICES=0
```

### AutoGen Configuration Issues

**Symptoms:**
- Agent initialization failures
- API connection errors
- Conversation timeouts

**Solutions:**
```bash
# Check AutoGen configuration
cat ~/.autogen/config.json

# Create minimal working config
mkdir -p ~/.autogen
cat > ~/.autogen/config.json << EOF
{
  "model_list": [
    {
      "model": "llama3.2",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "api_type": "openai"
    }
  ]
}
EOF

# Test AutoGen connection
python3 -c "
import autogen
config = autogen.config_list_from_json('~/.autogen/config.json')
print('AutoGen config loaded:', len(config), 'models')
"
```

## 🌐 Network & Connectivity Issues

### Port Conflicts

**Symptoms:**
- "Port already in use" errors
- Services unreachable
- Connection refused

**Diagnosis:**
```bash
# Check port usage
sudo netstat -tulpn | grep :11434
sudo lsof -i :3001
ss -tulpn | grep :3002
```

**Solutions:**
```bash
# Kill processes using ports
sudo kill -9 $(sudo lsof -t -i:11434)

# Change port configurations
# Edit docker-compose.yml
ports:
  - "11435:11434"  # Use different host port

# Use alternative ports
export OLLAMA_HOST=0.0.0.0:11435
```

### Firewall Issues

**Symptoms:**
- External access blocked
- Services unreachable from other machines
- Timeout errors

**Solutions:**
```bash
# Ubuntu/Debian firewall
sudo ufw allow 11434/tcp
sudo ufw allow 3001/tcp
sudo ufw allow 3002/tcp
sudo ufw allow 3003/tcp

# CentOS/RHEL firewall
sudo firewall-cmd --permanent --add-port=11434/tcp
sudo firewall-cmd --permanent --add-port=3001-3003/tcp
sudo firewall-cmd --reload

# macOS firewall (if enabled)
# System Preferences > Security & Privacy > Firewall > Options
# Add Docker Desktop and allow incoming connections
```

### DNS Resolution Issues

**Symptoms:**
- Cannot resolve hostnames
- Intermittent connection failures

**Solutions:**
```bash
# Check DNS resolution
nslookup localhost
dig localhost

# Add to /etc/hosts if needed
echo "127.0.0.1 ollama.local flowise.local openhands.local" | sudo tee -a /etc/hosts

# Configure Docker DNS
# Edit ~/.docker/daemon.json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

## 💾 Resource & Performance Issues

### Memory Issues

**Symptoms:**
- Out of memory errors
- System freezing
- Processes being killed

**Diagnosis:**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10
docker stats --no-stream

# Check swap usage
swapon --show
```

**Solutions:**
```bash
# Add swap space (if none exists)
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Optimize memory settings
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf

# Use smaller models
ollama pull llama3.2:1b  # ~1.3GB instead of ~4.7GB
```

### CPU Performance Issues

**Symptoms:**
- High CPU usage
- Slow response times
- System lagging

**Solutions:**
```bash
# Check CPU usage
htop
top -p $(pgrep -d',' -f ollama)

# Limit CPU usage for containers
docker update --cpus="2.0" container_name

# Use CPU-appropriate models
# For 4 cores: llama3.2:1b or llama3.2:3b
# For 8+ cores: llama3.2:7b or mistral:7b

# Optimize Ollama threading
export OLLAMA_NUM_PARALLEL=2
export OMP_NUM_THREADS=4
```

### Disk Space Issues

**Symptoms:**
- "No space left on device" errors
- Docker build failures
- Model download failures

**Diagnosis:**
```bash
# Check disk usage
df -h
du -sh ~/.ollama/models/
docker system df
```

**Solutions:**
```bash
# Clean up Docker
docker system prune -a --volumes

# Clean up Ollama models
ollama list
ollama rm unused_model

# Clean up system
sudo apt autoremove
sudo apt autoclean

# Move Ollama models to larger disk
export OLLAMA_MODELS="/path/to/larger/disk/models"
```

## 🔒 Security & Permissions Issues

### File Permission Issues

**Symptoms:**
- Permission denied errors
- Cannot read/write files
- Script execution failures

**Solutions:**
```bash
# Fix script permissions
chmod +x scripts/*.sh

# Fix data directory permissions
sudo chown -R $USER:$USER ./data/
chmod -R 755 ./data/

# Fix Python package permissions
sudo chown -R $USER:$USER ~/.local/
```

### Docker Permission Issues

**Symptoms:**
- Cannot connect to Docker socket
- Permission denied for Docker commands

**Solutions:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock

# Restart Docker service
sudo systemctl restart docker
```

### API Key Issues

**Symptoms:**
- Authentication failures
- API access denied
- Invalid key errors

**Solutions:**
```bash
# Set environment variables
export OPENAI_API_KEY="ollama"
export OPENAI_API_BASE="http://localhost:11434/v1"

# For LocalAI
export OPENAI_API_KEY="sk-localai"
export OPENAI_API_BASE="http://localhost:8080/v1"

# Verify environment
env | grep -E "(OPENAI|OLLAMA)"
```

## 📊 Monitoring & Metrics Issues

### Prometheus Not Collecting Metrics

**Symptoms:**
- Missing metrics in Grafana
- Prometheus targets down
- No data in dashboards

**Diagnosis:**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check metrics availability
curl http://localhost:8080/metrics

# Verify Prometheus config
docker exec prometheus promtool check config /etc/prometheus/prometheus.yml
```

**Solutions:**
```bash
# Restart Prometheus
docker restart prometheus

# Fix configuration
cp prometheus.yml /path/to/prometheus/config/
docker exec prometheus kill -HUP 1

# Check network connectivity
docker exec prometheus wget -qO- http://host.docker.internal:8080/metrics
```

### Grafana Dashboard Issues

**Symptoms:**
- Dashboards not loading
- No data displayed
- Connection errors

**Solutions:**
```bash
# Check Grafana datasource
curl -u admin:admin http://localhost:3003/api/datasources

# Reset Grafana admin password
docker exec grafana grafana-cli admin reset-admin-password admin

# Import dashboard manually
curl -X POST \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d @dashboard.json \
  http://localhost:3003/api/dashboards/db
```

## 🧪 Systematic Diagnostic Process

### 1. Initial Assessment

```bash
#!/bin/bash
# quick_diagnosis.sh

echo "=== AI Tools Quick Diagnosis ==="

# Check Docker
echo "Checking Docker..."
docker --version && echo "✓ Docker installed" || echo "✗ Docker not installed"
docker ps > /dev/null 2>&1 && echo "✓ Docker running" || echo "✗ Docker not running"

# Check services
echo "Checking AI services..."
curl -s http://localhost:11434/api/version > /dev/null && echo "✓ Ollama running" || echo "✗ Ollama not running"
curl -s http://localhost:3001/health > /dev/null && echo "✓ Flowise running" || echo "✗ Flowise not running"
curl -s http://localhost:3002/health > /dev/null && echo "✓ OpenHands running" || echo "✗ OpenHands not running"

# Check resources
echo "Checking system resources..."
free -h | grep "Mem:" | awk '{print "Memory: " $3 "/" $2 " (" $3/$2*100 "%)"}'
df -h | grep "/$" | awk '{print "Disk: " $3 "/" $2 " (" $5 ")"}'

# Check models
echo "Checking AI models..."
ollama list 2>/dev/null | grep -v "NAME" | wc -l | awk '{print "Ollama models: " $1}'
```

### 2. Deep Diagnostics

```python
#!/usr/bin/env python3
# deep_diagnostics.py

import subprocess
import requests
import json
import sys
from pathlib import Path

class SystemDiagnostics:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.success = []
    
    def check_python_environment(self):
        """Check Python and package installations"""
        try:
            import autogen
            self.success.append("AutoGen installed")
        except ImportError:
            self.issues.append("AutoGen not installed")
        
        try:
            import memgpt
            self.success.append("MemGPT installed")
        except ImportError:
            self.warnings.append("MemGPT not installed")
        
        # Check Python version
        if sys.version_info >= (3, 8):
            self.success.append(f"Python {sys.version_info.major}.{sys.version_info.minor} compatible")
        else:
            self.issues.append(f"Python {sys.version_info.major}.{sys.version_info.minor} too old")
    
    def check_services(self):
        """Check AI service health"""
        services = {
            "Ollama": "http://localhost:11434/api/version",
            "Flowise": "http://localhost:3001/health",
            "OpenHands": "http://localhost:3002/health",
            "Grafana": "http://localhost:3003/api/health"
        }
        
        for service, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.success.append(f"{service} healthy")
                else:
                    self.warnings.append(f"{service} responding but unhealthy")
            except requests.exceptions.ConnectionError:
                self.issues.append(f"{service} not responding")
            except Exception as e:
                self.warnings.append(f"{service} check failed: {e}")
    
    def check_models(self):
        """Check available AI models"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                models = result.stdout.strip().split('\n')[1:]  # Skip header
                if models and models[0]:
                    self.success.append(f"Ollama has {len(models)} models")
                else:
                    self.warnings.append("No Ollama models installed")
            else:
                self.issues.append("Cannot list Ollama models")
        except FileNotFoundError:
            self.issues.append("Ollama command not found")
    
    def check_configuration(self):
        """Check configuration files"""
        config_files = [
            "~/.autogen/config.json",
            "~/.aider.conf.yml",
            "prometheus.yml",
            "docker-compose.yml"
        ]
        
        for config_file in config_files:
            path = Path(config_file).expanduser()
            if path.exists():
                self.success.append(f"Config found: {config_file}")
            else:
                self.warnings.append(f"Config missing: {config_file}")
    
    def run_full_diagnostic(self):
        """Run complete diagnostic"""
        print("Running comprehensive diagnostics...")
        
        self.check_python_environment()
        self.check_services()
        self.check_models()
        self.check_configuration()
        
        # Print results
        print("\n✅ SUCCESS:")
        for item in self.success:
            print(f"  ✓ {item}")
        
        print("\n⚠️  WARNINGS:")
        for item in self.warnings:
            print(f"  ⚠ {item}")
        
        print("\n❌ ISSUES:")
        for item in self.issues:
            print(f"  ✗ {item}")
        
        if not self.issues:
            print("\n🎉 All critical systems operational!")
            return True
        else:
            print(f"\n🔧 Found {len(self.issues)} critical issues to resolve")
            return False

if __name__ == "__main__":
    diagnostics = SystemDiagnostics()
    success = diagnostics.run_full_diagnostic()
    sys.exit(0 if success else 1)
```

## 🔄 Automated Recovery Scripts

### Service Recovery Script

```bash
#!/bin/bash
# auto_recovery.sh

echo "Starting automated recovery process..."

# Function to restart service
restart_service() {
    service_name=$1
    echo "Restarting $service_name..."
    
    case $service_name in
        "ollama")
            docker restart ollama 2>/dev/null || ollama serve &
            ;;
        "flowise")
            docker restart flowise 2>/dev/null || docker-compose up -d flowise
            ;;
        "openhands")
            docker restart openhands 2>/dev/null || docker-compose up -d openhands
            ;;
        *)
            echo "Unknown service: $service_name"
            ;;
    esac
    
    # Wait and check
    sleep 10
    
    case $service_name in
        "ollama")
            curl -s http://localhost:11434/api/version >/dev/null && echo "✓ $service_name recovered" || echo "✗ $service_name still down"
            ;;
        "flowise")
            curl -s http://localhost:3001/health >/dev/null && echo "✓ $service_name recovered" || echo "✗ $service_name still down"
            ;;
        "openhands")
            curl -s http://localhost:3002/health >/dev/null && echo "✓ $service_name recovered" || echo "✗ $service_name still down"
            ;;
    esac
}

# Check and recover services
services=("ollama" "flowise" "openhands")

for service in "${services[@]}"; do
    case $service in
        "ollama")
            curl -s http://localhost:11434/api/version >/dev/null || restart_service $service
            ;;
        "flowise")
            curl -s http://localhost:3001/health >/dev/null || restart_service $service
            ;;
        "openhands")
            curl -s http://localhost:3002/health >/dev/null || restart_service $service
            ;;
    esac
done

echo "Recovery process completed"
```

## 📞 Getting Help

### Community Resources
- **GitHub Issues**: [pc-automation-tools Issues](https://github.com/Scarmonit/pc-automation-tools/issues)
- **Documentation**: Check all guides in `docs/` directory
- **Examples**: Review working examples in `llmstack/examples/`

### Log Collection for Support
```bash
# Collect logs for support
mkdir -p support_logs
docker logs ollama > support_logs/ollama.log 2>&1
docker logs flowise > support_logs/flowise.log 2>&1
docker logs openhands > support_logs/openhands.log 2>&1
docker logs grafana > support_logs/grafana.log 2>&1
docker logs prometheus > support_logs/prometheus.log 2>&1

# System information
uname -a > support_logs/system_info.txt
docker --version >> support_logs/system_info.txt
python3 --version >> support_logs/system_info.txt
free -h >> support_logs/system_info.txt
df -h >> support_logs/system_info.txt

# Create archive
tar -czf support_logs_$(date +%Y%m%d_%H%M%S).tar.gz support_logs/
```

### Debug Mode Setup
```bash
# Enable debug logging
export DEBUG=1
export OLLAMA_DEBUG=1
export AUTOGEN_LOGGING_LEVEL=DEBUG

# Restart services with debug
docker-compose down
docker-compose up -d

# Monitor logs in real-time
docker-compose logs -f
```

---

**🛠️ Follow this systematic approach to quickly diagnose and resolve issues!**

Most problems have documented solutions above. If you encounter new issues, please contribute solutions back to help the community.