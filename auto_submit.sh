#!/bin/bash
# Auto Submit Helper Script
# Quick access to auto-submit functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if GitHub token is set
check_github_token() {
    if [[ -z "${GITHUB_TOKEN}" ]]; then
        if [[ -f ".env" ]] && grep -q "GITHUB_TOKEN" .env; then
            print_info "Loading GitHub token from .env file"
            export $(grep -v '^#' .env | xargs)
        else
            print_error "GitHub token not found!"
            print_info "Set GITHUB_TOKEN environment variable or add to .env file"
            print_info "Get a token at: https://github.com/settings/tokens"
            exit 1
        fi
    fi
}

# Function to run audit and generate reports
run_audits() {
    print_info "Running security and code quality audits..."
    
    if [[ -f "security_audit.py" ]]; then
        print_info "Running security audit..."
        python3 security_audit.py
    fi
    
    if [[ -f "code_quality_audit.py" ]]; then
        print_info "Running code quality audit..."
        python3 code_quality_audit.py
    fi
    
    print_success "Audits completed!"
}

# Function to show help
show_help() {
    echo "Auto Submit Helper Script"
    echo "========================"
    echo
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  audit          Run security and code quality audits"
    echo "  bugs           Submit bug reports from audit results"
    echo "  merges         Create merge requests for automated fixes"
    echo "  auto           Run full automation (audits + bugs + merges)"
    echo "  dry-run        Preview what would be done without executing"
    echo "  help           Show this help message"
    echo
    echo "Options:"
    echo "  --type TYPE    Specify type: code, security, shell, python, all"
    echo "  --verbose      Enable verbose logging"
    echo
    echo "Examples:"
    echo "  $0 audit                    # Run audits"
    echo "  $0 bugs --type security     # Submit security bugs only"
    echo "  $0 merges --type shell      # Create shell script fixes"
    echo "  $0 auto                     # Full automation"
    echo "  $0 dry-run                  # Preview all actions"
    echo
    echo "Environment:"
    echo "  GITHUB_TOKEN=your_token     # Required for GitHub operations"
}

# Main script logic
case "${1:-help}" in
    "audit")
        print_info "🔍 Running audits..."
        run_audits
        ;;
    
    "bugs")
        print_info "🐛 Submitting bug reports..."
        check_github_token
        shift
        python3 auto_submit.py bugs "$@"
        ;;
    
    "merges")
        print_info "🔀 Creating merge requests..."
        check_github_token
        shift
        python3 auto_submit.py merges "$@"
        ;;
    
    "auto")
        print_info "🚀 Running full automation..."
        check_github_token
        run_audits
        shift
        python3 auto_submit.py auto "$@"
        ;;
    
    "dry-run")
        print_info "🔍 Running dry-run preview..."
        check_github_token
        run_audits
        print_info "Preview - Bug submission:"
        python3 auto_submit.py bugs --dry-run --type all
        print_info "Preview - Merge creation:"
        python3 auto_submit.py merges --dry-run --type all
        ;;
    
    "help"|"--help"|"-h")
        show_help
        ;;
    
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac