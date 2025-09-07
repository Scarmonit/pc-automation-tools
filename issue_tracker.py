#!/usr/bin/env python3
"""
Security and Code Quality Issue Tracking System

This module provides functionality to parse audit reports and create
structured tracking for all outstanding security and code quality issues.
"""

import os
import json
import yaml
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class Severity(Enum):
    """Issue severity levels"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"
    
    def __lt__(self, other):
        if not isinstance(other, Severity):
            return NotImplemented
        priority = {Severity.HIGH: 4, Severity.MEDIUM: 3, Severity.LOW: 2, Severity.INFO: 1}
        return priority[self] < priority[other]


class Category(Enum):
    """Issue categories"""
    HARDCODED_SECRETS = "Hardcoded Secrets"
    DOCKER_SECURITY = "Docker Security"
    FILE_PERMISSIONS = "File Permissions"
    NETWORK_SECURITY = "Network Security"
    DEPENDENCY_SECURITY = "Dependency Security"
    CODE_STYLE = "Code Style"
    CODE_COMPLEXITY = "Code Complexity"
    SHELL_SCRIPTS = "Shell Scripts"
    DOCUMENTATION = "Documentation"
    PROJECT_STRUCTURE = "Project Structure"
    DEPENDENCIES = "Dependencies"


class Status(Enum):
    """Issue status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DEFERRED = "deferred"
    WONT_FIX = "wont_fix"


@dataclass
class Issue:
    """Represents a single security or code quality issue"""
    id: str
    title: str
    description: str
    severity: Severity
    category: Category
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    status: Status = Status.OPEN
    assigned_to: Optional[str] = None
    created_date: str = ""
    due_date: Optional[str] = None
    remediation_notes: str = ""
    estimated_effort: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()


@dataclass
class IssueGroup:
    """Represents a group of related issues"""
    group_id: str
    title: str
    description: str
    category: Category
    severity: Severity
    issues: List[Issue]
    priority_rank: int = 0
    estimated_total_effort: Optional[str] = None


