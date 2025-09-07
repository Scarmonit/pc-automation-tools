#!/usr/bin/env python3
"""
Auto Submit CLI
Command-line interface for auto-submitting bugs and creating merge requests
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from github_automation import AutoSubmitter
from merge_automation import MergeAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_requirements():
    """Check if required environment variables and files are present"""
    missing = []
    
    # Check for GitHub token
    if not os.getenv('GITHUB_TOKEN'):
        missing.append("GITHUB_TOKEN environment variable")
    
    # Check for git repository
    if not Path('.git').exists():
        missing.append("Git repository (not in a git directory)")
    
    if missing:
        logger.error("Missing requirements:")
        for item in missing:
            logger.error(f"  - {item}")
        logger.info("\nTo set up GitHub token:")
        logger.info("1. Create a personal access token at https://github.com/settings/tokens")
        logger.info("2. Set GITHUB_TOKEN environment variable or add to .env file")
        logger.info("3. Ensure token has 'repo' and 'issues' permissions")
        return False
    
    return True


def submit_bugs_command(args):
    """Handle bug submission command"""
    logger.info("🐛 Starting bug auto-submission...")
    
    submitter = AutoSubmitter()
    
    total_issues = 0
    
    if args.type in ['code', 'all']:
        logger.info("Submitting code quality bugs...")
        issues = submitter.submit_audit_bugs(args.audit_report)
        total_issues += len(issues)
        logger.info(f"✅ Submitted {len(issues)} code quality issues")
    
    if args.type in ['security', 'all']:
        logger.info("Submitting security bugs...")
        issues = submitter.submit_security_bugs(args.security_report)
        total_issues += len(issues)
        logger.info(f"✅ Submitted {len(issues)} security issues")
    
    logger.info(f"🎉 Total issues submitted: {total_issues}")


def submit_merges_command(args):
    """Handle merge request creation command"""
    logger.info("🔀 Starting merge request auto-creation...")
    
    automation = MergeAutomation()
    
    created_prs = []
    
    if args.type in ['shell', 'all']:
        logger.info("Creating shell script fixes...")
        pr_url = automation.auto_fix_shell_scripts()
        if pr_url:
            created_prs.append(pr_url)
    
    if args.type in ['python', 'all']:
        logger.info("Creating Python import fixes...")
        pr_url = automation.auto_fix_python_imports()
        if pr_url:
            created_prs.append(pr_url)
    
    if created_prs:
        logger.info(f"🎉 Created {len(created_prs)} pull requests:")
        for i, pr_url in enumerate(created_prs, 1):
            logger.info(f"  {i}. {pr_url}")
    else:
        logger.info("ℹ️ No pull requests created (no fixes needed or dry run mode)")


def run_full_automation(args):
    """Run both bug submission and merge creation"""
    logger.info("🚀 Starting full automation workflow...")
    
    # First submit bugs
    logger.info("\n" + "="*50)
    logger.info("PHASE 1: Bug Submission")
    logger.info("="*50)
    submit_bugs_command(args)
    
    # Then create merge requests
    logger.info("\n" + "="*50)
    logger.info("PHASE 2: Merge Request Creation")
    logger.info("="*50)
    submit_merges_command(args)
    
    logger.info("\n🎉 Full automation workflow completed!")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='Auto-submit bugs and create merge requests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s bugs --type all                    # Submit all bug types
  %(prog)s bugs --type security --dry-run    # Preview security bugs
  %(prog)s merges --type shell               # Create shell script fixes
  %(prog)s auto                              # Run full automation
  
Environment Setup:
  Set GITHUB_TOKEN environment variable or create .env file
  with your GitHub personal access token.
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Bugs command
    bugs_parser = subparsers.add_parser('bugs', help='Submit bug reports to GitHub')
    bugs_parser.add_argument('--type', choices=['code', 'security', 'all'], default='all',
                            help='Type of bugs to submit (default: all)')
    bugs_parser.add_argument('--audit-report', default='code_quality_audit_report.md',
                            help='Path to code quality audit report')
    bugs_parser.add_argument('--security-report', default='security_audit_report.md',
                            help='Path to security audit report')
    bugs_parser.add_argument('--dry-run', action='store_true',
                            help='Preview what would be submitted without actually doing it')
    
    # Merges command
    merges_parser = subparsers.add_parser('merges', help='Create merge requests for fixes')
    merges_parser.add_argument('--type', choices=['shell', 'python', 'all'], default='all',
                              help='Type of fixes to create (default: all)')
    merges_parser.add_argument('--dry-run', action='store_true',
                              help='Preview what would be created without actually doing it')
    
    # Auto command
    auto_parser = subparsers.add_parser('auto', help='Run full automation (bugs + merges)')
    auto_parser.add_argument('--audit-report', default='code_quality_audit_report.md',
                            help='Path to code quality audit report')
    auto_parser.add_argument('--security-report', default='security_audit_report.md',
                            help='Path to security audit report')
    auto_parser.add_argument('--dry-run', action='store_true',
                            help='Preview what would be done without actually doing it')
    
    # Global options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set verbose logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set dry run environment variable
    if hasattr(args, 'dry_run') and args.dry_run:
        os.environ['DRY_RUN'] = 'true'
        logger.info("🔍 DRY RUN MODE: No actual changes will be made")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Route to appropriate command
    if args.command == 'bugs':
        submit_bugs_command(args)
    elif args.command == 'merges':
        submit_merges_command(args)
    elif args.command == 'auto':
        run_full_automation(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()