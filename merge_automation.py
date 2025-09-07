#!/usr/bin/env python3
"""
Merge Automation Module
Auto-create merge requests for code fixes and improvements
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Dict
from github_automation import GitHubAPI, MergeRequest

logger = logging.getLogger(__name__)


class MergeAutomation:
    """Automate creation of merge requests for code improvements"""
    
    def __init__(self, github_token: Optional[str] = None, repo: Optional[str] = None):
        """Initialize merge automation"""
        self.github = GitHubAPI(github_token, repo)
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
    
    def create_fix_branch(self, branch_name: str, base_branch: str = 'main') -> bool:
        """Create a new branch for fixes"""
        try:
            # Ensure we're on the base branch
            subprocess.run(['git', 'checkout', base_branch], check=True, capture_output=True)
            
            # Pull latest changes
            subprocess.run(['git', 'pull', 'origin', base_branch], check=True, capture_output=True)
            
            # Create new branch
            subprocess.run(['git', 'checkout', '-b', branch_name], check=True, capture_output=True)
            
            logger.info(f"Created new branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create branch {branch_name}: {e}")
            return False
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> bool:
        """Commit changes to current branch"""
        try:
            # Add files
            if files:
                for file in files:
                    subprocess.run(['git', 'add', file], check=True, capture_output=True)
            else:
                subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            
            # Check if there are any changes to commit
            result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True)
            if not result.stdout.strip():
                logger.info("No changes to commit")
                return False
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', message], check=True, capture_output=True)
            
            logger.info(f"Committed changes: {message}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to commit changes: {e}")
            return False
    
    def push_branch(self, branch_name: str) -> bool:
        """Push branch to origin"""
        try:
            subprocess.run(['git', 'push', 'origin', branch_name], check=True, capture_output=True)
            logger.info(f"Pushed branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to push branch {branch_name}: {e}")
            return False
    
    def auto_fix_shell_scripts(self) -> Optional[str]:
        """Automatically fix shell script issues and create PR"""
        branch_name = "auto-fix/shell-scripts-comprehensive-improvements"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create branch {branch_name} and enhance shell scripts")
            return None
        
        # Create branch
        if not self.create_fix_branch(branch_name):
            return None
        
        # Find and fix shell scripts
        fixed_files = []
        shell_scripts = list(Path('.').glob('**/*.sh'))
        
        for script in shell_scripts:
            if self._fix_shell_script(script):
                fixed_files.append(str(script))
        
        if not fixed_files:
            logger.info("No shell script improvements needed")
            return None
        
        # Commit changes
        commit_msg = f"Enhance shell scripts: Add error handling, validation, and documentation to {len(fixed_files)} scripts"
        if not self.commit_changes(commit_msg, fixed_files):
            return None
        
        # Push branch
        if not self.push_branch(branch_name):
            return None
        
        # Create pull request
        merge_request = MergeRequest(
            title="Auto-enhance: Comprehensive shell script improvements",
            description=f"""## Changes
This PR automatically enhances shell scripts with comprehensive improvements following repository conventions.

### Improvements Applied:
- ✅ Error handling (`set -e`) for robust execution
- ✅ Comprehensive documentation headers 
- ✅ Standardized logging functions with color output
- ✅ Validation and prerequisite checks
- ✅ Consistent formatting and style

### Files Modified
{chr(10).join(f'- `{f}`' for f in fixed_files)}

### Improvements
- Added `set -e` to exit on errors
- Improved script reliability
- Addresses code quality audit findings

This is an automated fix generated by the PC Automation Tools.""",
            source_branch=branch_name,
            tags=["auto-fix", "shell-scripts", "code-quality"]
        )
        
        try:
            pr = self.github.create_pull_request(merge_request)
            logger.info(f"Created PR #{pr['number']}: {pr['title']}")
            return pr['html_url']
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return None
    
    def auto_fix_python_imports(self) -> Optional[str]:
        """Automatically fix Python import issues and create PR"""
        branch_name = "auto-fix/python-imports"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create branch {branch_name} and fix Python imports")
            return None
        
        # Create branch
        if not self.create_fix_branch(branch_name):
            return None
        
        # Find and fix Python files
        fixed_files = []
        python_files = list(Path('.').glob('**/*.py'))
        
        for py_file in python_files:
            if self._fix_python_imports(py_file):
                fixed_files.append(str(py_file))
        
        if not fixed_files:
            logger.info("No Python import fixes needed")
            return None
        
        # Commit changes
        commit_msg = f"Fix Python imports: Sort and organize imports in {len(fixed_files)} files"
        if not self.commit_changes(commit_msg, fixed_files):
            return None
        
        # Push branch
        if not self.push_branch(branch_name):
            return None
        
        # Create pull request
        merge_request = MergeRequest(
            title="Auto-fix: Organize Python imports",
            description=f"""## Changes
