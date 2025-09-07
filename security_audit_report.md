# Security Audit Report

**Total Findings:** 67

- **HIGH:** 31 findings
- **MEDIUM:** 18 findings
- **LOW:** 18 findings

## Detailed Findings

### HIGH Severity

**1. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=${POSTGRES_PASSWORD:-password}...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.development.yml`
- Line: 31

**2. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=password......
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit_report.md`
- Line: 14

**3. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=$(openssl......
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit_report.md`
- Line: 19

**4. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=$(openssl......
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit_report.md`
- Line: 24

**5. Hardcoded Secrets**
- Description: Potential password found: password = "VKUY%Ck0"...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit_report.md`
- Line: 29

**6. Hardcoded Secrets**
- Description: Potential secret found: SECRET_KEY: "your-secret-key-here"...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit_report.md`
- Line: 34

**7. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=$(openssl...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/setup_llmstack.sh`
- Line: 16

**8. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=password......
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/COMPREHENSIVE_AUDIT_REPORT.md`
- Line: 372

**9. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=$(openssl......
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/COMPREHENSIVE_AUDIT_REPORT.md`
- Line: 377

**10. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=$(openssl......
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/COMPREHENSIVE_AUDIT_REPORT.md`
- Line: 382

**11. Hardcoded Secrets**
- Description: Potential password found: password = "VKUY%Ck0"...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/COMPREHENSIVE_AUDIT_REPORT.md`
- Line: 387

**12. Hardcoded Secrets**
- Description: Potential secret found: SECRET_KEY: "your-secret-key-here"...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/COMPREHENSIVE_AUDIT_REPORT.md`
- Line: 392

**13. Hardcoded Secrets**
- Description: Potential api_key found: API_KEY=your-openai-key-here...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 119

**14. Hardcoded Secrets**
- Description: Potential api_key found: API_KEY=your-anthropic-key-here...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 120

**15. Hardcoded Secrets**
- Description: Potential password found: password = "VKUY%Ck0"...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 38

**16. Hardcoded Secrets**
- Description: Potential password found: password = os.getenv("...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 39

**17. Hardcoded Secrets**
- Description: Potential password found: PASSWORD="your-secure-password"...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 51

**18. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=password'...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 86

**19. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=${POSTGRES_PASSWORD:-password}'...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 87

**20. Hardcoded Secrets**
- Description: Potential password found: PASSWORD={generate_secure_password()}...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 108

**21. Hardcoded Secrets**
- Description: Potential password found: PASSWORD={generate_secure_password()}...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 112

**22. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=your-secure-password...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 116

**23. Hardcoded Secrets**
- Description: Potential secret found: SECRET_KEY: "your-secret-key-here"...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 67

**24. Hardcoded Secrets**
- Description: Potential password found: PASSWORD=$(openssl...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/deploy_llmstack.sh`
- Line: 16

**25. Hardcoded Secrets**
- Description: Potential password found: PASSWORD="your-secure-password"...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/auto_login.py`
- Line: 5

**26. Hardcoded Secrets**
- Description: Potential password found: password = os.getenv("...
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/auto_login.py`
- Line: 89

**27. Logging Security**
- Description: Potential sensitive data logging
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/github_automation.py`
- Line: 61

**28. Logging Security**
- Description: Potential sensitive data logging
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/auto_submit.py`
- Line: 39

**29. Logging Security**
- Description: Potential sensitive data logging
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/auto_submit.py`
- Line: 40

**30. Logging Security**
- Description: Potential sensitive data logging
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/auto_submit.py`
- Line: 41

**31. Logging Security**
- Description: Potential sensitive data logging
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/auto_submit.py`
- Line: 42

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
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/.env.template`

**5. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/continue_config.json`

**6. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/ollama_config.json`

**7. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/configure_providers.py`

**8. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/.git/config`

**9. File Permissions**
- Description: Sensitive file is world-readable: -rw-r--r--
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/localai_config.yaml`

**10. Docker Security**
- Description: Container may run as root user
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.development.yml`

**11. Docker Security**
- Description: Container may run as root user
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.monitoring.yml`

**12. Docker Security**
- Description: Container may run as root user
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.vllm.yml`

**13. Docker Security**
- Description: Container may run as root user
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/monitoring/docker-compose.yml`

**14. Dependency Security**
- Description: Unpinned dependency: autogen-agentchat
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 14

**15. Dependency Security**
- Description: Unpinned dependency: aider-chat
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 17

**16. Dependency Security**
- Description: Unpinned dependency: jq
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 34

**17. Dependency Security**
- Description: Unpinned dependency: jupyter
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 37

**18. Dependency Security**
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

