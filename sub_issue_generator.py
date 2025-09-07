#!/usr/bin/env python3
"""
Actionable Sub-Issue Template Generator

This module creates detailed sub-issue templates for each category
of security and code quality issues found in the audit.
"""

import os
import json
import yaml
from datetime import datetime
from typing import Dict, List
from issue_tracker import IssueTracker, Severity, Category


class SubIssueTemplateGenerator:
    """Generates actionable sub-issue templates for each issue category"""
    
    def __init__(self, issue_tracker: IssueTracker):
        self.tracker = issue_tracker
        self.templates_dir = "issue_tracking/sub_issues"
        self._ensure_templates_dir()
    
    def _ensure_templates_dir(self):
        """Ensure templates directory exists"""
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def generate_all_templates(self):
        """Generate templates for all issue groups"""
        for group in self.tracker.issue_groups:
            self.generate_group_template(group)
    
    def generate_group_template(self, group):
        """Generate template for a specific issue group"""
        template_content = self._create_template_content(group)
        
        # Safe filename
        filename = f"{group.group_id.lower().replace('-', '_')}.md"
        filepath = os.path.join(self.templates_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(template_content)
        
        print(f"Generated template: {filepath}")
    
    def _create_template_content(self, group) -> str:
        """Create the template content for an issue group"""
        # Calculate effort estimate
        effort_mapping = {
            Category.HARDCODED_SECRETS: "2-4 hours",
            Category.DOCKER_SECURITY: "4-6 hours", 
            Category.FILE_PERMISSIONS: "1-2 hours",
            Category.DEPENDENCY_SECURITY: "2-3 hours",
            Category.NETWORK_SECURITY: "1-3 hours",
            Category.CODE_STYLE: "4-8 hours",
            Category.CODE_COMPLEXITY: "6-12 hours",
            Category.SHELL_SCRIPTS: "3-6 hours",
            Category.PROJECT_STRUCTURE: "2-4 hours",
            Category.DOCUMENTATION: "3-5 hours",
            Category.DEPENDENCIES: "1-2 hours",
        }
        
        estimated_effort = effort_mapping.get(group.category, "TBD")
        
        # Priority description
        priority_desc = self._get_priority_description(group.severity, group.category)
        
        # Remediation strategy
        remediation_strategy = self._get_remediation_strategy(group.category)
        
        # Acceptance criteria
        acceptance_criteria = self._get_acceptance_criteria(group.category)
        
        template = f"""# {group.title}

**Issue Group ID:** {group.group_id}
**Category:** {group.category.value}
**Severity:** {group.severity.value}
**Priority Rank:** {group.priority_rank}
**Total Issues:** {len(group.issues)}
**Estimated Effort:** {estimated_effort}
**Created:** {datetime.now().strftime('%Y-%m-%d')}

## Description

{group.description}

{priority_desc}

## Issues Summary

"""
        
        # Add issues table
        template += "| ID | Description | File | Line | Status |\n"
        template += "|-----|-------------|------|------|--------|\n"
        
        for issue in group.issues[:10]:  # Show first 10 issues
            file_display = issue.file_path.split('/')[-1] if issue.file_path else "N/A"
            line_display = str(issue.line_number) if issue.line_number else "N/A"
            template += f"| {issue.id} | {issue.description[:60]}... | {file_display} | {line_display} | {issue.status.value} |\n"
        
        if len(group.issues) > 10:
            template += f"\n*... and {len(group.issues) - 10} more issues*\n"
        
        template += f"""

## Remediation Strategy

{remediation_strategy}

## Implementation Plan

### Phase 1: Preparation
- [ ] Review all issues in this category
- [ ] Identify files requiring changes
- [ ] Backup affected files
- [ ] Set up testing environment

### Phase 2: Implementation
- [ ] Address high-impact issues first
- [ ] Apply remediation changes systematically
- [ ] Test changes incrementally
- [ ] Document changes made

### Phase 3: Validation
- [ ] Run security/quality checks
- [ ] Verify no new issues introduced
- [ ] Update issue status tracking
- [ ] Review with team

## Acceptance Criteria

{acceptance_criteria}

## Risk Assessment

### Risk Level: {self._get_risk_level(group.severity)}

### Potential Impact
{self._get_impact_description(group.category)}

### Mitigation Strategy
{self._get_mitigation_strategy(group.category)}

## Resource Requirements

- **Developer Time:** {estimated_effort}
- **Skills Required:** {self._get_required_skills(group.category)}
- **Tools Needed:** {self._get_required_tools(group.category)}

## Success Metrics

- [ ] All issues in category resolved
- [ ] No regression in functionality
- [ ] Security/quality scans pass
- [ ] Documentation updated
- [ ] Team review completed

## Related Issues

{self._get_related_categories(group.category)}

## Notes

*This is an auto-generated sub-issue template. Please review and customize as needed before implementation.*

**Next Actions:**
1. Assign team member responsible for this category
2. Schedule implementation timeline
3. Set up regular progress check-ins
4. Begin Phase 1 preparation work

---

**Auto-generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**From audit reports:** security_audit_report.md, code_quality_audit_report.md
"""
        
        return template
    
    def _get_priority_description(self, severity: Severity, category: Category) -> str:
        """Get priority description based on severity and category"""
        if severity == Severity.HIGH:
            return "🚨 **CRITICAL PRIORITY** - These issues pose immediate security risks and must be addressed as soon as possible."
        elif severity == Severity.MEDIUM:
            return "⚠️ **HIGH PRIORITY** - These issues should be resolved promptly to improve security and code quality."
        elif severity == Severity.LOW:
            return "📋 **MEDIUM PRIORITY** - These issues should be addressed to maintain good practices and code hygiene."
        else:
            return "ℹ️ **LOW PRIORITY** - These are informational items that can be addressed during regular maintenance."
    
    def _get_remediation_strategy(self, category: Category) -> str:
        """Get remediation strategy for each category"""
        strategies = {
            Category.HARDCODED_SECRETS: """
1. **Identify all hardcoded credentials and secrets**
2. **Create environment variables or secure vault storage**
3. **Replace hardcoded values with variable references**
4. **Update deployment configuration**
5. **Test with new secure configuration**
6. **Add secrets to .gitignore if not already present**
            """.strip(),
            
            Category.DOCKER_SECURITY: """
1. **Review all Docker Compose files**
2. **Add non-root user configurations**
3. **Implement security contexts and capabilities**
4. **Configure network isolation**
5. **Test container functionality with security settings**
6. **Update documentation for secure deployment**
            """.strip(),
            
            Category.FILE_PERMISSIONS: """
1. **Audit current file permissions**
2. **Identify files requiring restricted access**
3. **Update file permissions to appropriate levels**
4. **Implement permission validation scripts**
5. **Test application functionality**
6. **Document security requirements**
            """.strip(),
            
            Category.CODE_STYLE: """
1. **Set up automated code formatting tools**
2. **Configure linting rules and standards**
3. **Apply formatting fixes in batches**
4. **Add pre-commit hooks for future compliance**
5. **Update development guidelines**
6. **Train team on coding standards**
            """.strip(),
            
            Category.SHELL_SCRIPTS: """
1. **Add proper error handling (set -e)**
2. **Quote all variables properly**
3. **Add input validation**
4. **Implement logging and debugging options**
5. **Test scripts on different environments**
6. **Add comprehensive documentation**
            """.strip(),
        }
        
        return strategies.get(category, "Develop category-specific remediation approach based on issue details.")
    
    def _get_acceptance_criteria(self, category: Category) -> str:
        """Get acceptance criteria for each category"""
        criteria = {
            Category.HARDCODED_SECRETS: """
- [ ] No hardcoded passwords, API keys, or secrets in code
- [ ] All sensitive values use environment variables
- [ ] Secure configuration template provided
- [ ] Deployment documentation updated
- [ ] Security scan passes without credential warnings
            """.strip(),
            
            Category.DOCKER_SECURITY: """
- [ ] All containers run as non-root users
- [ ] Proper security contexts configured
- [ ] Network isolation implemented where appropriate
- [ ] No unnecessary capabilities granted
- [ ] Security scan passes for container configurations
            """.strip(),
            
            Category.FILE_PERMISSIONS: """
- [ ] Sensitive files have restricted permissions (600 or 640)
- [ ] No world-readable sensitive configuration files
- [ ] Permission validation script created
- [ ] Documentation includes security requirements
- [ ] No functionality broken by permission changes
            """.strip(),
            
            Category.CODE_STYLE: """
- [ ] All code follows established style guidelines
- [ ] Linting tools pass without errors
- [ ] Automated formatting configured
- [ ] Pre-commit hooks installed
- [ ] Style guide documentation updated
            """.strip(),
        }
        
        return criteria.get(category, "- [ ] All issues in category resolved\n- [ ] No new issues introduced\n- [ ] Functionality preserved")
    
    def _get_risk_level(self, severity: Severity) -> str:
        """Get risk level description"""
        mapping = {
            Severity.HIGH: "🔴 CRITICAL",
            Severity.MEDIUM: "🟡 HIGH", 
            Severity.LOW: "🟢 MEDIUM",
            Severity.INFO: "🔵 LOW"
        }
        return mapping.get(severity, "UNKNOWN")
    
    def _get_impact_description(self, category: Category) -> str:
        """Get impact description for each category"""
        impacts = {
            Category.HARDCODED_SECRETS: "Potential unauthorized access, credential exposure in version control, security breaches",
            Category.DOCKER_SECURITY: "Container escape vulnerabilities, privilege escalation, security compliance failures",
            Category.FILE_PERMISSIONS: "Unauthorized access to sensitive data, credential exposure, compliance violations",
            Category.NETWORK_SECURITY: "Unintended network exposure, potential attack surface expansion",
            Category.CODE_STYLE: "Reduced maintainability, increased technical debt, developer productivity impact",
            Category.SHELL_SCRIPTS: "Runtime failures, unexpected behavior, security vulnerabilities",
        }
        return impacts.get(category, "Quality and maintainability impact")
    
    def _get_mitigation_strategy(self, category: Category) -> str:
        """Get mitigation strategy for each category"""
        return "Implement systematic remediation following the implementation plan. Test thoroughly and maintain secure practices."
    
    def _get_required_skills(self, category: Category) -> str:
        """Get required skills for each category"""
        skills = {
            Category.HARDCODED_SECRETS: "Security practices, environment configuration, secret management",
            Category.DOCKER_SECURITY: "Docker/container security, system administration, network configuration", 
            Category.FILE_PERMISSIONS: "Unix/Linux permissions, security administration",
            Category.CODE_STYLE: "Code formatting, linting tools, development practices",
            Category.SHELL_SCRIPTS: "Shell scripting, error handling, system administration",
        }
        return skills.get(category, "General development and security practices")
    
    def _get_required_tools(self, category: Category) -> str:
        """Get required tools for each category"""
        tools = {
            Category.HARDCODED_SECRETS: "Environment management, secret scanners, secure vaults",
            Category.DOCKER_SECURITY: "Docker, docker-compose, security scanning tools",
            Category.FILE_PERMISSIONS: "chmod, security audit tools",
            Category.CODE_STYLE: "Linters (pylint, flake8), formatters (black, prettier)",
            Category.SHELL_SCRIPTS: "shellcheck, bash, testing frameworks",
        }
        return tools.get(category, "Standard development tools")
    
    def _get_related_categories(self, category: Category) -> str:
        """Get related issue categories"""
        related = {
            Category.HARDCODED_SECRETS: "- Docker Security (environment variables)\n- File Permissions (secure storage)",
            Category.DOCKER_SECURITY: "- Network Security (container networking)\n- File Permissions (container filesystem)",
            Category.CODE_STYLE: "- Code Complexity (refactoring)\n- Documentation (code comments)",
        }
        return related.get(category, "No directly related categories identified")


def main():
    """Main function to generate sub-issue templates"""
    # Load issue tracker data
    tracker = IssueTracker()
    tracker.load_issues()
    
    # Generate templates
    generator = SubIssueTemplateGenerator(tracker)
    print("Generating actionable sub-issue templates...")
    generator.generate_all_templates()
    
    print(f"\nGenerated {len(tracker.issue_groups)} sub-issue templates")
    print(f"Templates saved to: {generator.templates_dir}")
    
    # Create index file
    index_content = "# Actionable Sub-Issue Templates\n\n"
    index_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    index_content += "## Available Templates\n\n"
    
    for i, group in enumerate(tracker.issue_groups, 1):
        filename = f"{group.group_id.lower().replace('-', '_')}.md"
        index_content += f"{i}. **[{group.title}]({filename})** ({group.severity.value} priority)\n"
        index_content += f"   - {len(group.issues)} issues\n"
        index_content += f"   - Category: {group.category.value}\n\n"
    
    with open(f"{generator.templates_dir}/README.md", 'w') as f:
        f.write(index_content)
    
    print(f"Index created: {generator.templates_dir}/README.md")


if __name__ == "__main__":
    main()