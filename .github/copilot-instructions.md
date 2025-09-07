# LLMStack Open Source Deployment Repository

**ALWAYS follow these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

This repository is a comprehensive deployment and orchestration system for running LLMStack with 100% free and open source AI components. It provides scripts, configurations, and automation for deploying local AI models (Ollama, LM Studio, vLLM) and AI agents (AutoGen, Flowise, OpenHands, Aider) with zero API costs and full data privacy.

## Critical System Requirements

Run system requirements check FIRST:
```bash
./scripts/check_system.sh
```

**Minimum Requirements:**
- **CPU:** 4+ cores (validated automatically)
- **RAM:** 8GB+ minimum, 16GB+ recommended (validated automatically)
- **Storage:** 50GB+ free disk space (validated automatically)
- **GPU:** Optional but recommended for performance (4GB+ VRAM)
- **OS:** Linux, macOS, or Windows with WSL2
- **Docker:** Required for all containerized services
- **Python:** 3.12+ (validated automatically)

**CRITICAL:** The disk space check often fails in sandboxed environments. Document this as a known limitation when working in constrained environments.

## Working Effectively

### Bootstrap and Setup (VALIDATED)

**ALWAYS make scripts executable first:**
```bash
chmod +x scripts/*.sh *.sh
```

**Install Python dependencies - NEVER CANCEL (takes 2-3 minutes):**
```bash
python3 -m pip install -r requirements.txt
```
Set timeout to 300+ seconds. Successfully installs all required packages including autogen-agentchat, aider-chat, openai, anthropic, and testing frameworks.

**Validate system requirements:**
```bash
make check
# Alternative: ./scripts/check_system.sh
```
Takes ~5 seconds. Returns CPU/RAM/disk/GPU status with clear pass/fail indicators.

**Test framework installations:**
```bash
python3 llmstack/test_installations.py
```
Takes ~1 second. Shows which AI frameworks are properly installed vs missing.

### Main Deployment Commands

**CRITICAL LIMITATION:** External network access is blocked in many environments. Commands that download from external sources (ollama.com, GitHub releases, etc.) will fail with connection errors like "Could not resolve host: ollama.com".

**One-command deployment (NETWORK DEPENDENT):**
```bash
./deploy.sh
```
**NEVER CANCEL** - Full deployment takes 45-60 minutes. Set timeout to 4000+ seconds.
- Phase 1: Model servers (15-20 minutes)
- Phase 2: LLMStack deployment (10-15 minutes)  
- Phase 3: AI agents (15-20 minutes)
- Phase 4: Configuration (5-10 minutes)
- Phase 5: Validation (5 minutes)

**Individual component installation (NETWORK DEPENDENT):**
```bash
# Each of these requires external network access
./scripts/install_ollama.sh        # Downloads from ollama.com
./scripts/install_lm_studio.sh     # Downloads AppImage
./scripts/deploy_llmstack.sh       # Clones GitHub repository
./scripts/install_agents.sh        # Downloads Docker images
```

### Service Management (VALIDATED)

**Start/stop services:**
```bash
./scripts/manage_services.sh start    # Takes 30-60 seconds
./scripts/manage_services.sh stop     # Takes 10-15 seconds  
./scripts/manage_services.sh status   # Takes 5-10 seconds
./scripts/manage_services.sh logs     # Immediate
```

**Using Makefile (VALIDATED):**
```bash
make help                           # Shows all commands (~1 second)
make check                         # System requirements (~5 seconds)
make start                         # Start services (~30-60 seconds)
make stop                          # Stop services (~10-15 seconds)
make logs                          # Show logs (immediate)
make clean                         # Cleanup (~30 seconds)
```

### Docker Compose Operations

**Validate configurations (VALIDATED):**
```bash
docker compose -f docker-compose.development.yml config
```
Takes ~5 seconds. Shows parsed configuration and detects syntax errors.

**LIMITATION:** Actual Docker container startup fails due to missing images (trypromptly/llmstack repository access denied).

## Testing and Validation

## Manual Validation Scenarios for AI Components

**After making changes to the repository, ALWAYS manually test these specific scenarios:**

### 1. Complete System Bootstrap Test
```bash
# Verify fresh clone setup (simulate new developer)
chmod +x scripts/*.sh *.sh                                    # ~1 second
python3 -m pip install -r requirements.txt                    # ~180 seconds, NEVER CANCEL
./scripts/check_system.sh                                     # ~5 seconds
make check                                                     # ~5 seconds
python3 llmstack/test_installations.py                        # ~1 second
```

