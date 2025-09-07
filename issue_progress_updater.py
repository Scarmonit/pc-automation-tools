#!/usr/bin/env python3
"""
Issue Progress Updater

Simple utility to update issue status and track progress
on security and code quality remediation efforts.
"""

import json
import yaml
import os
from datetime import datetime
from typing import List, Dict, Optional
from issue_tracker import IssueTracker, Status, Severity


class ProgressUpdater:
    """Utility for updating and tracking issue remediation progress"""
    
    def __init__(self, data_dir: str = "issue_tracking"):
        self.data_dir = data_dir
        self.issues_file = os.path.join(data_dir, "all_issues.json")
        self.groups_file = os.path.join(data_dir, "issue_groups.yaml")
        self.progress_file = os.path.join(data_dir, "progress_log.json")
        self.issues = []
        self.progress_log = []
        self._load_data()
    
    def _load_data(self):
        """Load existing issue data"""
        if os.path.exists(self.issues_file):
            with open(self.issues_file, 'r') as f:
                self.issues = json.load(f)
        
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                self.progress_log = json.load(f)
    
    def update_issue_status(self, issue_id: str, new_status: str, notes: str = "", assigned_to: str = ""):
        """Update the status of a specific issue"""
        issue_found = False
        
        for issue in self.issues:
            if issue['id'] == issue_id:
                old_status = issue['status']
                issue['status'] = new_status
                
                if assigned_to:
                    issue['assigned_to'] = assigned_to
                
                # Log the change
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "issue_id": issue_id,
                    "old_status": old_status,
                    "new_status": new_status,
                    "notes": notes,
                    "updated_by": assigned_to or "system"
                }
                self.progress_log.append(log_entry)
                
                issue_found = True
                print(f"✓ Updated {issue_id}: {old_status} → {new_status}")
                break
        
        if not issue_found:
            print(f"❌ Issue {issue_id} not found")
            return False
        
        self._save_data()
        return True
    
    def bulk_update_category(self, category: str, new_status: str, notes: str = ""):
        """Update all issues in a specific category"""
        updated_count = 0
        
        for issue in self.issues:
            if issue['category'] == category:
                old_status = issue['status']
                if old_status != new_status:
                    issue['status'] = new_status
                    
                    log_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "issue_id": issue['id'],
                        "old_status": old_status,
                        "new_status": new_status,
                        "notes": f"Bulk update: {notes}",
                        "updated_by": "bulk_update"
                    }
                    self.progress_log.append(log_entry)
                    updated_count += 1
        
        print(f"✓ Updated {updated_count} issues in category '{category}' to '{new_status}'")
        self._save_data()
        return updated_count
    
    def get_progress_summary(self) -> Dict:
        """Get current progress summary"""
        status_counts = {}
        severity_progress = {}
        category_progress = {}
        
        for issue in self.issues:
            # Count by status
            status = issue['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by severity
            severity = issue['severity']
            if severity not in severity_progress:
                severity_progress[severity] = {'total': 0, 'completed': 0}
            severity_progress[severity]['total'] += 1
            if status == 'completed':
                severity_progress[severity]['completed'] += 1
            
            # Count by category
            category = issue['category']
            if category not in category_progress:
                category_progress[category] = {'total': 0, 'completed': 0}
            category_progress[category]['total'] += 1
            if status == 'completed':
                category_progress[category]['completed'] += 1
        
        return {
            'total_issues': len(self.issues),
            'status_counts': status_counts,
            'severity_progress': severity_progress,
            'category_progress': category_progress,
            'completion_percentage': round((status_counts.get('completed', 0) / len(self.issues)) * 100, 1) if self.issues else 0
        }
    
    def generate_progress_report(self) -> str:
        """Generate a detailed progress report"""
        summary = self.get_progress_summary()
        
        report = f"""# Issue Remediation Progress Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Issues:** {summary['total_issues']}
**Completion:** {summary['completion_percentage']}%

## Status Overview

"""
        
        # Status breakdown
        for status, count in summary['status_counts'].items():
            percentage = round((count / summary['total_issues']) * 100, 1)
            report += f"- **{status.title()}:** {count} issues ({percentage}%)\n"
        
        report += "\n## Progress by Severity\n\n"
        
        # Severity progress
        for severity, data in summary['severity_progress'].items():
            completed = data['completed']
            total = data['total']
            percentage = round((completed / total) * 100, 1) if total > 0 else 0
            status_icon = "✅" if percentage == 100 else "🔄" if percentage > 0 else "⏳"
            
            report += f"{status_icon} **{severity}:** {completed}/{total} completed ({percentage}%)\n"
        
        report += "\n## Progress by Category\n\n"
        
        # Category progress
        sorted_categories = sorted(summary['category_progress'].items(), 
                                 key=lambda x: x[1]['completed'] / x[1]['total'] if x[1]['total'] > 0 else 0, 
                                 reverse=True)
        
        for category, data in sorted_categories:
            completed = data['completed']
            total = data['total']
            percentage = round((completed / total) * 100, 1) if total > 0 else 0
            status_icon = "✅" if percentage == 100 else "🔄" if percentage > 0 else "⏳"
            
            report += f"{status_icon} **{category}:** {completed}/{total} completed ({percentage}%)\n"
        
        # Recent activity
        if self.progress_log:
            report += "\n## Recent Activity (Last 10 Updates)\n\n"
            recent_updates = sorted(self.progress_log, key=lambda x: x['timestamp'], reverse=True)[:10]
            
            for update in recent_updates:
                timestamp = datetime.fromisoformat(update['timestamp']).strftime('%Y-%m-%d %H:%M')
                report += f"- **{timestamp}:** {update['issue_id']} → {update['new_status']}"
                if update['notes']:
                    report += f" ({update['notes']})"
                report += "\n"
        
        return report
    
    def list_issues_by_status(self, status: str = "open") -> List[Dict]:
        """List all issues with a specific status"""
        return [issue for issue in self.issues if issue['status'] == status]
    
    def list_high_priority_issues(self) -> List[Dict]:
        """List all high priority (HIGH severity) issues"""
        return [issue for issue in self.issues if 'HIGH' in issue['severity'] and 'OPEN' in issue['status']]
    
    def _save_data(self):
        """Save updated data to files"""
        # Save issues
        with open(self.issues_file, 'w') as f:
            json.dump(self.issues, f, indent=2)
        
        # Save progress log
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress_log, f, indent=2)


