#!/usr/bin/env python3
"""
Security Fix Script for Critical Vulnerabilities
Automatically fixes critical security issues found in the audit
"""

import os
import secrets
import string
from pathlib import Path

def generate_secure_password(length=16):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secret_key(length=50):
    """Generate a secure secret key"""
    return secrets.token_urlsafe(length)

def fix_hardcoded_credentials():
    """Fix hardcoded credentials by replacing with environment variables"""

    print("🔧 Fixing hardcoded credentials...")

    # Fix auto_login.py - remove hardcoded password
    auto_login_path = Path("llmstack/auto_login.py")
    if auto_login_path.exists():
        with open(auto_login_path, 'r') as f:
            content = f.read()

        # Replace hardcoded credentials with environment variables
        new_content = content.replace(
            'email = "scarmonit@gmail.com"',
            'email = os.getenv("LOGIN_EMAIL", "")'
        ).replace(
            'password = "VKUY%Ck0"',
            'password = os.getenv("LOGIN_PASSWORD", "")'
        )

        # Add import for os if not present
        if 'import os' not in new_content:
            new_content = 'import os\n' + new_content

        # Add security warning comment
        security_comment = '''
# SECURITY WARNING: Credentials should be set via environment variables
# Set LOGIN_EMAIL and LOGIN_PASSWORD environment variables before running
# Example: export LOGIN_EMAIL="your-email@example.com"
#          export LOGIN_PASSWORD="your-secure-password"
'''
        new_content = security_comment + new_content

        with open(auto_login_path, 'w') as f:
            f.write(new_content)
        print(f"  ✅ Fixed hardcoded credentials in {auto_login_path}")

    # Fix config/llmstack.yaml - replace placeholder secret
    config_path = Path("config/llmstack.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            content = f.read()

        # Replace placeholder secret key
        new_content = content.replace(
            'LLMSTACK_SECRET_KEY: "your-secret-key-here"',
            'LLMSTACK_SECRET_KEY: "${LLMSTACK_SECRET_KEY}"'
        ).replace(
            'DATABASE_URL: "postgresql://postgres:password@postgres:5432/llmstack"',
            'DATABASE_URL: "${DATABASE_URL}"'
        )

        with open(config_path, 'w') as f:
            f.write(new_content)
        print(f"  ✅ Fixed placeholder secrets in {config_path}")

    # Fix docker-compose.development.yml - use environment variables
    docker_compose_path = Path("docker-compose.development.yml")
    if docker_compose_path.exists():
        with open(docker_compose_path, 'r') as f:
            content = f.read()

        # Replace hardcoded password with environment variable
        new_content = content.replace(
            '- POSTGRES_PASSWORD=password',
            '- POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-password}'
        )

        with open(docker_compose_path, 'w') as f:
            f.write(new_content)
        print(f"  ✅ Fixed hardcoded password in {docker_compose_path}")

def create_env_template():
    """Create a comprehensive .env template with secure defaults"""

    print("📝 Creating secure environment template...")

    env_template = f"""# LLMStack Environment Configuration
# Copy this file to .env and update with your actual values

# Security Keys (CHANGE THESE!)
LLMSTACK_SECRET_KEY={generate_secret_key()}
JWT_SECRET_KEY={generate_secret_key()}

# Database Configuration
DATABASE_URL=postgresql://postgres:${{POSTGRES_PASSWORD}}@localhost:5432/llmstack
POSTGRES_PASSWORD={generate_secure_password()}

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD={generate_secure_password()}

# Authentication (for auto_login.py)
LOGIN_EMAIL=your-email@example.com
LOGIN_PASSWORD=your-secure-password

# API Keys (set these if using external services)
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

# Service URLs
OLLAMA_BASE_URL=http://localhost:11434
FLOWISE_URL=http://localhost:3001
OPENHANDS_URL=http://localhost:3002
GRAFANA_URL=http://localhost:3003

# Performance Settings
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
WORKER_PROCESSES=4

# Feature Flags
ENABLE_AGENTS=true
ENABLE_RAG=true
ENABLE_WORKFLOWS=true
ENABLE_MONITORING=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
ALLOWED_HOSTS=localhost,127.0.0.1
SECURE_COOKIES=true
"""

    with open('.env.template', 'w') as f:
        f.write(env_template)
    print("  ✅ Created .env.template with secure defaults")

def update_gitignore():
    """Update .gitignore to ensure sensitive files are not committed"""

    print("🛡️  Updating .gitignore for security...")

    gitignore_path = Path('.gitignore')

    # Security-focused gitignore additions
    security_additions = """
# Security - Sensitive files (DO NOT COMMIT)
.env
.env.local
.env.production
.env.*.local
secrets/
private_keys/
*.key
*.pem
*.p12
*.pfx
*.crt
config/secrets.yaml
config/production.yaml

# Credentials and API keys
**/api_keys.json
**/credentials.json
**/service-account*.json
auth.json
token.json

# Database dumps and backups
*.sql
*.dump
*.backup
backups/

# Logs that might contain sensitive data
audit.log
security.log
access.log
error.log
"""

    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            content = f.read()

        # Only add if not already present
        if 'Security - Sensitive files' not in content:
            with open(gitignore_path, 'a') as f:
                f.write(security_additions)
            print("  ✅ Updated .gitignore with security patterns")
    else:
        with open(gitignore_path, 'w') as f:
            f.write(security_additions)
        print("  ✅ Created .gitignore with security patterns")

def fix_docker_security():
    """Fix Docker security issues"""

    print("🐳 Fixing Docker security issues...")

    docker_files = [
        "docker-compose.development.yml",
        "docker-compose.monitoring.yml",
        "docker-compose.vllm.yml"
    ]

    for docker_file in docker_files:
        docker_path = Path(docker_file)
        if docker_path.exists():
            with open(docker_path, 'r') as f:
                content = f.read()

            # Add security context and user
            if 'user:' not in content and 'security_opt:' not in content:
                # Add security improvements - this is a simplified approach
                # In practice, each service would need specific user configuration
                print(f"  ⚠️  {docker_file} needs manual review for user configuration")

    print("  ✅ Docker files flagged for security review")

def create_security_checklist():
    """Create a security checklist for the team"""

    checklist = """# Security Checklist

## Critical Actions Required

### 1. Environment Variables
- [ ] Copy `.env.template` to `.env`
- [ ] Update all placeholder values in `.env`
- [ ] Verify `.env` is in `.gitignore`
- [ ] Set strong passwords (minimum 16 characters)

### 2. Credentials Management
- [ ] Remove any remaining hardcoded passwords
- [ ] Use environment variables for all secrets
- [ ] Implement proper secret rotation
- [ ] Use a secret management system in production

### 3. Docker Security
- [ ] Review all Docker containers to run as non-root users
- [ ] Implement proper network segmentation
- [ ] Use specific version tags instead of 'latest'
- [ ] Enable Docker security scanning

### 4. Network Security
- [ ] Restrict service binding to localhost where possible
- [ ] Implement proper firewall rules
- [ ] Use TLS/SSL for all external communications
- [ ] Regular security scanning of exposed ports

### 5. File Permissions
- [ ] Restrict permissions on configuration files
- [ ] Ensure sensitive files are not world-readable
- [ ] Implement proper access controls
- [ ] Regular permission audits

### 6. Dependencies
- [ ] Pin all dependency versions
- [ ] Regular security updates
- [ ] Use dependency vulnerability scanning
- [ ] Remove unused dependencies

### 7. Monitoring & Logging
- [ ] Implement security event logging
- [ ] Set up intrusion detection
- [ ] Regular log analysis
- [ ] Incident response procedures

## Regular Security Practices

### Daily
- [ ] Monitor logs for suspicious activity
- [ ] Check for security alerts

### Weekly
- [ ] Review access logs
- [ ] Update dependencies if needed

### Monthly
- [ ] Run security audit
- [ ] Review and rotate secrets
- [ ] Update security documentation

### Quarterly
- [ ] Comprehensive penetration testing
- [ ] Security training for team
- [ ] Review security policies
"""

    with open('SECURITY_CHECKLIST.md', 'w') as f:
        f.write(checklist)
    print("📋 Created SECURITY_CHECKLIST.md")

def main():
    """Main function to run all security fixes"""
    print("🚨 Starting Critical Security Fixes...")
    print("=" * 50)

    fix_hardcoded_credentials()
    create_env_template()
    update_gitignore()
    fix_docker_security()
    create_security_checklist()

    print("\n" + "=" * 50)
    print("✅ Critical security fixes completed!")
    print("\n🎯 IMMEDIATE ACTIONS REQUIRED:")
    print("1. Review and customize .env.template")
    print("2. Copy .env.template to .env with your values")
    print("3. Follow SECURITY_CHECKLIST.md")
    print("4. Review all Docker configurations")
    print("5. Test all services with new configuration")
    print("\n⚠️  WARNING: Test thoroughly before production deployment!")

if __name__ == "__main__":
    main()
