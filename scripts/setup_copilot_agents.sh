#!/bin/bash

echo "🤖 Setting up GitHub Copilot Agents for PC Automation Tools..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

print_status "Python 3 is available"

# Check if we're in the correct repository
if [ ! -f "llmstack/copilot_agent_integration.py" ]; then
    print_error "This script must be run from the repository root directory"
    exit 1
fi

print_status "Repository structure validated"

# Install Python dependencies if needed
print_info "Checking Python dependencies..."
if ! python3 -c "import requests" &> /dev/null; then
    print_warning "Installing required Python packages..."
    pip3 install -r requirements.txt --user
fi

print_status "Python dependencies are ready"

# Run the Copilot integration script
print_info "Configuring GitHub Copilot integration..."
python3 llmstack/copilot_agent_integration.py

if [ $? -eq 0 ]; then
    print_status "Copilot integration configured successfully"
else
    print_error "Failed to configure Copilot integration"
    exit 1
fi

# Check if VS Code is available
if command -v code &> /dev/null; then
    print_status "VS Code detected"
    
    # Check if Copilot extension is installed
    if code --list-extensions | grep -q "github.copilot"; then
        print_status "GitHub Copilot extension is installed"
    else
        print_warning "GitHub Copilot extension not found"
        echo "To install it, run: code --install-extension github.copilot"
    fi
    
    # Check if Python extension is installed
    if code --list-extensions | grep -q "ms-python.python"; then
        print_status "Python extension is installed"
    else
        print_warning "Python extension not found"
        echo "To install it, run: code --install-extension ms-python.python"
    fi
else
    print_warning "VS Code not found in PATH"
    echo "Please install VS Code and the GitHub Copilot extension"
fi

# Validate configuration files
print_info "Validating configuration files..."

files_to_check=(
    ".github/copilot.yml"
    ".github/copilot-instructions.md"
    ".vscode/settings.json"
    "docs/COPILOT_AGENTS_GUIDE.md"
    "llmstack/copilot_agent_integration.py"
)

all_files_exist=true
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        print_status "Found: $file"
    else
        print_error "Missing: $file"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = true ]; then
    print_status "All configuration files are present"
else
    print_error "Some configuration files are missing"
    exit 1
fi

# Test basic functionality
print_info "Testing integration..."

# Test Python import
if python3 -c "
import sys
sys.path.append('llmstack')
try:
    from copilot_agent_integration import CopilotAgentManager
    print('✓ Integration module imports successfully')
except Exception as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)
"; then
    print_status "Integration module test passed"
else
    print_error "Integration module test failed"
    exit 1
fi

# Create a .gitignore entry for Copilot cache if needed
if ! grep -q ".copilot" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# GitHub Copilot cache" >> .gitignore
    echo ".copilot/" >> .gitignore
    print_status "Added Copilot cache to .gitignore"
fi

# Display final instructions
echo ""
echo "🎉 GitHub Copilot Agents setup completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Restart VS Code if it's currently open"
echo "2. Open any Python file in the repository"
echo "3. Start typing AI agent code to see Copilot suggestions"
echo "4. Read the guide: docs/COPILOT_AGENTS_GUIDE.md"
echo ""
echo "🧪 Test Copilot Integration:"
echo "   Create a new Python file and type:"
echo "   'from autogen import AssistantAgent'"
echo "   'def create_coding_assistant():'"
echo ""
echo "📚 Documentation:"
echo "   - Setup Guide: docs/COPILOT_AGENTS_GUIDE.md"
echo "   - Copilot Config: .github/copilot.yml"
echo "   - VS Code Settings: .vscode/settings.json"
echo ""
echo "🔧 Troubleshooting:"
echo "   If Copilot isn't working:"
echo "   1. Ensure you have a GitHub Copilot subscription"
echo "   2. Sign in to GitHub in VS Code"
echo "   3. Enable the Copilot extension"
echo "   4. Restart VS Code"
echo ""

# Check GitHub authentication status
if command -v gh &> /dev/null; then
    if gh auth status &> /dev/null; then
        print_status "GitHub CLI is authenticated"
    else
        print_warning "GitHub CLI not authenticated"
        echo "Run 'gh auth login' to authenticate"
    fi
else
    print_info "GitHub CLI not installed (optional)"
fi

echo "✨ Ready to use GitHub Copilot with AI agents!"