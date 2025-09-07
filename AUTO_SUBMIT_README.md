# Auto Submit Bugs and Merges

This module provides automated functionality to submit bug reports and create merge requests based on code quality and security audit findings.

## Features

- 🐛 **Auto Bug Submission**: Automatically create GitHub issues from audit report findings
- 🔀 **Auto Merge Requests**: Create pull requests with automated code fixes
- 🔍 **Dry Run Mode**: Preview actions without making actual changes
- 🎯 **Selective Processing**: Choose specific types of bugs or fixes to process
- 📊 **Comprehensive Reporting**: Detailed logging and progress tracking

## Quick Start

### 1. Setup GitHub Token

Create a GitHub personal access token:
1. Go to https://github.com/settings/tokens
2. Create a new token with `repo` and `issues` permissions
3. Set environment variable: `export GITHUB_TOKEN=your_token_here`

### 2. Run Auto Submit

```bash
# Quick automation with helper script
./auto_submit.sh auto

# Or use Python directly
python3 auto_submit.py auto
```

## Usage Examples

### Bug Submission

```bash
# Submit all bug types
python3 auto_submit.py bugs --type all

# Submit only security bugs
python3 auto_submit.py bugs --type security

# Preview what would be submitted (dry run)
python3 auto_submit.py bugs --dry-run --type all
```

### Merge Request Creation

```bash
# Create all automated fixes
python3 auto_submit.py merges --type all

# Create only shell script fixes
python3 auto_submit.py merges --type shell

# Create only Python import fixes
python3 auto_submit.py merges --type python

# Preview changes (dry run)
python3 auto_submit.py merges --dry-run --type all
```

### Full Automation

```bash
# Run complete automation workflow
python3 auto_submit.py auto

# With dry run to preview
python3 auto_submit.py auto --dry-run
```

### Helper Script

```bash
# Run audits only
./auto_submit.sh audit

# Submit bugs
./auto_submit.sh bugs --type security

# Create merges
./auto_submit.sh merges --type shell

# Full automation
./auto_submit.sh auto

# Preview everything
./auto_submit.sh dry-run
```

## Configuration

### Environment Variables

```bash
# Required
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=owner/repository-name

# Optional
DRY_RUN=true                    # Enable dry run mode
LOG_LEVEL=INFO                  # Logging level
```

### .env File Example

```bash
# GitHub Configuration
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=Scarmonit/pc-automation-tools

# Enable dry run mode (optional)
DRY_RUN=false
```

## What Gets Automated

### Bug Types Submitted

**Security Issues (High Priority)**:
- Hardcoded credentials and secrets
- File permission issues
- Docker security problems
- Network exposure issues

**Code Quality Issues (Medium Priority)**:
- Missing error handling in shell scripts
- High cyclomatic complexity
- Unused imports and variables
- Code style violations
- Documentation issues

### Automatic Fixes Created

**Shell Script Improvements**:
- Add `set -e` for error handling
- Fix script permissions
- Improve error handling

**Python Code Improvements**:
- Sort and organize imports
- Fix import order (standard, third-party, local)
- Remove unused imports

## File Structure

```
auto_submit.py          # Main CLI interface
github_automation.py    # GitHub API integration
merge_automation.py     # Merge request automation
auto_submit.sh         # Bash helper script
test_automation.py     # Test suite
```

## API Reference

### GitHubAPI Class

```python
from github_automation import GitHubAPI, BugReport

# Initialize
api = GitHubAPI(token="your_token", repo="owner/repo")

# Create issue
bug = BugReport(title="Bug Title", description="Description")
issue = api.create_issue(bug)

# Create pull request
merge = MergeRequest(title="Fix Title", description="Description", 
                    source_branch="feature", target_branch="main")
pr = api.create_pull_request(merge)
```

### AutoSubmitter Class

```python
from github_automation import AutoSubmitter

# Initialize
submitter = AutoSubmitter()

# Submit bugs from audit reports
submitter.submit_audit_bugs("code_quality_audit_report.md")
submitter.submit_security_bugs("security_audit_report.md")
```

### MergeAutomation Class

```python
from merge_automation import MergeAutomation

# Initialize
automation = MergeAutomation()

# Create automated fixes
automation.auto_fix_shell_scripts()
automation.auto_fix_python_imports()
```

## Testing

Run the test suite:

```bash
python3 test_automation.py
```

Test individual components:

```bash
# Test with dry run
DRY_RUN=true python3 auto_submit.py auto

# Test parsing only
python3 -c "
from github_automation import AutoSubmitter
s = AutoSubmitter()
bugs = s._parse_audit_report('code_quality_audit_report.md')
print(f'Found {len(bugs)} bugs')
"
```

## Troubleshooting

### Common Issues

**GitHub API Rate Limiting**:
- Use dry run mode for testing
- Wait between operations
- Use personal token instead of GitHub Actions token

**Permission Errors**:
- Ensure token has `repo` and `issues` permissions
- Check repository access permissions
- Verify token is not expired

**Parsing Errors**:
- Ensure audit reports exist and are formatted correctly
- Check file paths in reports
- Verify markdown format matches expected structure

### Debug Mode

Enable verbose logging:

```bash
python3 auto_submit.py auto --verbose
```

### Dry Run Testing

Always test with dry run first:

```bash
# Test everything without making changes
python3 auto_submit.py auto --dry-run
```

## Integration

### CI/CD Integration

Add to your GitHub workflow:

```yaml
name: Auto Submit Issues
on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday

jobs:
  auto-submit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Run Auto Submit
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python3 auto_submit.py auto
```

### Scheduled Automation

Add to crontab for regular automation:

```bash
# Run weekly audit and submit bugs
0 6 * * 1 cd /path/to/repo && ./auto_submit.sh auto >> /var/log/auto_submit.log 2>&1
```

## License

This automation module is part of the PC Automation Tools project and follows the same license terms.