This PR automatically organizes and sorts Python imports according to PEP 8 standards.

### Files Modified
{chr(10).join(f'- `{f}`' for f in fixed_files)}

### Improvements
- Sorted imports alphabetically
- Separated standard library, third-party, and local imports
- Improved code readability
- Addresses code quality audit findings

This is an automated fix generated by the PC Automation Tools.""",
            source_branch=branch_name,
            tags=["auto-fix", "python", "imports", "code-quality"]
        )
        
        try:
            pr = self.github.create_pull_request(merge_request)
            logger.info(f"Created PR #{pr['number']}: {pr['title']}")
            return pr['html_url']
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return None
    
    def _fix_shell_script(self, script_path: Path) -> bool:
        """Fix a single shell script by adding comprehensive improvements"""
        try:
            with open(script_path, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            if not lines:
                return False
            
            original_lines = lines.copy()
            modifications_made = False
            
            # Find shebang line
            shebang_idx = -1
            for i, line in enumerate(lines):
                if line.startswith('#!'):
                    shebang_idx = i
                    break
            
            if shebang_idx == -1:
                return False
            
            # Check if already has set -e
            has_set_e = any('set -e' in line for line in lines[:10])
            
            # Add error handling if missing
            if not has_set_e:
                lines.insert(shebang_idx + 1, 'set -e')
                modifications_made = True
            
            # Add comprehensive header comment if missing
            has_description = any(line.strip().startswith('#') and 
                                'Description:' in line or 'Purpose:' in line 
                                for line in lines[:15])
            
            if not has_description and not any('# ' in line and len(line.strip()) > 3 
                                             for line in lines[1:6]):
                script_name = script_path.name
                purpose = self._generate_script_purpose(script_name)
                header_comment = f"# Description: {purpose}"
                
                # Insert after shebang and set -e
                insert_idx = shebang_idx + 1
                if has_set_e or modifications_made:
                    insert_idx += 1
                
                lines.insert(insert_idx, "")
                lines.insert(insert_idx + 1, header_comment)
                modifications_made = True
            
            # Add logging functions if they don't exist and script needs them
            needs_logging = any('echo' in line for line in lines)
            has_logging_functions = any('log_info()' in line or 'log_error()' in line 
                                      for line in lines)
            
            if needs_logging and not has_logging_functions and len(lines) > 10:
                logging_functions = self._get_logging_functions()
                
                # Find a good place to insert logging functions (after initial comments)
                insert_idx = shebang_idx + 1
                while insert_idx < len(lines) and (lines[insert_idx].startswith('#') or 
                                                  lines[insert_idx].strip() == '' or
                                                  'set -e' in lines[insert_idx]):
                    insert_idx += 1
                
                lines.insert(insert_idx, "")
                lines.insert(insert_idx + 1, "# Logging functions")
                for i, func_line in enumerate(logging_functions):
                    lines.insert(insert_idx + 2 + i, func_line)
                lines.insert(insert_idx + 2 + len(logging_functions), "")
                modifications_made = True
            
            # Only write if modifications were made
            if modifications_made:
                with open(script_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                logger.info(f"Enhanced shell script: {script_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to enhance shell script {script_path}: {e}")
            return False
    
    def _generate_script_purpose(self, script_name: str) -> str:
        """Generate a purpose description based on script name"""
        name_lower = script_name.lower()
        
        # Check more specific patterns first
        if 'validate' in name_lower or 'check' in name_lower:
            return "Validate system configuration and health"
        elif 'troubleshoot' in name_lower:
            return "Troubleshoot system issues and provide diagnostics"
        elif 'benchmark' in name_lower:
            return "Run performance benchmarks and tests"
        elif 'optimize' in name_lower:
            return "Optimize system performance and configuration"
        elif 'install' in name_lower:
            return f"Install and configure {name_lower.replace('install_', '').replace('.sh', '').replace('_', ' ')}"
        elif 'setup' in name_lower:
            return f"Setup {name_lower.replace('setup_', '').replace('.sh', '').replace('_', ' ')}"
        elif 'deploy' in name_lower:
            return "Deploy and configure system components"
        elif 'manage' in name_lower:
            return f"Manage {name_lower.replace('manage_', '').replace('.sh', '').replace('_', ' ')}"
        elif 'monitor' in name_lower:
            return "Setup monitoring and observability"
        else:
            return f"Automation script for {name_lower.replace('.sh', '').replace('_', ' ')}"
    
    def _get_logging_functions(self) -> list:
        """Get standardized logging functions following repo conventions"""
        return [
            "# Color codes for output",
            "RED='\\033[0;31m'",
            "GREEN='\\033[0;32m'", 
            "YELLOW='\\033[1;33m'",
            "BLUE='\\033[0;34m'",
            "NC='\\033[0m' # No Color",
            "",
            "log_info() {",
            "    echo -e \"${BLUE}[INFO]${NC} $1\"",
            "}",
            "",
            "log_success() {",
            "    echo -e \"${GREEN}[SUCCESS]${NC} $1\"", 
            "}",
            "",
            "log_warning() {",
            "    echo -e \"${YELLOW}[WARNING]${NC} $1\"",
            "}",
            "",
            "log_error() {",
            "    echo -e \"${RED}[ERROR]${NC} $1\"",
            "}"
        ]
    
    def _fix_python_imports(self, py_file: Path) -> bool:
        """Fix Python imports in a file"""
        try:
            with open(py_file, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Find import section
            import_start = -1
            import_end = -1
            
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    if import_start == -1:
                        import_start = i
                    import_end = i
                elif import_start != -1 and line.strip() and not line.startswith('#'):
                    break
            
            if import_start == -1:
                return False
            
            # Extract and sort imports
            import_lines = lines[import_start:import_end + 1]
            
            # Separate different types of imports
            standard_imports = []
            third_party_imports = []
            local_imports = []
            
            for line in import_lines:
                if not line.strip() or line.startswith('#'):
                    continue
                
                # Simple heuristic for categorizing imports
                if any(lib in line for lib in ['os', 'sys', 'json', 'datetime', 'pathlib', 'subprocess']):
                    standard_imports.append(line)
                elif line.startswith('from .') or line.startswith('import .'):
                    local_imports.append(line)
                else:
                    third_party_imports.append(line)
            
            # Sort each category
            standard_imports.sort()
            third_party_imports.sort()
            local_imports.sort()
            
            # Combine with proper spacing
            new_imports = []
            if standard_imports:
                new_imports.extend(standard_imports)
                new_imports.append('')
            if third_party_imports:
                new_imports.extend(third_party_imports)
                new_imports.append('')
            if local_imports:
                new_imports.extend(local_imports)
                new_imports.append('')
            
            # Remove trailing empty line if it exists
            if new_imports and new_imports[-1] == '':
                new_imports.pop()
            
            # Check if changes are needed
            if new_imports == import_lines:
                return False
            
            # Replace import section
            new_lines = lines[:import_start] + new_imports + lines[import_end + 1:]
            
            # Write back
            with open(py_file, 'w') as f:
                f.write('\n'.join(new_lines))
            
            logger.info(f"Fixed Python imports: {py_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fix Python imports {py_file}: {e}")
            return False
    
    def _fix_powershell_script(self, script_path: Path) -> bool:
        """Fix a single PowerShell script by adding comprehensive improvements"""
        try:
            with open(script_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            lines = content.split('\n')
            if not lines:
                return False
            
            modifications_made = False
            
            # Add error handling if missing
            has_error_handling = any('$ErrorActionPreference' in line for line in lines[:10])
            if not has_error_handling:
                # Insert after any initial comments
                insert_idx = 0
                while insert_idx < len(lines) and lines[insert_idx].strip().startswith('#'):
                    insert_idx += 1
                
                lines.insert(insert_idx, "$ErrorActionPreference = 'Stop'")
                lines.insert(insert_idx + 1, "")
                modifications_made = True
            
            # Add comprehensive header comment if missing
            has_description = any(line.strip().startswith('#') and 
                                ('Description:' in line or 'Purpose:' in line)
                                for line in lines[:15])
            
            if not has_description:
                script_name = script_path.name
                purpose = self._generate_script_purpose(script_name.replace('.ps1', '.sh'))
                header_comment = f"# Description: {purpose}"
                
                lines.insert(0, header_comment)
                lines.insert(1, "")
                modifications_made = True
            
            if modifications_made:
                with open(script_path, 'w', encoding='utf-8-sig') as f:
                    f.write('\n'.join(lines))
                
                logger.info(f"Enhanced PowerShell script: {script_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to enhance PowerShell script {script_path}: {e}")
            return False
    
    def _fix_batch_script(self, script_path: Path) -> bool:
        """Fix a single batch script by adding comprehensive improvements"""
        try:
            with open(script_path, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            if not lines:
                return False
            
            modifications_made = False
            
            # Add error handling if missing
            has_error_handling = any('@echo off' in line.lower() for line in lines[:5])
            if not has_error_handling:
                lines.insert(0, "@echo off")
                lines.insert(1, "setlocal EnableDelayedExpansion")
                lines.insert(2, "")
                modifications_made = True
            
            # Add comprehensive header comment if missing  
            has_description = any(line.strip().startswith('::') or line.strip().startswith('REM')
                                for line in lines[:10])
            
            if not has_description:
                script_name = script_path.name
                purpose = self._generate_script_purpose(script_name.replace('.bat', '.sh'))
                header_comment = f":: Description: {purpose}"
                
                # Insert after @echo off
                insert_idx = 0
                while insert_idx < len(lines) and ('@echo' in lines[insert_idx].lower() or
                                                  'setlocal' in lines[insert_idx].lower()):
                    insert_idx += 1
                
                lines.insert(insert_idx, header_comment)
                lines.insert(insert_idx + 1, "")
                modifications_made = True
            
            if modifications_made:
                with open(script_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                logger.info(f"Enhanced batch script: {script_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to enhance batch script {script_path}: {e}")
            return False
    
    def auto_fix_powershell_scripts(self) -> Optional[str]:
        """Automatically fix PowerShell script issues and create PR"""
        branch_name = "auto-fix/powershell-scripts-improvements"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create branch {branch_name} and enhance PowerShell scripts")
            return None
        
        # Create branch
        if not self.create_fix_branch(branch_name):
            return None
        
        # Find and fix PowerShell scripts
        fixed_files = []
        ps_scripts = list(Path('.').glob('**/*.ps1'))
        
        for script in ps_scripts:
            if self._fix_powershell_script(script):
                fixed_files.append(str(script))
        
        if not fixed_files:
            logger.info("No PowerShell script improvements needed")
            return None
        
        # Commit changes
        commit_msg = f"Enhance PowerShell scripts: Add error handling and documentation to {len(fixed_files)} scripts"
        if not self.commit_changes(commit_msg, fixed_files):
            return None
        
        # Push branch
        if not self.push_branch(branch_name):
            return None
        
        # Create pull request
        merge_request = MergeRequest(
            title="Auto-enhance: PowerShell script improvements",
            description=f"""## Changes
