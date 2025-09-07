# LLMStack Open Source Deployment Instructions

**CRITICAL**: Always follow these instructions first and only fallback to additional search or bash commands if the information here is incomplete or found to be in error.

## Working Effectively

### Bootstrap and Environment Setup
- **Always run first**: `bash scripts/check_system.sh` to verify system requirements (takes ~0.1 seconds)
- **Install dependencies**: `pip3 install -r requirements.txt` -- takes 90-120 seconds, NEVER CANCEL
- **Fix line endings if needed**: `sed -i 's/\r$//' scripts/*.sh && chmod +x scripts/*.sh` (Windows line ending fix)
- **Verify installation**: `python3 llmstack/test_installations.py` (takes ~0.6 seconds)

### Build and Deploy Commands

#### Full Deployment (Complete System)
- **One-command deployment**: `bash deploy.sh` -- takes 15-45 minutes depending on network, NEVER CANCEL
- **Set timeout to 60+ minutes** for the full deployment command

#### Step-by-Step Deployment (Recommended for Development)
```bash
# Phase 1: System Check (0.1 seconds)
bash scripts/check_system.sh

# Phase 2: Install Local Model Servers (5-15 minutes each, NEVER CANCEL)
bash scripts/install_ollama.sh        # Downloads 2-4GB models
bash scripts/install_lm_studio.sh     # Downloads installer
bash scripts/setup_vllm.sh           # GPU acceleration setup

# Phase 3: Deploy LLMStack (10-20 minutes, NEVER CANCEL)
bash scripts/deploy_llmstack.sh      # Clones repo, builds Node.js client

# Phase 4: Install AI Agents (5-10 minutes total, NEVER CANCEL)
bash scripts/install_agents.sh       # AutoGen, Flowise, OpenHands
bash scripts/install_continue.sh     # VS Code extension
bash scripts/install_jan.sh         # Desktop app

# Phase 5: Configuration (2-5 minutes)
bash scripts/setup_monitoring.sh     # Grafana, Prometheus
bash scripts/optimize_system.sh      # Performance tuning

# Phase 6: Validation (1-2 minutes)
bash scripts/validate_deployment.sh  # Health checks
python3 scripts/benchmark_system.py  # Performance test
```

#### Using Makefile Commands
```bash
make help                    # Show all available commands
make check                   # System requirements (0.1 seconds)
make install                 # Install dependencies (90+ seconds, NEVER CANCEL)
make deploy                  # Full deployment (20-45 minutes, NEVER CANCEL)
make dev                     # Development environment (2-5 minutes)
make validate               # Deployment validation (1-2 minutes)
make benchmark              # Performance test (0.3 seconds if no services)
make clean                  # Cleanup containers (30 seconds)
```

### **CRITICAL TIMEOUT REQUIREMENTS**
- **NEVER CANCEL builds or deployments** - Set timeouts to 60+ minutes
- **System check**: 30 seconds timeout
- **Dependency installation**: 180 seconds timeout
- **Model downloads**: 1200+ seconds timeout (models are 2-4GB each)
- **Docker builds**: 900+ seconds timeout
- **Full deployment**: 3600+ seconds timeout (60 minutes)

## Testing and Validation

### Core Validation Steps
```bash
# Always run after making changes
bash scripts/validate_deployment.sh      # Takes 1-2 minutes
python3 scripts/benchmark_system.py      # Takes 0.3-30 seconds depending on services
```

### Manual Validation Scenarios
**ALWAYS test these scenarios after deployment changes:**

1. **System Health Check**:
   ```bash
   # All should show ✓ or ⚠ (warnings acceptable)
   bash scripts/check_system.sh
   ```

2. **Service Accessibility**:
   ```bash
   # Check each service endpoint (when services are running)
   curl -s http://localhost:3000/api/health    # LLMStack
   curl -s http://localhost:11434/api/tags     # Ollama
   curl -s http://localhost:3001               # Flowise
   curl -s http://localhost:3002/health        # OpenHands
   ```

3. **Model Inference Test** (when Ollama is running):
   ```bash
   curl -X POST http://localhost:11434/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model": "llama3.2:3b", "messages": [{"role": "user", "content": "Hello"}]}'
   ```

4. **Development Environment Test**:
   ```bash
   make dev  # Start development stack
   # Wait 2-5 minutes for services to start
   make validate
   ```

## Environment Limitations and Network Requirements

### What Works in All Environments
- ✅ System requirements checking
- ✅ Python dependency installation
- ✅ Local script execution
- ✅ Docker commands (docker --version, docker ps)
- ✅ File operations and basic validation
- ✅ Python framework testing

### What Requires Internet Access
- ❌ **Ollama installation fails** - requires ollama.com (blocked in some environments)
- ❌ **Model downloads fail** - requires model repositories
- ❌ **LLMStack Docker images** - may require docker login or repository access
- ✅ **GitHub, Docker Hub, PyPI** - generally accessible

