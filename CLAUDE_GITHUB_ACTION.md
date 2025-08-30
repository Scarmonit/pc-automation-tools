# 🤖 Claude Code GitHub Action Setup Guide

## Overview
The Claude Code GitHub Action brings AI-powered automation to your GitHub workflow, providing automatic code reviews, issue triage, documentation generation, and code implementation.

## Features

### 🔍 Automatic PR Reviews
- Code quality assessment
- Security vulnerability detection
- Performance analysis
- Best practices validation
- Constructive feedback

### 🏷️ Issue Triage & Management
- Automatic labeling
- Complexity estimation
- Duplicate detection
- Solution suggestions
- Interactive Q&A with @claude mentions

### 📚 Documentation Generation
- API documentation updates
- README synchronization
- Code examples creation
- Changelog maintenance
- Function documentation

### 🔧 Auto-Implementation
- Task-based code generation
- Test creation
- Bug fixes
- Feature implementation
- Refactoring

## Quick Setup

### 1. Install via Claude Code (Recommended)
```bash
# In Claude Code terminal
/install-github-app
```

### 2. Manual Setup
```bash
# Run the setup script
chmod +x setup-claude-github-action.sh
./setup-claude-github-action.sh
```

### 3. Set GitHub Secrets
Add these secrets to your repository:
- `ANTHROPIC_API_KEY` - Your Anthropic API key (required)
- `AWS_ACCESS_KEY_ID` - For AWS Bedrock (optional)
- `AWS_SECRET_ACCESS_KEY` - For AWS Bedrock (optional)
- `GOOGLE_VERTEX_PROJECT` - For Google Vertex AI (optional)

## Workflow Files Created

### 1. `.github/workflows/claude-pr-review.yml`
Automatically reviews all PRs with:
- Code quality analysis
- Security scanning
- Performance checks
- Best practices validation

### 2. `.github/workflows/claude-issue-triage.yml`
Manages issues with:
- Auto-labeling
- Complexity assessment
- Solution suggestions
- Interactive responses

### 3. `.github/workflows/claude-auto-fix.yml`
Implements code changes:
- Task-based implementation
- Automatic PR creation
- Test generation
- Documentation updates

### 4. `.github/workflows/claude-docs-sync.yml`
Maintains documentation:
- README updates
- API docs generation
- Code examples
- Changelog updates

## Usage Examples

### PR Reviews
Claude automatically reviews all PRs. For specific feedback:
```markdown
@claude Please focus on security implications of these changes
```

### Issue Assistance
In any issue, mention Claude for help:
```markdown
@claude How should we implement this feature?
```

### Manual Task Execution
Trigger specific tasks:
```bash
gh workflow run claude-auto-fix -f task="Add unit tests for UserService"
```

### Task File Management
Add tasks to `.github/claude-tasks.md`:
```markdown
- [ ] Implement user authentication
- [ ] Add input validation
- [ ] Optimize database queries
```

## Advanced Configuration

### Custom Review Prompts
Edit workflow files to customize Claude's behavior:
```yaml
prompt: |
  Focus on:
  - React best practices
  - TypeScript strict mode compliance
  - Accessibility standards
```

### Temperature Settings
Adjust Claude's creativity/precision:
```yaml
claude_args: |
  --temperature 0.1  # More deterministic (good for code)
  --temperature 0.7  # More creative (good for suggestions)
```

### Model Selection
Use different Claude models:
```yaml
claude_args: |
  --model claude-3-opus-20240229
  --model claude-3-sonnet-20240229
```

## Best Practices

### 1. Security
- Never commit API keys directly
- Use GitHub Secrets for credentials
- Review Claude's suggestions before merging

### 2. Cost Management
- Set up spending limits in Anthropic Console
- Use appropriate models for tasks
- Configure workflows to run only when needed

### 3. Collaboration
- Establish team guidelines for @claude mentions
- Review AI-generated PRs thoroughly
- Use Claude as an assistant, not a replacement

## Troubleshooting

### Common Issues

#### Workflow Not Triggering
- Check GitHub Actions is enabled
- Verify secrets are set correctly
- Ensure proper permissions in workflow

#### API Rate Limits
- Implement caching where possible
- Batch similar requests
- Use webhook events efficiently

#### Authentication Errors
- Verify API key is valid
- Check secret names match workflow
- Ensure proper IAM permissions (for AWS/GCP)

## Commands Reference

### GitHub CLI Commands
```bash
# List workflows
gh workflow list

# View workflow runs
gh run list

# Trigger manual workflow
gh workflow run claude-auto-fix

# View secrets
gh secret list

# Set a secret
echo "your-api-key" | gh secret set ANTHROPIC_API_KEY
```

### Workflow Dispatch
```bash
# Run with custom parameters
gh workflow run claude-auto-fix \
  -f task="Refactor authentication module" \
  -f branch="claude-refactor"
```

## Integration with Other Tools

### Works with:
- GitHub Projects
- GitHub Discussions
- GitHub Wiki
- External CI/CD systems
- Slack/Discord webhooks

## Updates & Maintenance

### Keep Action Updated
```yaml
uses: anthropics/claude-code-action@v1  # Uses latest v1.x
uses: anthropics/claude-code-action@main # Uses latest main branch
```

### Monitor Usage
- Check GitHub Actions usage in Settings
- Review Anthropic API usage dashboard
- Set up cost alerts

## Support & Resources

- **Documentation**: [GitHub Action Docs](https://github.com/anthropics/claude-code-action)
- **Issues**: [Report Issues](https://github.com/anthropics/claude-code-action/issues)
- **Community**: [Discord Server](https://discord.gg/anthropic)
- **API Reference**: [Anthropic API Docs](https://docs.anthropic.com)

## License
This setup is provided as-is. Check the original repository for license details.

---

*Generated with Claude Code - Your AI Programming Assistant*