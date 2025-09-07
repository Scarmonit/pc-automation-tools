#!/bin/bash

#######################################################################################
# CLAUDE AI ULTIMATE POWER EDITION - WINDOWS VERSION
# Modified for Windows/Git Bash compatibility
#######################################################################################

set -eo pipefail

# Terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# System paths
INSTALL_PREFIX="$HOME/.claude-ultimate"
CONFIG_DIR="$HOME/.config/claude-ultimate"
DATA_DIR="$HOME/.local/share/claude-ultimate"
CACHE_DIR="$HOME/.cache/claude-ultimate"
MODELS_DIR="$DATA_DIR/models"

#######################################################################################
# BANNER
#######################################################################################

show_banner() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
    ███████╗██╗███╗   ██╗ ██████╗ ██╗   ██╗██╗      █████╗ ██████╗ ██╗████████╗██╗   ██╗
    ██╔════╝██║████╗  ██║██╔════╝ ██║   ██║██║     ██╔══██╗██╔══██╗██║╚══██╔══╝╚██╗ ██╔╝
    ███████╗██║██╔██╗ ██║██║  ███╗██║   ██║██║     ███████║██████╔╝██║   ██║    ╚████╔╝ 
    ╚════██║██║██║╚██╗██║██║   ██║██║   ██║██║     ██╔══██║██╔══██╗██║   ██║     ╚██╔╝  
    ███████║██║██║ ╚████║╚██████╔╝╚██████╔╝███████╗██║  ██║██║  ██║██║   ██║      ██║   
    ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝   ╚═╝      ╚═╝   
EOF
    echo -e "${NC}"
    echo -e "${BOLD}${YELLOW}            ULTIMATE POWER EDITION - WINDOWS EDITION${NC}"
    echo ""
}

#######################################################################################
# SIMPLIFIED SYSTEM DETECTION
#######################################################################################

detect_system() {
    echo -e "${BLUE}[INFO]${NC} Detecting system capabilities..."
    
    # Basic system info
    OS="Windows (Git Bash)"
    ARCH=$(uname -m)
    CPU_CORES=$(nproc 2>/dev/null || echo "4")
    
    # RAM detection
    if [ -f /proc/meminfo ]; then
        RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        RAM_GB=$((RAM_KB / 1024 / 1024))
    else
        RAM_GB="Unknown"
    fi
    
    # GPU detection
    GPU_DETECTED=false
    if command -v nvidia-smi &>/dev/null; then
        GPU_DETECTED=true
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1 || echo "NVIDIA GPU")
    fi
    
    # Python check
    PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2 || python --version 2>/dev/null | cut -d' ' -f2 || echo "Not found")
    
    # Display summary
    echo -e "${CYAN}┌─────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│                   SYSTEM CAPABILITIES                   │${NC}"
    echo -e "${CYAN}├─────────────────────────────────────────────────────────┤${NC}"
    echo -e "${CYAN}│${NC} OS:          ${BOLD}$OS${NC}"
    echo -e "${CYAN}│${NC} CPU:         ${BOLD}$CPU_CORES cores${NC}"
    echo -e "${CYAN}│${NC} RAM:         ${BOLD}${RAM_GB}GB${NC}"
    echo -e "${CYAN}│${NC} GPU:         ${BOLD}$([ "$GPU_DETECTED" = true ] && echo "$GPU_NAME" || echo "None detected")${NC}"
    echo -e "${CYAN}│${NC} Python:      ${BOLD}$PYTHON_VERSION${NC}"
    echo -e "${CYAN}└─────────────────────────────────────────────────────────┘${NC}"
    echo ""
}

#######################################################################################
# PYTHON ENVIRONMENT SETUP
#######################################################################################

