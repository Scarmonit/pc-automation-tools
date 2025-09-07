#!/bin/bash
# LLMStack Open Source Deployment Script
# Purpose: Deploy LLMStack with 100% free and open source components
# Target: Zero API costs, full data privacy, production-ready system

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
export LLMSTACK_HOME="${LLMSTACK_HOME:-$HOME/llmstack}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if command -v $1 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Main deployment function
main() {
    log_info "Starting LLMStack Open Source Deployment"
    
    # Parse command line arguments
    case "${1:-}" in
        check)
            bash "$SCRIPT_DIR/scripts/check_system.sh"
            ;;
        install-models)
            bash "$SCRIPT_DIR/scripts/install_models.sh"
            ;;
        deploy)
            bash "$SCRIPT_DIR/scripts/deploy_llmstack.sh"
            ;;
        install-agents)
            bash "$SCRIPT_DIR/scripts/install_agents.sh"
            ;;
        configure)
            bash "$SCRIPT_DIR/scripts/configure_integrations.sh"
            ;;
        monitor)
            bash "$SCRIPT_DIR/scripts/setup_monitoring.sh"
            ;;
        optimize)
            bash "$SCRIPT_DIR/scripts/optimize_performance.sh"
            ;;
        validate)
            bash "$SCRIPT_DIR/scripts/validate_deployment.sh"
            ;;
        benchmark)
            python3 "$SCRIPT_DIR/scripts/benchmark.py"
            ;;
        all)
            log_info "Running complete deployment..."
            bash "$SCRIPT_DIR/scripts/check_system.sh"
            bash "$SCRIPT_DIR/scripts/install_models.sh"
            bash "$SCRIPT_DIR/scripts/deploy_llmstack.sh"
            bash "$SCRIPT_DIR/scripts/install_agents.sh"
            bash "$SCRIPT_DIR/scripts/configure_integrations.sh"
            bash "$SCRIPT_DIR/scripts/setup_monitoring.sh"
            bash "$SCRIPT_DIR/scripts/optimize_performance.sh"
            bash "$SCRIPT_DIR/scripts/validate_deployment.sh"
            log_info "Deployment complete!"
            ;;
        start)
            log_info "Starting all services..."
            cd "$LLMSTACK_HOME"
            docker compose up -d
            ollama serve &
            if [ -f "$HOME/lm-studio.AppImage" ]; then
                "$HOME/lm-studio.AppImage" server start --port 1234 &
            fi
            log_info "Services started"
            ;;
        stop)
            log_info "Stopping all services..."
            cd "$LLMSTACK_HOME"
            docker compose down
            killall ollama 2>/dev/null || true
            killall lm-studio.AppImage 2>/dev/null || true
            log_info "Services stopped"
            ;;
        status)
            bash "$SCRIPT_DIR/scripts/validate_deployment.sh"
            ;;
        help|*)
            echo "LLMStack Open Source Deployment Tool"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  check          - Check system requirements"
            echo "  install-models - Install local AI models (Ollama, LM Studio, etc.)"
            echo "  deploy         - Deploy LLMStack base system"
            echo "  install-agents - Install free AI agents (AutoGen, Flowise, etc.)"
            echo "  configure      - Configure integrations"
            echo "  monitor        - Set up monitoring stack"
            echo "  optimize       - Optimize performance"
            echo "  validate       - Validate deployment"
            echo "  benchmark      - Run performance benchmark"
            echo "  all            - Run complete deployment"
            echo "  start          - Start all services"
            echo "  stop           - Stop all services"
            echo "  status         - Check service status"
            echo "  help           - Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  LLMSTACK_HOME  - Installation directory (default: ~/llmstack)"
            echo ""
            echo "Examples:"
            echo "  $0 check                    # Check if system meets requirements"
            echo "  $0 all                      # Complete installation"
            echo "  $0 start                    # Start services after installation"
            echo "  LLMSTACK_HOME=/opt/llm $0 deploy  # Custom installation path"
            ;;
    esac
}

# Run main function
main "$@"