class IssueTracker:
    """Main class for tracking and managing security/quality issues"""
    
    def __init__(self, data_dir: str = "issue_tracking"):
        self.data_dir = data_dir
        self.issues: List[Issue] = []
        self.issue_groups: List[IssueGroup] = []
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(f"{self.data_dir}/issues", exist_ok=True)
        os.makedirs(f"{self.data_dir}/groups", exist_ok=True)
        os.makedirs(f"{self.data_dir}/reports", exist_ok=True)
    
    def parse_security_audit_report(self, report_path: str) -> List[Issue]:
        """Parse security audit report and extract issues"""
        issues = []
        
        try:
            with open(report_path, 'r') as f:
                content = f.read()
            
            # Parse HIGH severity issues
            high_section = re.search(r'### HIGH Severity\s*\n(.*?)(?=### MEDIUM Severity|$)', content, re.DOTALL)
            if high_section:
                issues.extend(self._parse_security_issues(high_section.group(1), Severity.HIGH))
            
            # Parse MEDIUM severity issues
            medium_section = re.search(r'### MEDIUM Severity\s*\n(.*?)(?=### LOW Severity|$)', content, re.DOTALL)
            if medium_section:
                issues.extend(self._parse_security_issues(medium_section.group(1), Severity.MEDIUM))
            
            # Parse LOW severity issues
            low_section = re.search(r'### LOW Severity\s*\n(.*?)$', content, re.DOTALL)
            if low_section:
                issues.extend(self._parse_security_issues(low_section.group(1), Severity.LOW))
                
        except Exception as e:
            print(f"Error parsing security audit report: {e}")
        
        return issues
    
    def _parse_security_issues(self, section_content: str, severity: Severity) -> List[Issue]:
        """Parse individual security issues from a section"""
        issues = []
        
        # Pattern to match issue blocks
        issue_pattern = r'\*\*(\d+)\.\s+([^*]+?)\*\*\s*\n- Description:\s*([^\n]+)(?:\n- File:\s*([^\n]+))?(?:\n- Line:\s*(\d+))?'
        
        matches = re.findall(issue_pattern, section_content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            issue_num, category_name, description, file_path, line_num = match
            
            # Map category name to enum
            category = self._map_security_category(category_name.strip())
            
            issue_id = f"SEC-{severity.value}-{issue_num.zfill(3)}"
            title = f"{category_name.strip()}: {description[:50]}..."
            
            issue = Issue(
                id=issue_id,
                title=title,
                description=description.strip(),
                severity=severity,
                category=category,
                file_path=file_path.strip() if file_path else None,
                line_number=int(line_num) if line_num else None
            )
            
            issues.append(issue)
        
        return issues
    
    def parse_code_quality_report(self, report_path: str) -> List[Issue]:
        """Parse code quality audit report and extract issues"""
        issues = []
        
        try:
            with open(report_path, 'r') as f:
                content = f.read()
            
            # Parse MEDIUM severity issues
            medium_section = re.search(r'### MEDIUM Severity\s*\n(.*?)(?=### LOW Severity|$)', content, re.DOTALL)
            if medium_section:
                issues.extend(self._parse_quality_issues(medium_section.group(1), Severity.MEDIUM))
            
            # Parse LOW severity issues
            low_section = re.search(r'### LOW Severity\s*\n(.*?)(?=### INFO Severity|$)', content, re.DOTALL)
            if low_section:
                issues.extend(self._parse_quality_issues(low_section.group(1), Severity.LOW))
            
            # Parse INFO severity issues
            info_section = re.search(r'### INFO Severity\s*\n(.*?)$', content, re.DOTALL)
            if info_section:
                issues.extend(self._parse_quality_issues(info_section.group(1), Severity.INFO))
                
        except Exception as e:
            print(f"Error parsing code quality report: {e}")
        
        return issues
    
    def _parse_quality_issues(self, section_content: str, severity: Severity) -> List[Issue]:
        """Parse individual code quality issues from a section"""
        issues = []
        
        # Pattern to match issue blocks
        issue_pattern = r'\*\*(\d+)\.\s+([^*]+?)\*\*\s*\n- Description:\s*([^\n]+)(?:\n- File:\s*([^\n]+))?(?:\n- Line:\s*(\d+))?'
        
        matches = re.findall(issue_pattern, section_content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            issue_num, category_name, description, file_path, line_num = match
            
            # Map category name to enum
            category = self._map_quality_category(category_name.strip())
            
            issue_id = f"QA-{severity.value}-{issue_num.zfill(3)}"
            title = f"{category_name.strip()}: {description[:50]}..."
            
            issue = Issue(
                id=issue_id,
                title=title,
                description=description.strip(),
                severity=severity,
                category=category,
                file_path=file_path.strip() if file_path else None,
                line_number=int(line_num) if line_num else None
            )
            
            issues.append(issue)
        
        return issues
    
    def _map_security_category(self, category_name: str) -> Category:
        """Map security category name to enum"""
        mapping = {
            "Hardcoded Secrets": Category.HARDCODED_SECRETS,
            "File Permissions": Category.FILE_PERMISSIONS,
            "Docker Security": Category.DOCKER_SECURITY,
            "Network Security": Category.NETWORK_SECURITY,
            "Dependency Security": Category.DEPENDENCY_SECURITY,
        }
        return mapping.get(category_name, Category.DOCUMENTATION)
    
    def _map_quality_category(self, category_name: str) -> Category:
        """Map code quality category name to enum"""
        mapping = {
            "Code Style": Category.CODE_STYLE,
            "Code Complexity": Category.CODE_COMPLEXITY,
            "Shell Scripts": Category.SHELL_SCRIPTS,
            "Documentation": Category.DOCUMENTATION,
            "Project Structure": Category.PROJECT_STRUCTURE,
            "Dependencies": Category.DEPENDENCIES,
        }
        return mapping.get(category_name, Category.DOCUMENTATION)
    
    def group_issues_by_category(self) -> Dict[Category, List[Issue]]:
        """Group issues by category"""
        groups = {}
        for issue in self.issues:
            if issue.category not in groups:
                groups[issue.category] = []
            groups[issue.category].append(issue)
        return groups
    
    def create_issue_groups(self):
        """Create issue groups for better organization"""
        category_groups = self.group_issues_by_category()
        
        priority_mapping = {
            Category.HARDCODED_SECRETS: 1,
            Category.DOCKER_SECURITY: 2,
            Category.FILE_PERMISSIONS: 3,
            Category.DEPENDENCY_SECURITY: 4,
            Category.NETWORK_SECURITY: 5,
            Category.CODE_COMPLEXITY: 6,
            Category.CODE_STYLE: 7,
            Category.SHELL_SCRIPTS: 8,
            Category.PROJECT_STRUCTURE: 9,
            Category.DOCUMENTATION: 10,
            Category.DEPENDENCIES: 11,
        }
        
        for category, issues in category_groups.items():
            if not issues:
                continue
                
            # Determine group severity (highest severity in group)
            group_severity = max(issue.severity for issue in issues)
            
            group = IssueGroup(
                group_id=f"GROUP-{category.name}",
                title=f"{category.value} Issues",
                description=f"All {category.value.lower()} related issues requiring remediation",
                category=category,
                severity=group_severity,
                issues=issues,
                priority_rank=priority_mapping.get(category, 99)
            )
            
            self.issue_groups.append(group)
        
        # Sort by priority
        self.issue_groups.sort(key=lambda g: (g.severity.value, g.priority_rank))
    
    def save_issues_to_json(self, filename: str = "all_issues.json"):
        """Save all issues to JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump([asdict(issue) for issue in self.issues], f, indent=2, default=str)
    
    def save_issue_groups_to_yaml(self, filename: str = "issue_groups.yaml"):
        """Save issue groups to YAML file"""
        filepath = os.path.join(self.data_dir, filename)
        groups_data = []
        
        for group in self.issue_groups:
            group_dict = asdict(group)
            group_dict['issues'] = [asdict(issue) for issue in group.issues]
            groups_data.append(group_dict)
        
        with open(filepath, 'w') as f:
            yaml.dump(groups_data, f, default_flow_style=False)
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of all issues"""
        total_issues = len(self.issues)
        
        severity_counts = {
            Severity.HIGH: len([i for i in self.issues if i.severity == Severity.HIGH]),
            Severity.MEDIUM: len([i for i in self.issues if i.severity == Severity.MEDIUM]),
            Severity.LOW: len([i for i in self.issues if i.severity == Severity.LOW]),
            Severity.INFO: len([i for i in self.issues if i.severity == Severity.INFO]),
        }
        
        category_counts = {}
        for issue in self.issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        report = f"""# Security and Code Quality Issues Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Issues:** {total_issues}

## Issues by Severity
- **HIGH:** {severity_counts[Severity.HIGH]} issues
- **MEDIUM:** {severity_counts[Severity.MEDIUM]} issues
- **LOW:** {severity_counts[Severity.LOW]} issues
- **INFO:** {severity_counts[Severity.INFO]} issues

## Issues by Category
"""
        
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{category.value}:** {count} issues\n"
        
        report += f"\n## Issue Groups ({len(self.issue_groups)} groups)\n\n"
        
        for i, group in enumerate(self.issue_groups, 1):
            report += f"{i}. **{group.title}** ({group.severity.value} priority)\n"
            report += f"   - {len(group.issues)} issues\n"
            report += f"   - Category: {group.category.value}\n\n"
        
        return report
    
    def load_issues(self):
        """Load all issues from audit reports"""
        # Parse security audit report
        security_report = "security_audit_report.md"
        if os.path.exists(security_report):
            self.issues.extend(self.parse_security_audit_report(security_report))
        
        # Parse code quality audit report
        quality_report = "code_quality_audit_report.md"
        if os.path.exists(quality_report):
            self.issues.extend(self.parse_code_quality_report(quality_report))
        
        # Create issue groups
        self.create_issue_groups()


def main():
    """Main function to initialize and run the issue tracker"""
    tracker = IssueTracker()
    
    print("Loading issues from audit reports...")
    tracker.load_issues()
    
    print(f"Loaded {len(tracker.issues)} total issues")
    print(f"Created {len(tracker.issue_groups)} issue groups")
    
    # Save data
    tracker.save_issues_to_json()
    tracker.save_issue_groups_to_yaml()
    
    # Generate summary report
    summary = tracker.generate_summary_report()
    with open(f"{tracker.data_dir}/summary_report.md", 'w') as f:
        f.write(summary)
    
    print("\nSummary Report:")
    print("=" * 50)
    print(summary)
    
    print(f"\nData saved to '{tracker.data_dir}/' directory")


if __name__ == "__main__":
    main()