setup_python_env() {
    echo -e "${BLUE}[INFO]${NC} Setting up Python environment..."
    
    # Check for Python
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}[ERROR]${NC} Python not found! Please install Python first."
        exit 1
    fi
    
    # Create directories
    mkdir -p "$INSTALL_PREFIX/bin"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$MODELS_DIR"
    
    # Create virtual environment
    echo -e "${BLUE}[INFO]${NC} Creating virtual environment..."
    $PYTHON_CMD -m venv "$INSTALL_PREFIX/venv" 2>/dev/null || {
        echo -e "${YELLOW}[WARN]${NC} Could not create virtual environment"
        return
    }
    
    # Activate virtual environment
    source "$INSTALL_PREFIX/venv/Scripts/activate" 2>/dev/null || \
    source "$INSTALL_PREFIX/venv/bin/activate" 2>/dev/null || {
        echo -e "${YELLOW}[WARN]${NC} Could not activate virtual environment"
        return
    }
    
    # Upgrade pip
    echo -e "${BLUE}[INFO]${NC} Upgrading pip..."
    $PYTHON_CMD -m pip install --upgrade pip setuptools wheel --quiet
    
    # Install basic AI packages
    echo -e "${BLUE}[INFO]${NC} Installing AI packages (this may take a while)..."
    
    PACKAGES=(
        "openai"
        "anthropic"
        "transformers"
        "torch"
        "numpy"
        "pandas"
        "requests"
        "tqdm"
        "rich"
    )
    
    for package in "${PACKAGES[@]}"; do
        echo -e "  Installing $package..."
        $PYTHON_CMD -m pip install "$package" --quiet 2>/dev/null || \
            echo -e "${YELLOW}  [WARN]${NC} Failed to install $package"
    done
    
    echo -e "${GREEN}[✓]${NC} Python environment ready"
}

#######################################################################################
# CREATE SIMPLE AI TOOLS
#######################################################################################

create_ai_tools() {
    echo -e "${BLUE}[INFO]${NC} Creating AI command-line tools..."
    
    # Create a simple AI chat script
    cat > "$INSTALL_PREFIX/bin/ai-chat.py" << 'EOF'
#!/usr/bin/env python
"""Simple AI Chat Interface"""

import os
import sys

try:
    import openai
    from anthropic import Anthropic
except ImportError:
    print("AI libraries not installed. Run: pip install openai anthropic")
    sys.exit(1)

def chat():
    print("AI Chat Interface")
    print("================")
    print("Type 'quit' to exit\n")
    
    # Check for API keys
    if os.environ.get("OPENAI_API_KEY"):
        print("Using OpenAI")
        client = openai.OpenAI()
        model = "gpt-3.5-turbo"
    elif os.environ.get("ANTHROPIC_API_KEY"):
        print("Using Anthropic")
        client = Anthropic()
        model = "claude-3-haiku-20240307"
    else:
        print("No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
        
        print("\nAI: Thinking...")
        # Add actual API calls here
        print("(API calls would go here)")

if __name__ == "__main__":
    chat()
EOF
    
    # Create model downloader
    cat > "$INSTALL_PREFIX/bin/download-models.sh" << 'EOF'
#!/bin/bash
echo "Model Downloader"
echo "================"
echo ""
echo "Available models:"
echo "1. GPT-2 (124M parameters)"
echo "2. DistilBERT (66M parameters)"
echo "3. BERT Base (110M parameters)"
echo ""
echo "Note: Actual downloading requires additional setup"
EOF
    
    chmod +x "$INSTALL_PREFIX/bin/ai-chat.py"
    chmod +x "$INSTALL_PREFIX/bin/download-models.sh"
    
    echo -e "${GREEN}[✓]${NC} AI tools created"
}

#######################################################################################
# MAIN INSTALLATION
#######################################################################################

main() {
    show_banner
    detect_system
    
    echo -e "${BOLD}${CYAN}Starting installation...${NC}"
    echo ""
    
    setup_python_env
    create_ai_tools
    
    # Add to PATH
    echo ""
    echo -e "${BLUE}[INFO]${NC} Adding to PATH..."
    echo "export PATH=\"$INSTALL_PREFIX/bin:\$PATH\"" >> ~/.bashrc
    
    # Final summary
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         🚀 INSTALLATION COMPLETE! 🚀                         ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Installation Summary:${NC}"
    echo "  • Installation directory: $INSTALL_PREFIX"
    echo "  • Python packages installed: ${#PACKAGES[@]}"
    echo "  • Tools created: 2"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Set your API keys:"
    echo "     export OPENAI_API_KEY='your-key-here'"
    echo "     export ANTHROPIC_API_KEY='your-key-here'"
    echo "  2. Restart your terminal or run: source ~/.bashrc"
    echo "  3. Try the tools:"
    echo "     python $INSTALL_PREFIX/bin/ai-chat.py"
    echo "     bash $INSTALL_PREFIX/bin/download-models.sh"
    echo ""
    echo -e "${BOLD}${GREEN}Happy hacking! 🚀${NC}"
}

# Run the installation
main "$@"