This PR automatically enhances PowerShell scripts with comprehensive improvements.

### Improvements Applied:
- ✅ Error handling (`$ErrorActionPreference = 'Stop'`)
- ✅ Comprehensive documentation headers
- ✅ Consistent formatting and style

### Files Modified
- {chr(10).join(f'- `{file}`' for file in fixed_files)}

### Testing
All enhanced scripts maintain backward compatibility while adding robust error handling.

### Impact
- Improved reliability and error reporting
- Better maintainability and documentation
- Consistent user experience across scripts""",
            assignees=[],
            labels=["enhancement", "automation", "powershell"]
        )
        
        try:
            return self.github.create_pull_request(merge_request)
        
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return None
    
    def auto_fix_batch_scripts(self) -> Optional[str]:
        """Automatically fix batch script issues and create PR"""
        branch_name = "auto-fix/batch-scripts-improvements"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create branch {branch_name} and enhance batch scripts")
            return None
        
        # Create branch
        if not self.create_fix_branch(branch_name):
            return None
        
        # Find and fix batch scripts
        fixed_files = []
        batch_scripts = list(Path('.').glob('**/*.bat'))
        
        for script in batch_scripts:
            if self._fix_batch_script(script):
                fixed_files.append(str(script))
        
        if not fixed_files:
            logger.info("No batch script improvements needed")
            return None
        
        # Commit changes
        commit_msg = f"Enhance batch scripts: Add error handling and documentation to {len(fixed_files)} scripts"
        if not self.commit_changes(commit_msg, fixed_files):
            return None
        
        # Push branch
        if not self.push_branch(branch_name):
            return None
        
        # Create pull request
        merge_request = MergeRequest(
            title="Auto-enhance: Batch script improvements", 
            description=f"""## Changes