def main():
    """Main CLI interface for progress updates"""
    import sys
    
    updater = ProgressUpdater()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 issue_progress_updater.py status <issue_id> <new_status> [notes]")
        print("  python3 issue_progress_updater.py category <category> <new_status> [notes]")
        print("  python3 issue_progress_updater.py report")
        print("  python3 issue_progress_updater.py summary")
        print("  python3 issue_progress_updater.py high-priority")
        print("")
        print("Status options: open, in_progress, completed, deferred, wont_fix")
        return
    
    command = sys.argv[1]
    
    if command == "status" and len(sys.argv) >= 4:
        issue_id = sys.argv[2]
        new_status = sys.argv[3]
        notes = sys.argv[4] if len(sys.argv) > 4 else ""
        updater.update_issue_status(issue_id, new_status, notes)
    
    elif command == "category" and len(sys.argv) >= 4:
        category = sys.argv[2]
        new_status = sys.argv[3]
        notes = sys.argv[4] if len(sys.argv) > 4 else ""
        updater.bulk_update_category(category, new_status, notes)
    
    elif command == "report":
        report = updater.generate_progress_report()
        print(report)
        
        # Save report to file
        report_file = os.path.join(updater.data_dir, "progress_report.md")
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")
    
    elif command == "summary":
        summary = updater.get_progress_summary()
        print(f"Total Issues: {summary['total_issues']}")
        print(f"Completion: {summary['completion_percentage']}%")
        print("\nStatus Breakdown:")
        for status, count in summary['status_counts'].items():
            print(f"  {status}: {count}")
    
    elif command == "high-priority":
        high_priority = updater.list_high_priority_issues()
        print(f"High Priority Issues ({len(high_priority)} remaining):")
        for issue in high_priority:
            print(f"  {issue['id']}: {issue['title']}")
    
    else:
        print("Invalid command or arguments")


if __name__ == "__main__":
    main()