#!/usr/bin/env python3
"""
Code Quality Audit Tool for PC Automation Tools Repository
Analyzes code quality, structure, and best practices compliance
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
import subprocess

class CodeQualityAuditor:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.findings = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }
        self.metrics = {
            'total_files': 0,
            'python_files': 0,
            'shell_files': 0,
            'config_files': 0,
            'lines_of_code': 0,
            'functions': 0,
            'classes': 0
        }
        
    def log_finding(self, severity: str, category: str, description: str, file_path: str = None, line_num: int = None):
        """Log a code quality finding"""
        finding = {
            'category': category,
            'description': description,
            'file': str(file_path) if file_path else None,
            'line': line_num,
            'severity': severity
        }
        self.findings[severity].append(finding)
        
    def analyze_file_structure(self) -> None:
        """Analyze overall file and directory structure"""
        print("  • Analyzing file structure...")
        
        # Count file types
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                self.metrics['total_files'] += 1
                
                if file_path.suffix == '.py':
                    self.metrics['python_files'] += 1
                elif file_path.suffix == '.sh':
                    self.metrics['shell_files'] += 1
                elif file_path.suffix in {'.json', '.yaml', '.yml', '.conf', '.cfg', '.ini'}:
                    self.metrics['config_files'] += 1
                    
        # Check for essential files
        essential_files = ['README.md', 'requirements.txt', '.gitignore', 'LICENSE']
        for essential_file in essential_files:
            if not (self.repo_path / essential_file).exists():
                self.log_finding(
                    'medium',
                    'Project Structure',
                    f'Missing essential file: {essential_file}'
                )
                
        # Check for proper directory structure
        expected_dirs = ['scripts', 'docs', 'tests']
        for expected_dir in expected_dirs:
            if not (self.repo_path / expected_dir).exists():
                self.log_finding(
                    'low',
                    'Project Structure',
                    f'Missing recommended directory: {expected_dir}'
                )
                
    def analyze_python_code_quality(self) -> None:
        """Analyze Python code for quality issues"""
        print("  • Analyzing Python code quality...")
        
        python_files = list(self.repo_path.glob('**/*.py'))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                self.metrics['lines_of_code'] += len(content.splitlines())
                
                # Parse AST for deeper analysis
                try:
                    tree = ast.parse(content)
                    self._analyze_ast(tree, file_path)
                except SyntaxError as e:
                    self.log_finding(
                        'high',
                        'Python Syntax',
                        f'Syntax error: {e}',
                        file_path,
                        e.lineno
                    )
                    
                # Check for code smells
                self._check_python_code_smells(content, file_path)
                
            except Exception as e:
                self.log_finding('low', 'File Access', f'Could not analyze Python file: {e}', file_path)
                
    def _analyze_ast(self, tree: ast.AST, file_path: Path) -> None:
        """Analyze Python AST for quality metrics"""
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.metrics['functions'] += 1
                
                # Check function complexity
                complexity = self._calculate_cyclomatic_complexity(node)
                if complexity > 10:
                    self.log_finding(
                        'medium',
                        'Code Complexity',
                        f'High cyclomatic complexity in function {node.name}: {complexity}',
                        file_path,
                        node.lineno
                    )
                    
                # Check function length
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > 50:
                    self.log_finding(
                        'low',
                        'Code Style',
                        f'Long function {node.name}: {func_lines} lines',
                        file_path,
                        node.lineno
                    )
                    
            elif isinstance(node, ast.ClassDef):
                self.metrics['classes'] += 1
                
                # Check class size
                class_methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(class_methods) > 20:
                    self.log_finding(
                        'medium',
                        'Code Structure',
                        f'Large class {node.name}: {len(class_methods)} methods',
                        file_path,
                        node.lineno
                    )
                    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity
        
    def _check_python_code_smells(self, content: str, file_path: Path) -> None:
        """Check for Python code smells"""
        
        lines = content.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 88:  # PEP 8 recommends 79, but 88 is common
                self.log_finding(
                    'low',
                    'Code Style',
                    f'Line too long ({len(line)} characters)',
                    file_path,
                    line_num
                )
                
            # Multiple statements on one line
            if ';' in line and not line.strip().startswith('#'):
                self.log_finding(
                    'medium',
                    'Code Style',
                    'Multiple statements on one line',
                    file_path,
                    line_num
                )
                
            # TODO comments
            if 'TODO' in line.upper() or 'FIXME' in line.upper():
                self.log_finding(
                    'info',
                    'Documentation',
                    'TODO/FIXME comment found',
                    file_path,
                    line_num
                )
                
        # Check for missing docstrings
        if 'def ' in content and '"""' not in content and "'''" not in content:
            self.log_finding(
                'low',
                'Documentation',
                'Functions without docstrings detected',
                file_path
            )
            
        # Check imports
        if 'import *' in content:
            self.log_finding(
                'medium',
                'Code Style',
                'Wildcard import detected',
                file_path
            )
            
    def analyze_shell_scripts(self) -> None:
        """Analyze shell scripts for quality and security"""
        print("  • Analyzing shell scripts...")
        
        shell_files = list(self.repo_path.glob('**/*.sh'))
        
        for file_path in shell_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                lines = content.splitlines()
                
                # Check shebang
                if not lines or not lines[0].startswith('#!'):
                    self.log_finding(
                        'medium',
                        'Shell Scripts',
                        'Missing or invalid shebang',
                        file_path,
                        1
                    )
                    
                # Check for best practices
                if 'set -e' not in content:
                    self.log_finding(
                        'medium',
                        'Shell Scripts',
                        'Missing "set -e" for error handling',
                        file_path
                    )
                    
                # Check for unquoted variables
                unquoted_vars = re.findall(r'\$[A-Za-z_][A-Za-z0-9_]*(?!["}])', content)
                if unquoted_vars:
                    self.log_finding(
                        'low',
                        'Shell Scripts',
                        f'Potentially unquoted variables: {", ".join(set(unquoted_vars[:5]))}',
                        file_path
                    )
                    
            except Exception as e:
                self.log_finding('low', 'File Access', f'Could not analyze shell script: {e}', file_path)
                
    def analyze_configuration_files(self) -> None:
        """Analyze configuration files for issues"""
        print("  • Analyzing configuration files...")
        
        config_extensions = {'.json', '.yaml', '.yml', '.conf', '.cfg', '.ini'}
        config_files = []
        
        for ext in config_extensions:
            config_files.extend(self.repo_path.glob(f'**/*{ext}'))
            
        for file_path in config_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check JSON syntax
                if file_path.suffix == '.json':
                    try:
                        json.loads(content)
                    except json.JSONDecodeError as e:
                        self.log_finding(
                            'high',
                            'Configuration',
                            f'Invalid JSON syntax: {e}',
                            file_path,
                            e.lineno if hasattr(e, 'lineno') else None
                        )
                        
                # Check for potential security issues in configs
                if any(word in content.lower() for word in ['password', 'secret', 'key', 'token']):
                    if any(dummy in content.lower() for dummy in ['example', 'placeholder', 'change-me']):
                        self.log_finding(
                            'info',
                            'Configuration',
                            'Configuration contains placeholder credentials',
                            file_path
                        )
                        
            except Exception as e:
                self.log_finding('low', 'File Access', f'Could not analyze config file: {e}', file_path)
                
    def analyze_documentation(self) -> None:
        """Analyze documentation quality"""
        print("  • Analyzing documentation...")
        
        doc_files = list(self.repo_path.glob('**/*.md')) + list(self.repo_path.glob('**/*.rst'))
        
        if not doc_files:
            self.log_finding(
                'medium',
                'Documentation',
                'No documentation files found'
            )
            return
            
        readme_files = [f for f in doc_files if 'readme' in f.name.lower()]
        if not readme_files:
            self.log_finding(
                'medium',
                'Documentation',
                'No README file found'
            )
            
        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for empty documentation
                if len(content.strip()) < 100:
                    self.log_finding(
                        'low',
                        'Documentation',
                        'Very short documentation file',
                        doc_file
                    )
                    
                # Check for broken links (basic check)
                broken_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                links = re.findall(broken_link_pattern, content)
                for link_text, link_url in links:
                    if link_url.startswith('http') and 'localhost' in link_url:
                        self.log_finding(
                            'low',
                            'Documentation',
                            f'Documentation contains localhost link: {link_url}',
                            doc_file
                        )
                        
            except Exception as e:
                self.log_finding('low', 'File Access', f'Could not analyze documentation: {e}', doc_file)
                
    def check_dependency_management(self) -> None:
        """Check dependency management practices"""
        print("  • Analyzing dependency management...")
        
        req_files = list(self.repo_path.glob('**/requirements*.txt'))
        
        for req_file in req_files:
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Check for version pinning
                        if not re.search(r'[<>=!]', line):
                            self.log_finding(
                                'medium',
                                'Dependencies',
                                f'Unpinned dependency: {line}',
                                req_file,
                                line_num
                            )
                            
                        # Check for potentially insecure packages
                        insecure_packages = ['pickle', 'yaml', 'eval']
                        if any(pkg in line.lower() for pkg in insecure_packages):
                            self.log_finding(
                                'low',
                                'Dependencies',
                                f'Potentially risky dependency: {line}',
                                req_file,
                                line_num
                            )
                            
            except Exception as e:
                self.log_finding('low', 'File Access', f'Could not analyze requirements: {e}', req_file)
                
    def check_test_coverage(self) -> None:
        """Check for test files and coverage"""
        print("  • Analyzing test coverage...")
        
        test_files = []
        test_patterns = ['test_*.py', '*_test.py', 'tests/*.py', 'test/**/*.py']
        
        for pattern in test_patterns:
            test_files.extend(self.repo_path.glob(pattern))
            
        if not test_files:
            self.log_finding(
                'medium',
                'Testing',
                'No test files found'
            )
        else:
            test_ratio = len(test_files) / max(self.metrics['python_files'], 1)
            if test_ratio < 0.1:  # Less than 10% test coverage
                self.log_finding(
                    'medium',
                    'Testing',
                    f'Low test coverage: {len(test_files)} test files for {self.metrics["python_files"]} Python files'
                )
                
    def run_audit(self) -> Dict:
        """Run the complete code quality audit"""
        print("🔍 Starting comprehensive code quality audit...")
        
        self.analyze_file_structure()
        self.analyze_python_code_quality()
        self.analyze_shell_scripts()
        self.analyze_configuration_files()
        self.analyze_documentation()
        self.check_dependency_management()
        self.check_test_coverage()
        
        return self.findings
        
    def generate_report(self) -> str:
        """Generate a detailed code quality audit report"""
        total_findings = sum(len(findings) for findings in self.findings.values())
        
        report = "# Code Quality Audit Report\n\n"
        
        # Metrics Summary
        report += "## Project Metrics\n\n"
        report += f"- **Total Files:** {self.metrics['total_files']}\n"
        report += f"- **Python Files:** {self.metrics['python_files']}\n"
        report += f"- **Shell Scripts:** {self.metrics['shell_files']}\n"
        report += f"- **Config Files:** {self.metrics['config_files']}\n"
        report += f"- **Lines of Code:** {self.metrics['lines_of_code']}\n"
        report += f"- **Functions:** {self.metrics['functions']}\n"
        report += f"- **Classes:** {self.metrics['classes']}\n\n"
        
        # Findings Summary
        report += f"**Total Quality Issues:** {total_findings}\n\n"
        
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = len(self.findings[severity])
            if count > 0:
                report += f"- **{severity.upper()}:** {count} issues\n"
        
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
    """Main function to run the code quality audit"""
    repo_path = os.getcwd()
    auditor = CodeQualityAuditor(repo_path)
    
    # Run the audit
    findings = auditor.run_audit()
    
    # Generate and save report
    report = auditor.generate_report()
    
    with open('code_quality_audit_report.md', 'w') as f:
        f.write(report)
    
    print(f"\n✅ Code quality audit completed!")
    print(f"📊 Total issues: {sum(len(f) for f in findings.values())}")
    print(f"📄 Report saved to: code_quality_audit_report.md")
    
    # Return appropriate exit code
    critical_high = len(findings['critical']) + len(findings['high'])
    return 1 if critical_high > 0 else 0

if __name__ == "__main__":
    exit(main())