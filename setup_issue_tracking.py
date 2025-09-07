#!/usr/bin/env python3
"""
Issue Tracking System Setup

This script sets up the complete security and code quality issue tracking system
for the PC Automation Tools repository.
"""

import os
import sys
import subprocess
from datetime import datetime


def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"Running: {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def check_dependencies():
    """Check if required dependencies are available"""
    print("Checking dependencies...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print("❌ Python 3.6+ required")
        return False
    print(f"✓ Python {python_version.major}.{python_version.minor}")
    
    # Check required modules
    required_modules = ['json', 'yaml', 're', 'os', 'datetime', 'dataclasses', 'enum', 'typing']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing modules: {', '.join(missing_modules)}")
        return False
    
    print("✓ All required modules available")
    return True


def setup_issue_tracking():
    """Set up the complete issue tracking system"""
    print("\n" + "="*60)
    print("Setting up Security & Code Quality Issue Tracking System")
    print("="*60)
    
    if not check_dependencies():
        print("❌ Dependency check failed")
        return False
    
    # Step 1: Initialize issue tracker and parse audit reports
    print("\n1. Initializing issue tracker...")
    if not run_command("python3 issue_tracker.py", "Parse audit reports and create issue database"):
        print("❌ Failed to initialize issue tracker")
        return False
    
    # Step 2: Generate actionable sub-issue templates
    print("\n2. Generating actionable sub-issue templates...")
    if not run_command("python3 sub_issue_generator.py", "Create detailed templates for each issue category"):
        print("❌ Failed to generate templates")
        return False
    
    # Step 3: Generate initial progress report
    print("\n3. Generating initial progress report...")
    if not run_command("python3 issue_progress_updater.py report", "Create baseline progress report"):
        print("❌ Failed to generate progress report")
        return False
    
    # Step 4: Verify setup
    print("\n4. Verifying setup...")
    
    # Check that all expected files exist
    expected_files = [
        "issue_tracking/all_issues.json",
        "issue_tracking/issue_groups.yaml", 
        "issue_tracking/summary_report.md",
        "issue_tracking/sub_issues/README.md",
        "issue_tracking/progress_report.md",
        "ISSUE_TRACKING_DASHBOARD.md"
    ]
    
    all_files_exist = True
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_files_exist = False
    
    if not all_files_exist:
        print("❌ Setup verification failed - missing files")
        return False
    
    # Count issues and templates
    try:
        import json
        with open("issue_tracking/all_issues.json", 'r') as f:
            issues = json.load(f)
        
        templates_dir = "issue_tracking/sub_issues"
        template_count = len([f for f in os.listdir(templates_dir) if f.endswith('.md') and f != 'README.md'])
        
        print(f"\n✓ Setup complete!")
        print(f"  - {len(issues)} issues tracked")
        print(f"  - {template_count} actionable templates created")
        print(f"  - Complete dashboard and progress tracking ready")
        
    except Exception as e:
        print(f"❌ Error verifying setup: {e}")
        return False
    
    return True


def print_usage_instructions():
    """Print instructions for using the tracking system"""
    print("\n" + "="*60)
    print("ISSUE TRACKING SYSTEM - USAGE INSTRUCTIONS")
    print("="*60)
    
    print("""
🎯 QUICK START:

1. View the main dashboard:
   cat ISSUE_TRACKING_DASHBOARD.md

2. Check high-priority issues:
   python3 issue_progress_updater.py high-priority

3. Generate current progress report:
   python3 issue_progress_updater.py report

4. Update issue status:
   python3 issue_progress_updater.py status SEC-HIGH-001 in_progress "Started remediation"

5. Bulk update category:
   python3 issue_progress_updater.py category "Hardcoded Secrets" completed "Fixed all hardcoded secrets"

📁 KEY FILES:

- ISSUE_TRACKING_DASHBOARD.md          - Main overview and navigation
- issue_tracking/summary_report.md     - Current status summary  
- issue_tracking/sub_issues/           - Detailed remediation templates
- issue_tracking/progress_report.md    - Progress tracking
- issue_tracking/all_issues.json       - Complete issue database

🔧 AVAILABLE COMMANDS:

- python3 issue_tracker.py             - Regenerate issue database from audit reports
- python3 sub_issue_generator.py       - Regenerate actionable templates
- python3 issue_progress_updater.py    - Update progress and generate reports

📋 WORKFLOW:

1. Start with HIGH severity issues (Hardcoded Secrets)
2. Follow the detailed templates in issue_tracking/sub_issues/
3. Update progress using the progress updater
4. Generate regular progress reports
5. Move systematically through priority categories

🚨 PRIORITY ORDER:
1. Hardcoded Secrets (CRITICAL)
2. Docker Security (HIGH)
3. File Permissions (HIGH)  
4. Dependency Security (MEDIUM)
5. Code Style & Quality (MEDIUM)
6. Documentation & Structure (LOW)
""")


def main():
    """Main function"""
    print("PC Automation Tools - Issue Tracking System Setup")
    print(f"Setup started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not setup_issue_tracking():
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    
    print_usage_instructions()
    
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE - Issue tracking system is ready!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review ISSUE_TRACKING_DASHBOARD.md")
    print("2. Start with hardcoded secrets remediation")
    print("3. Update progress as you work")


if __name__ == "__main__":
    main()