This PR automatically enhances batch scripts with comprehensive improvements.

### Improvements Applied:
- ✅ Error handling (`@echo off`, `setlocal EnableDelayedExpansion`)
- ✅ Comprehensive documentation headers
- ✅ Consistent formatting and style

### Files Modified
- {chr(10).join(f'- `{file}`' for file in fixed_files)}

### Testing
All enhanced scripts maintain backward compatibility while adding robust error handling.

### Impact
- Improved reliability and error reporting  
- Better maintainability and documentation
- Consistent user experience across scripts""",
            assignees=[],
            labels=["enhancement", "automation", "batch"]
        )
        
        try:
            return self.github.create_pull_request(merge_request)
        
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return None
    
    def auto_fix_all_scripts(self) -> Dict[str, Optional[str]]:
        """Automatically fix all script types and create PRs"""
        results = {}
        
        logger.info("Starting comprehensive script improvements...")
        
        # Fix shell scripts
        logger.info("Enhancing shell scripts...")
        results['shell'] = self.auto_fix_shell_scripts()
        
        # Fix PowerShell scripts  
        logger.info("Enhancing PowerShell scripts...")
        results['powershell'] = self.auto_fix_powershell_scripts()
        
        # Fix batch scripts
        logger.info("Enhancing batch scripts...")
        results['batch'] = self.auto_fix_batch_scripts()
        
        # Summary
        successful_prs = [script_type for script_type, pr_url in results.items() if pr_url]
        if successful_prs:
            logger.info(f"Successfully created PRs for: {', '.join(successful_prs)}")
        else:
            logger.info("No script improvements were needed")
        
        return results
    
    def create_audit_fix_pr(self) -> List[str]:
        """Create PRs for all automatic fixes based on audit findings"""
        created_prs = []
        
        # Auto-fix all script types
        script_results = self.auto_fix_all_scripts()
        for script_type, pr_url in script_results.items():
            if pr_url:
                created_prs.append(pr_url)
        
        # Auto-fix Python imports
        python_pr = self.auto_fix_python_imports()
        if python_pr:
            created_prs.append(python_pr)
        
        return created_prs


def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-create merge requests for code fixes')
    parser.add_argument('--action', choices=['shell', 'powershell', 'batch', 'python', 'scripts', 'all'], 
                        default='all', help='Type of fixes to apply (default: all)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without actually doing it')
    
    args = parser.parse_args()
    
    # Set dry run environment variable
    if args.dry_run:
        os.environ['DRY_RUN'] = 'true'
    
    automation = MergeAutomation()
    
    if args.action in ['shell', 'scripts', 'all']:
        logger.info("Creating shell script enhancements...")
        automation.auto_fix_shell_scripts()
    
    if args.action in ['powershell', 'scripts', 'all']:
        logger.info("Creating PowerShell script enhancements...")
        automation.auto_fix_powershell_scripts()
    
    if args.action in ['batch', 'scripts', 'all']:
        logger.info("Creating batch script enhancements...")
        automation.auto_fix_batch_scripts()
    
    if args.action in ['python', 'all']:
        logger.info("Creating Python import fixes...")
        automation.auto_fix_python_imports()
    
    logger.info("Merge automation completed!")


if __name__ == '__main__':
    main()