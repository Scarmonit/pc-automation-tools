#!/usr/bin/env python3
"""
Comprehensive Security Audit Tool for PC Automation Tools Repository
Performs security assessment across code, configuration, and infrastructure
"""

import os
import re
import json
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Set
import hashlib
import stat

class SecurityAuditor:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.findings = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }
        
    def log_finding(self, severity: str, category: str, description: str, file_path: str = None, line_num: int = None):
        """Log a security finding"""
        finding = {
            'category': category,
            'description': description,
            'file': str(file_path) if file_path else None,
            'line': line_num,
            'severity': severity
        }
        self.findings[severity].append(finding)
        
    def scan_hardcoded_secrets(self) -> None:
        """Scan for hardcoded secrets and sensitive data"""
        secret_patterns = {
            'api_key': r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{16,})["\']?',
            'password': r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^"\'\s]{8,})["\']?',
            'token': r'(?i)(token|auth_token|access_token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
            'secret': r'(?i)(secret|secret_key)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{16,})["\']?',
            'private_key': r'-----BEGIN\s+(RSA\s+)?PRIVATE KEY-----',
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'github_token': r'gh[ps]_[A-Za-z0-9_]{36}',
            'slack_token': r'xox[baprs]-[0-9a-zA-Z]{10,48}',
        }
        
        # File extensions to scan
        extensions = {'.py', '.sh', '.yaml', '.yml', '.json', '.env', '.conf', '.cfg', '.ini', '.txt', '.md'}
        
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    for pattern_name, pattern in secret_patterns.items():
                        matches = re.finditer(pattern, content, re.MULTILINE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            # Check if it's not just a placeholder or example
                            matched_text = match.group(0)
                            if not self._is_placeholder(matched_text):
                                severity = 'critical' if pattern_name in ['private_key', 'aws_key'] else 'high'
                                self.log_finding(
                                    severity,
                                    'Hardcoded Secrets',
                                    f'Potential {pattern_name} found: {matched_text[:50]}...',
                                    file_path,
                                    line_num
                                )
                                
                except Exception as e:
                    self.log_finding('low', 'File Access', f'Could not read file: {e}', file_path)
                    
    def _is_placeholder(self, text: str) -> bool:
        """Check if the text appears to be a placeholder or example"""
        placeholders = ['example', 'placeholder', 'dummy', 'test', 'fake', 'sample', 'your_', 'xxx', '***']
        return any(placeholder in text.lower() for placeholder in placeholders)
        
    def scan_file_permissions(self) -> None:
        """Check file permissions for security issues"""
        sensitive_files = ['.env', 'config', 'secrets', 'private', 'key', 'cert', 'password']
        
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                file_stat = file_path.stat()
                file_mode = stat.filemode(file_stat.st_mode)
                
                # Check for overly permissive files
                if file_stat.st_mode & stat.S_IWOTH:  # World writable
                    self.log_finding(
                        'high',
                        'File Permissions',
                        f'World-writable file: {file_mode}',
                        file_path
                    )
                    
                # Check sensitive files permissions
                if any(sensitive in file_path.name.lower() for sensitive in sensitive_files):
                    if file_stat.st_mode & stat.S_IROTH:  # World readable
                        self.log_finding(
                            'medium',
                            'File Permissions',
                            f'Sensitive file is world-readable: {file_mode}',
                            file_path
                        )
                        
    def scan_docker_security(self) -> None:
        """Analyze Docker configurations for security issues"""
        docker_files = list(self.repo_path.glob('**/Dockerfile*')) + list(self.repo_path.glob('**/docker-compose*.yml'))
        
        for file_path in docker_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for security anti-patterns
                if 'USER root' in content or not re.search(r'USER\s+\w+', content):
                    self.log_finding(
                        'medium',
                        'Docker Security',
                        'Container may run as root user',
                        file_path
                    )
                    
                if '--privileged' in content:
                    self.log_finding(
                        'high',
                        'Docker Security',
                        'Privileged container detected',
                        file_path
                    )
                    
                if re.search(r'ports:\s*-\s*["\']?0\.0\.0\.0:', content):
                    self.log_finding(
                        'medium',
                        'Docker Security',
                        'Service exposed on all interfaces (0.0.0.0)',
                        file_path
                    )
                    
            except Exception as e:
                self.log_finding('low', 'File Access', f'Could not read Docker file: {e}', file_path)
                
    def scan_network_exposure(self) -> None:
        """Check for network security issues"""
        config_files = list(self.repo_path.glob('**/*.yml')) + list(self.repo_path.glob('**/*.yaml')) + list(self.repo_path.glob('**/*.json'))
        
        dangerous_hosts = ['0.0.0.0', '127.0.0.1', 'localhost']
        public_ports = [80, 443, 8080, 3000, 3001, 3002, 5000, 8000, 9000]
        
        for file_path in config_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for exposed services
                for host in dangerous_hosts:
                    if f':{host}:' in content or f'"{host}"' in content:
                        self.log_finding(
                            'medium',
                            'Network Security',
                            f'Service potentially exposed on {host}',
                            file_path
                        )
                        
                # Check for common vulnerable ports
                for port in public_ports:
                    if f':{port}' in content:
                        self.log_finding(
                            'low',
                            'Network Security',
                            f'Service exposed on port {port}',
                            file_path
                        )
                        
            except Exception as e:
                self.log_finding('low', 'File Access', f'Could not read config file: {e}', file_path)
                
    def scan_dependencies(self) -> None:
        """Check for dependency security issues"""
        req_files = list(self.repo_path.glob('**/requirements*.txt'))
        
        for req_file in req_files:
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Check for unpinned versions
                        if '==' not in line and '>=' not in line and '<=' not in line:
                            self.log_finding(
                                'medium',
                                'Dependency Security',
                                f'Unpinned dependency: {line}',
                                req_file,
                                line_num
                            )
                            
            except Exception as e:
                self.log_finding('low', 'File Access', f'Could not read requirements file: {e}', req_file)
                
    def scan_input_validation(self) -> None:
        """Check for potential input validation issues"""
        python_files = list(self.repo_path.glob('**/*.py'))
        
        dangerous_patterns = {
            'eval': r'\beval\s*\(',
            'exec': r'\bexec\s*\(',
            'os.system': r'os\.system\s*\(',
            'subprocess without shell=False': r'subprocess\.(run|call|Popen)\s*\([^)]*shell\s*=\s*True',
            'sql injection': r'(execute|cursor)\s*\([^)]*%\s*%|\.format\s*\('
        }
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern_name, pattern in dangerous_patterns.items():
                    matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.log_finding(
                            'high',
                            'Input Validation',
                            f'Potentially dangerous {pattern_name} usage',
                            file_path,
                            line_num
                        )
                        
            except Exception as e:
                self.log_finding('low', 'File Access', f'Could not read Python file: {e}', file_path)
                
    def scan_logging_security(self) -> None:
        """Check for logging security issues"""
        python_files = list(self.repo_path.glob('**/*.py'))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for potential password logging
                password_log_pattern = r'log(?:ger)?\.(?:debug|info|warning|error|critical)\s*\([^)]*(?:password|passwd|pwd|secret|token|key)'
                matches = re.finditer(password_log_pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    self.log_finding(
                        'high',
                        'Logging Security',
                        'Potential sensitive data logging',
                        file_path,
                        line_num
                    )
                    
            except Exception as e:
                self.log_finding('low', 'File Access', f'Could not read Python file: {e}', file_path)
                
    def run_audit(self) -> Dict:
        """Run the complete security audit"""
        print("🔍 Starting comprehensive security audit...")
        
        print("  • Scanning for hardcoded secrets...")
        self.scan_hardcoded_secrets()
        
        print("  • Checking file permissions...")
        self.scan_file_permissions()
        
        print("  • Analyzing Docker security...")
        self.scan_docker_security()
        
        print("  • Checking network exposure...")
        self.scan_network_exposure()
        
        print("  • Scanning dependencies...")
        self.scan_dependencies()
        
        print("  • Checking input validation...")
        self.scan_input_validation()
        
        print("  • Analyzing logging security...")
        self.scan_logging_security()
        
        return self.findings
        
    def generate_report(self) -> str:
        """Generate a detailed security audit report"""
        total_findings = sum(len(findings) for findings in self.findings.values())
        
        report = "# Security Audit Report\n\n"
        report += f"**Total Findings:** {total_findings}\n\n"
        
        # Summary by severity
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = len(self.findings[severity])
            if count > 0:
                report += f"- **{severity.upper()}:** {count} findings\n"
        
        report += "\n## Detailed Findings\n\n"
        
        # Detailed findings by severity
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            findings = self.findings[severity]
            if findings:
                report += f"### {severity.upper()} Severity\n\n"
                
                for i, finding in enumerate(findings, 1):
                    report += f"**{i}. {finding['category']}**\n"
                    report += f"- Description: {finding['description']}\n"
                    if finding['file']:
                        report += f"- File: `{finding['file']}`\n"
                    if finding['line']:
                        report += f"- Line: {finding['line']}\n"
                    report += "\n"
                    
        return report

def main():
    """Main function to run the security audit"""
    repo_path = os.getcwd()
    auditor = SecurityAuditor(repo_path)
    
    # Run the audit
    findings = auditor.run_audit()
    
    # Generate and save report
    report = auditor.generate_report()
    
    with open('security_audit_report.md', 'w') as f:
        f.write(report)
    
    print(f"\n✅ Security audit completed!")
    print(f"📊 Total findings: {sum(len(f) for f in findings.values())}")
    print(f"📄 Report saved to: security_audit_report.md")
    
    # Return appropriate exit code
    critical_high = len(findings['critical']) + len(findings['high'])
    return 1 if critical_high > 0 else 0

if __name__ == "__main__":
    exit(main())