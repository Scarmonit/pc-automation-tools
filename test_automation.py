#!/usr/bin/env python3
"""
Tests for GitHub Automation functionality
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import our modules
from github_automation import GitHubAPI, BugReport, AutoSubmitter
from merge_automation import MergeAutomation


class TestGitHubAPI(unittest.TestCase):
    """Test GitHub API functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.api = GitHubAPI(token="test_token", repo="test/repo")
    
    def test_bug_report_creation(self):
        """Test BugReport dataclass"""
        bug = BugReport(
            title="Test Bug",
            description="Test description",
            severity="high",
            file_path="/test/file.py",
            line_number=42
        )
        
        self.assertEqual(bug.title, "Test Bug")
        self.assertEqual(bug.severity, "high")
        self.assertEqual(bug.line_number, 42)
        self.assertEqual(bug.tags, [])  # Default empty list
    
    def test_api_headers(self):
        """Test API headers are correctly set"""
        self.assertIn('Authorization', self.api.headers)
        self.assertEqual(self.api.headers['Authorization'], 'token test_token')
        self.assertEqual(self.api.repo, 'test/repo')
    
    @patch('requests.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'number': 1, 'title': 'Test Issue'}
        mock_response.content = True
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        result = self.api._make_request('POST', 'test/endpoint', {'test': 'data'})
        
        self.assertEqual(result['number'], 1)
        mock_request.assert_called_once()
    
    @patch('requests.request')
    def test_create_issue(self, mock_request):
        """Test issue creation"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'number': 123, 'title': 'Test Bug'}
        mock_response.content = True
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        bug = BugReport(
            title="Test Bug",
            description="Test description",
            severity="medium"
        )
        
        issue = self.api.create_issue(bug)
        
        self.assertEqual(issue['number'], 123)
        self.assertEqual(issue['title'], 'Test Bug')


class TestAutoSubmitter(unittest.TestCase):
    """Test AutoSubmitter functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Set dry run mode for tests
        os.environ['DRY_RUN'] = 'true'
        self.submitter = AutoSubmitter(github_token="test_token", repo="test/repo")
    
    def test_parse_audit_report(self):
        """Test parsing of audit report"""
        # Create a temporary audit report with correct format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Code Quality Audit Report

## Detailed Findings

**47. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_openhands.sh`

**48. Python Code**
- Description: Unused import detected
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/module.py`
- Line: 5
""")
            report_file = f.name
        
        try:
            bugs = self.submitter._parse_audit_report(report_file)
            
            # Should have parsed 2 bugs
            self.assertEqual(len(bugs), 2)
            
            # Check first bug
            self.assertEqual(bugs[0].title, 'Code Quality: Missing "set -e" for error handling')
            self.assertEqual(bugs[0].file_path, '/home/runner/work/pc-automation-tools/pc-automation-tools/install_openhands.sh')
            
            # Check second bug
            self.assertEqual(bugs[1].title, 'Code Quality: Unused import detected')
            self.assertEqual(bugs[1].file_path, '/home/runner/work/pc-automation-tools/pc-automation-tools/module.py')
            self.assertEqual(bugs[1].line_number, 5)
            
        finally:
            os.unlink(report_file)
    
    def test_parse_security_report(self):
        """Test parsing of security report"""
        # Create a temporary security report with correct format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Security Audit Report

## Detailed Findings

### HIGH Severity

**1. Hardcoded Secrets**
- Description: Potential password found: password = "test123"
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/config.py`
- Line: 10
""")
            report_file = f.name
        
        try:
            bugs = self.submitter._parse_security_report(report_file)
            
            # Should have parsed 1 security bug
            self.assertEqual(len(bugs), 1)
            
            # Check security bug
            self.assertEqual(bugs[0].title, 'Security: Potential password found: password = "test123"')
            self.assertEqual(bugs[0].severity, 'high')  # Should be high since it's under HIGH Severity
            self.assertIn('security', bugs[0].tags)
            self.assertEqual(bugs[0].line_number, 10)
            
        finally:
            os.unlink(report_file)


class TestMergeAutomation(unittest.TestCase):
    """Test MergeAutomation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Set dry run mode for tests
        os.environ['DRY_RUN'] = 'true'
        self.automation = MergeAutomation(github_token="test_token", repo="test/repo")
    
    def test_fix_shell_script(self):
        """Test shell script fixing"""
        # Create a temporary shell script without set -e
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write("""#!/bin/bash
echo "Hello World"
""")
            script_path = Path(f.name)
        
        try:
            # Fix the script
            result = self.automation._fix_shell_script(script_path)
            self.assertTrue(result)
            
            # Check that set -e was added
            with open(script_path, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            self.assertEqual(lines[0], '#!/bin/bash')
            self.assertEqual(lines[1], 'set -e')
            self.assertEqual(lines[2], 'echo "Hello World"')
            
        finally:
            script_path.unlink()
    
    def test_fix_shell_script_already_fixed(self):
        """Test shell script that already has set -e"""
        # Create a temporary shell script with set -e
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write("""#!/bin/bash
set -e
echo "Hello World"
""")
            script_path = Path(f.name)
        
        try:
            # Try to fix the script (should return False as no changes needed)
            result = self.automation._fix_shell_script(script_path)
            self.assertFalse(result)
            
        finally:
            script_path.unlink()
    
    def test_fix_python_imports(self):
        """Test Python import fixing"""
        # Create a temporary Python file with unsorted imports
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""import requests
import os
import sys
from pathlib import Path

def main():
    pass
""")
            py_path = Path(f.name)
        
        try:
            # Fix the imports
            result = self.automation._fix_python_imports(py_path)
            self.assertTrue(result)
            
            # Check that imports were sorted
            with open(py_path, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            # Standard library imports should come first
            self.assertIn('import os', lines[0:3])
            self.assertIn('import sys', lines[0:3])
            
        finally:
            py_path.unlink()


def run_tests():
    """Run all tests"""
    print("🧪 Running GitHub Automation Tests...")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestGitHubAPI))
    suite.addTest(unittest.makeSuite(TestAutoSubmitter))
    suite.addTest(unittest.makeSuite(TestMergeAutomation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return False


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)