### Environment-Specific Instructions

#### In Restricted Environments (No External Access)
```bash
# Document limitations but continue with what works
echo "❌ External downloads unavailable - Ollama installation will fail"
echo "❌ Model downloads unavailable - use pre-installed models if available"
echo "❌ Some Docker images may be unavailable"

# Focus on local development and testing
python3 llmstack/test_installations.py
bash scripts/check_system.sh
# Test local Python frameworks and scripts
```

#### In Full Network Environments
```bash
# Full deployment possible
bash deploy.sh
# Allow 45-60 minutes for complete setup
```

## Access Points and URLs

After successful deployment (when services are running):

### Main Applications
- **LLMStack UI**: http://localhost:3000
- **Flowise**: http://localhost:3001  
- **OpenHands**: http://localhost:3002

### Monitoring & Management
- **Grafana**: http://localhost:3003 (admin/admin)
- **Prometheus**: http://localhost:9090

### API Endpoints  
- **Ollama API**: http://localhost:11434/v1
- **LM Studio API**: http://localhost:1234/v1
- **vLLM API**: http://localhost:8000/v1

## Common Tasks and Expected Outputs

### Repository Structure (ls -la output)
```
.claude/              # Claude AI configuration
.env.example         # Environment template
.git/               # Git repository
.gitignore          # Git ignore file
Makefile           # Build commands
README.md          # Project documentation
ai-tools/          # Additional AI tools
apps/              # Production applications
config/            # Configuration files
llmstack/          # LLMStack examples and configs
requirements.txt   # Python dependencies
scripts/           # Deployment scripts
validate.sh        # Main validation script
```

### Key Scripts Directory (ls scripts/)
```
benchmark.sh            # Performance testing
check_system.sh        # System requirements
deploy_llmstack.sh     # Main LLMStack deployment
install_agents.sh      # AI agents installation
install_ollama.sh      # Ollama local models
validate_deployment.sh # Health checks
```

### Dependency Installation Output
```bash
pip3 install -r requirements.txt
# Installs ~50 packages including:
# - openai, anthropic (AI APIs)
# - aider-chat, pyautogen (AI tools)
# - pandas, numpy (data processing)
# - Takes 90-120 seconds, downloads ~200MB
```

## Troubleshooting

### Line Ending Issues (Windows)
```bash
# Fix CRLF line endings that cause script failures
sed -i 's/\r$//' scripts/*.sh
chmod +x scripts/*.sh
```

### Network Access Issues
```bash
# Test network connectivity
python3 -c "import requests; print(requests.get('https://github.com').status_code)"
# Expected: 200 for success, exception for network issues
```

### Docker Issues
```bash
# Check Docker daemon
docker ps
# Expected: Empty table if no containers, error if daemon down

# Clean up Docker if needed
docker system prune -a
```

### Disk Space Issues
```bash
# System check shows disk requirements
bash scripts/check_system.sh
# Expected: ✗ Need 50GB+ free disk (warning, not blocking)
```

## Key Project Information

### Project Purpose
Complete deployment system for LLMStack with 100% free/open source AI components. Provides local AI development environment with zero API costs and full data privacy.

### Main Components
- **LLMStack**: Web UI for AI app development
- **Ollama**: Local model inference (Llama, Mistral, CodeLlama)
- **AutoGen**: Multi-agent conversations
- **Flowise**: Visual AI workflow builder
- **OpenHands**: AI coding assistant
- **Aider**: AI pair programming

### Build Pattern
Shell scripts orchestrated through Makefile and deploy.sh, with Docker containers for services and local Python dependencies for tooling.

### Expected File Changes
When working on this repository, changes typically involve:
- Shell scripts in `scripts/` directory
- Configuration files in `config/`
- Docker compose files for service orchestration
- Python scripts for automation and testing

Always run `bash scripts/check_system.sh` and validate with `bash scripts/validate_deployment.sh` after making changes.

## Quick Validation Workflow

When services are NOT running (expected in development environments):
```bash
# These commands should work and complete quickly:
bash scripts/check_system.sh           # 0.02s - System requirements
python3 llmstack/test_installations.py # 0.57s - Python frameworks  
bash scripts/validate_deployment.sh    # 0.03s - Service health (will show errors)
python3 scripts/benchmark_system.py    # 0.24s - Performance test (no services)

# All commands should complete successfully even when reporting service errors
# This validates the tooling works correctly
```

When services ARE running (after successful deployment):
```bash
# These should show ✓ success indicators:
curl -s http://localhost:3000/api/health  # LLMStack health
curl -s http://localhost:11434/api/tags   # Ollama models
bash scripts/validate_deployment.sh      # All services healthy
```