### 2. Configuration Syntax Validation  
```bash
# Test all Docker Compose files can be parsed correctly
docker compose -f docker-compose.development.yml config       # ~5 seconds
docker compose -f docker-compose.monitoring.yml config        # ~5 seconds
docker compose -f docker-compose.vllm.yml config             # ~5 seconds
```

### 3. Working Service Deployment Test
```bash
# Deploy actual working services and verify functionality
docker compose -f docker-compose.monitoring.yml up -d         # ~60 seconds first time
sleep 10                                                       # Wait for startup
curl -s http://localhost:9090/api/v1/status/config           # Verify Prometheus API
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" # Check containers
docker compose -f docker-compose.monitoring.yml down          # ~10 seconds cleanup
```

### 4. Script Functionality Test
```bash
# Verify all key scripts execute without syntax errors
./scripts/manage_services.sh status                          # ~10 seconds
./validate.sh                                               # ~30 seconds (expect 7 errors)
python3 scripts/benchmark_system.py                         # ~60 seconds (expect no benchmarks)
```

### 5. Python Environment Integrity
```bash
# Test core imports work correctly
python3 -c "import openai, anthropic, requests; print('Core OK')"      # ~1 second
python3 -c "import pandas, numpy; print('Data processing OK')"         # ~2 seconds  
python3 -c "import pytest; print('Testing framework OK')"              # ~1 second
```

### Expected Manual Validation Results
- **System requirements**: CPU/RAM pass, GPU optional warning, disk may fail (environment dependent)
- **Configuration parsing**: All Docker Compose files validate successfully
- **Monitoring deployment**: Prometheus starts successfully on port 9090, API responds
- **Script execution**: All scripts run without syntax errors
- **Import tests**: Core Python dependencies import successfully
- **Service validation**: Expected failures for Ollama, LLMStack (network dependent services)

**Any deviation from these expected results indicates a problem that must be investigated.**

**Expected results in sandbox environment:**
- System check: CPU/RAM pass, GPU warning, disk may fail
- Framework test: OpenAI/Requests pass, others may fail  
- Service status: All offline (expected without deployment)
- Validation: 7 errors expected (services not running)
- Benchmark: No successful benchmarks (services offline)
- **Docker monitoring**: Prometheus/Grafana CAN be deployed and accessed successfully

### Working Validation Scenarios

**ALWAYS test these specific scenarios after making changes:**

1. **Configuration Validation (VALIDATED - all pass):**
   ```bash
   # Test Docker Compose syntax - all configurations are valid
   docker compose -f docker-compose.development.yml config     # ~5 seconds
   docker compose -f docker-compose.monitoring.yml config      # ~5 seconds  
   docker compose -f docker-compose.vllm.yml config           # ~5 seconds
   ```

2. **Script Execution (VALIDATED):**
   ```bash
   # Test all scripts can execute without syntax errors
   ./scripts/check_system.sh                    # ~5 seconds
   ./scripts/manage_services.sh status          # ~10 seconds
   ./validate.sh                               # ~30 seconds
   ```

3. **Python Environment (VALIDATED):**
   ```bash
   # Verify Python dependencies work (~1 second each)
   python3 -c "import openai, anthropic, requests; print('Core imports OK')"
   python3 llmstack/test_installations.py
   ```

4. **Docker Functionality (VALIDATED):**
   ```bash
   # Verify Docker works
   docker --version                            # Immediate
   docker compose version                      # Immediate
   docker run hello-world                      # ~30 seconds (pulls image)
   ```

5. **Working Service Deployment (VALIDATED):**
   ```bash
   # Monitoring services CAN be deployed successfully
   docker compose -f docker-compose.monitoring.yml up -d    # ~60 seconds (pulls images)
   
   # Verify services are running
   docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
   curl -s http://localhost:9090/api/v1/status/config       # Test Prometheus
   
   # Clean up when done
   docker compose -f docker-compose.monitoring.yml down     # ~10 seconds
   ```

## Critical Timing and Timeout Requirements

**NEVER CANCEL these operations - this repository is DEPLOYMENT focused, not traditional building:**

### Long-Running Operations (NEVER CANCEL)
- **pip install**: 300+ seconds (2-3 minutes for full dependencies)
- **Docker image pulls**: 1800+ seconds (30+ minutes for large AI images)
- **Full deployment**: 4000+ seconds (60+ minutes end-to-end)
- **Model downloads**: 3600+ seconds (60+ minutes for 7B models)
- **Service startup**: 180+ seconds (3+ minutes for all containers)

