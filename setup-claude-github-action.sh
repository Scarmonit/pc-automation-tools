#!/bin/bash

# Claude Code GitHub Action Setup Script
echo "🤖 Setting up Claude Code GitHub Action"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Get repository info
REPO_URL=$(git config --get remote.origin.url)
REPO_NAME=$(basename -s .git "$REPO_URL")
REPO_OWNER=$(git config --get remote.origin.url | sed -n 's/.*github.com[:/]\([^/]*\)\/.*/\1/p')

echo "Repository: $REPO_OWNER/$REPO_NAME"
echo ""

# Check for GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}GitHub CLI not found. Installing...${NC}"
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update
    sudo apt install gh
fi

# Authenticate with GitHub if needed
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}Please authenticate with GitHub:${NC}"
    gh auth login
fi

# Function to set a secret
set_secret() {
    local secret_name=$1
    local secret_value=$2
    
    echo -n "Setting secret $secret_name... "
    if echo "$secret_value" | gh secret set "$secret_name" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# Check for Anthropic API key
echo ""
echo "🔑 Setting up secrets..."
echo "------------------------"

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}Please enter your Anthropic API key:${NC}"
    read -s ANTHROPIC_API_KEY
    echo ""
fi

# Set the Anthropic API key as a GitHub secret
set_secret "ANTHROPIC_API_KEY" "$ANTHROPIC_API_KEY"

# Optional: Set up AWS Bedrock credentials
echo ""
echo "Do you want to set up AWS Bedrock? (y/n)"
read -r setup_bedrock
if [ "$setup_bedrock" = "y" ]; then
    echo "Enter AWS Access Key ID:"
    read -s AWS_ACCESS_KEY_ID
    echo "Enter AWS Secret Access Key:"
    read -s AWS_SECRET_ACCESS_KEY
    echo "Enter AWS Region (default: us-east-1):"
    read AWS_REGION
    AWS_REGION=${AWS_REGION:-us-east-1}
    
    set_secret "AWS_ACCESS_KEY_ID" "$AWS_ACCESS_KEY_ID"
    set_secret "AWS_SECRET_ACCESS_KEY" "$AWS_SECRET_ACCESS_KEY"
    set_secret "AWS_REGION" "$AWS_REGION"
fi

# Create workflow directory if it doesn't exist
mkdir -p .github/workflows

# Enable GitHub Actions if not already enabled
echo ""
echo "📦 Enabling GitHub Actions..."
gh api -X PUT "repos/$REPO_OWNER/$REPO_NAME/actions/permissions" \
  -f enabled=true \
  -f allowed_actions=all 2>/dev/null

# Create claude-tasks.md file for task management
cat > .github/claude-tasks.md << 'EOF'
# Claude Tasks

This file is monitored by Claude Code Action. Add tasks here for automatic implementation.

## Pending Tasks

- [ ] Add unit tests for main functions
- [ ] Improve error handling
- [ ] Update documentation
- [ ] Optimize performance bottlenecks

## Completed Tasks

<!-- Claude will move completed tasks here -->

---
*This file is processed by Claude Code GitHub Action*
EOF

# Create a sample PR template
cat > .github/pull_request_template.md << 'EOF'
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Existing tests updated

## Claude Review Request
@claude Please review this PR for:
- Code quality
- Security issues
- Performance concerns
- Best practices

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
EOF

echo ""
echo -e "${GREEN}✅ Claude Code GitHub Action setup complete!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Commit the workflow files: git add .github/ && git commit -m '🤖 Add Claude Code workflows'"
echo "2. Push to GitHub: git push"
echo "3. Claude will automatically:"
echo "   - Review all new PRs"
echo "   - Triage and label issues"
echo "   - Respond to @claude mentions"
echo "   - Generate documentation"
echo "   - Implement tasks from .github/claude-tasks.md"
echo ""
echo "💡 Usage tips:"
echo "- Mention @claude in any issue or PR for AI assistance"
echo "- Add tasks to .github/claude-tasks.md for auto-implementation"
echo "- Trigger manual fixes with: gh workflow run claude-auto-fix -f task='Your task here'"
echo ""
echo "🔗 Documentation: https://github.com/anthropics/claude-code-action"