# Security Audit Report

**Total Findings:** 40

- **HIGH:** 5 findings
- **MEDIUM:** 17 findings
- **LOW:** 18 findings

## Detailed Findings

### HIGH Severity

**1. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=password...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.development.yml`
- Line: 31

**2. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=$(openssl...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/setup_llmstack.sh`
- Line: 16

**3. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=$(openssl...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/deploy_llmstack.sh`
- Line: 16

**4. Hardcoded Secrets**
- Description: Potential password found: password = "VKUY%Ck0"...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/auto_login.py`
- Line: 83

**5. Hardcoded Secrets**
- Description: Potential secret found: SECRET_KEY: "your-secret-key-here"...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/config/llmstack.yaml`
- Line: 8

### MEDIUM Severity

**1. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/.env.example`

**2. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/provider_config.py`

**3. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/autogen_config.json`

**4. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/continue_config.json`

**5. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/ollama_config.json`

**6. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/configure_providers.py`

**7. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/.git/config`

**8. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/localai_config.yaml`

**9. Docker Security**
- Description: Container may run as root user
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.development.yml`

**10. Docker Security**
- Description: Container may run as root user
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.monitoring.yml`

**11. Docker Security**
- Description: Container may run as root user
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.vllm.yml`

**12. Docker Security**
- Description: Container may run as root user
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/monitoring/docker-compose.yml`

**13. Dependency Security**
- Description: Unpinned dependency: autogen-agentchat
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 14

**14. Dependency Security**
- Description: Unpinned dependency: aider-chat
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 17

**15. Dependency Security**
- Description: Unpinned dependency: jq
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 34

**16. Dependency Security**
- Description: Unpinned dependency: jupyter
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 37

**17. Dependency Security**
- Description: Unpinned dependency: ipywidgets
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 38

### LOW Severity

**1. Network Security**
- Description: Service exposed on port 80
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.development.yml`

**2. Network Security**
- Description: Service exposed on port 3000
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.development.yml`

**3. Network Security**
- Description: Service exposed on port 3000
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.monitoring.yml`

**4. Network Security**
- Description: Service exposed on port 3000
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/prometheus.yml`

**5. Network Security**
- Description: Service exposed on port 80
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.vllm.yml`

**6. Network Security**
- Description: Service exposed on port 8000
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.vllm.yml`

**7. Network Security**
- Description: Service exposed on port 3001
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/monitoring/prometheus.yml`

**8. Network Security**
- Description: Service exposed on port 3002
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/monitoring/prometheus.yml`

**9. Network Security**
- Description: Service exposed on port 3000
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/monitoring/docker-compose.yml`

**10. Network Security**
- Description: Service exposed on port 80
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/localai_config.yaml`

**11. Network Security**
- Description: Service exposed on port 8080
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/localai_config.yaml`

**12. Network Security**
- Description: Service exposed on port 80
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/flowise_agent_flow.json`

**13. Network Security**
- Description: Service exposed on port 8080
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/flowise_agent_flow.json`

**14. Network Security**
- Description: Service exposed on port 80
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/.claude/settings.json`

**15. Network Security**
- Description: Service exposed on port 8080
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/.claude/settings.json`

**16. Network Security**
- Description: Service exposed on port 3000
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/.claude/settings.json`

**17. Network Security**
- Description: Service exposed on port 3001
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/.claude/settings.json`

**18. Network Security**
- Description: Service exposed on port 5000
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/.claude/settings.json`