### Medium Duration Operations 
- **Docker Compose pull**: 120+ seconds (2+ minutes for multiple images)
- **Monitoring deployment**: 60+ seconds (1+ minute first time)
- **Container startup**: 30+ seconds (varies by service)

### Quick Operations (under 30 seconds)
- **System requirements check**: ~5 seconds
- **Configuration validation**: ~5 seconds  
- **Framework import tests**: ~1 second
- **Service status checks**: ~10 seconds
- **Script execution**: ~5-30 seconds depending on complexity

**IMPORTANT:** This is primarily a DEPLOYMENT and ORCHESTRATION repository. There is no traditional "build" process like compiling code. The main "build" activities are:
1. Installing dependencies (`pip install`)
2. Pulling Docker images (`docker compose pull`)
3. Starting services (`docker compose up`)
4. Downloading AI models (Ollama/LM Studio)

## Known Limitations and Workarounds

### Network Access Issues
- **Problem:** External downloads fail in sandboxed environments
- **Symptoms:** "Could not resolve host", "connection refused"
- **Workaround:** Document as expected limitation, focus on configuration validation
- **Commands affected:** All install_*.sh scripts, deploy.sh, Docker pulls

### Docker Image Access
- **Problem:** trypromptly/llmstack image access denied  
- **Symptoms:** "pull access denied for trypromptly/llmstack"
- **Workaround:** Use monitoring services for testing (these work), avoid main LLMStack deployment
- **Working alternative:** `docker compose -f docker-compose.monitoring.yml up -d` 
- **Commands affected:** make dev, main docker-compose.development.yml

### Resource Constraints  
- **Problem:** Insufficient disk space in sandbox (27GB available, 50GB required)
- **Symptoms:** Disk check fails in system requirements
- **Workaround:** Document as environmental limitation
- **Impact:** Model downloads and container storage

## Directory Structure and Key Files

```
.
├── deploy.sh                  # Main deployment script (NETWORK DEPENDENT)
├── Makefile                   # Common commands (VALIDATED)
├── requirements.txt           # Python dependencies (VALIDATED)
├── scripts/                   # Core deployment scripts
│   ├── check_system.sh       # System requirements (VALIDATED)
│   ├── manage_services.sh    # Service control (VALIDATED)
│   ├── install_*.sh          # Component installers (NETWORK DEPENDENT)
│   ├── benchmark.sh          # Performance testing (VALIDATED)
│   └── validate_deployment.sh # Full validation (VALIDATED)
├── docker-compose.*.yml      # Service configurations (VALIDATED)
├── llmstack/                 # Examples and test scripts
│   ├── test_installations.py # Framework validation (VALIDATED)
│   └── src/tests/           # Additional test scripts
└── config/                   # Configuration files
```

## Troubleshooting Common Issues

**Script permission errors:**
```bash
chmod +x scripts/*.sh *.sh
```

**Python import errors:**
```bash
python3 -m pip install -r requirements.txt --user
```

**Docker access issues:**
```bash
# Check Docker daemon
docker --version
docker compose version

# Test basic functionality  
docker run hello-world
```

**Service connection failures:**
```bash
# Expected in sandbox - all services will be offline
./scripts/manage_services.sh status
```

## Access Points (When Deployed)

After successful deployment in a real environment:

### Main Applications
- **LLMStack UI:** http://localhost:3000
- **Flowise:** http://localhost:3001
- **OpenHands:** http://localhost:3002

### Monitoring & Management  
- **Grafana:** http://localhost:3003 (admin/admin)
- **Prometheus:** http://localhost:9090

### API Endpoints
- **Ollama API:** http://localhost:11434/v1
- **LM Studio API:** http://localhost:1234/v1
- **vLLM API:** http://localhost:8000/v1

## Development Workflow

**Before making changes:**
1. Run `./scripts/check_system.sh`
2. Verify `python3 -m pip install -r requirements.txt` 
3. Test `python3 llmstack/test_installations.py`

**After making changes:**
1. Run `make check` to validate system
2. Test configuration: `docker compose -f docker-compose.development.yml config`
3. Run `./validate.sh` to check service expectations
4. Validate Python changes: `python3 llmstack/test_installations.py`
5. **Test working deployment:** `docker compose -f docker-compose.monitoring.yml up -d && sleep 10 && curl -s http://localhost:9090/api/v1/status/config && docker compose -f docker-compose.monitoring.yml down`

**Always validate that scripts remain executable and configuration files are syntactically correct.**