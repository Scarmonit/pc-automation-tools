#!/bin/bash
# Install Local AI Models Script

set -e

echo "=== Installing Local AI Models ==="
echo ""

# Helper functions
log_info() { echo "[INFO] $1"; }
log_error() { echo "[ERROR] $1"; }
log_success() { echo "✓ $1"; }

# Install Ollama
install_ollama() {
    log_info "Installing Ollama..."
    
    # Check if already installed
    if command -v ollama &> /dev/null; then
        log_success "Ollama already installed"
    else
        # Install based on OS
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -fsSL https://ollama.com/install.sh | sh
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install ollama
        else
            log_error "Unsupported OS for automatic Ollama installation"
            echo "Please install Ollama manually from https://ollama.com"
            return 1
        fi
    fi
    
    # Start Ollama service
    log_info "Starting Ollama service..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl enable ollama 2>/dev/null || true
        sudo systemctl start ollama 2>/dev/null || ollama serve &
    else
        ollama serve &
    fi
    
    sleep 5
    
    # Download essential models
    log_info "Downloading essential models..."
    
    models=(
        "llama3.2:3b"         # 2GB - Fast general purpose
        "mistral:7b-instruct" # 4GB - Excellent reasoning
        "codellama:7b"        # 4GB - Code generation
        "qwen2.5:3b"          # 2GB - Multilingual support
        "starcoder2:3b"       # 2GB - Code completion
    )
    
    for model in "${models[@]}"; do
        log_info "Pulling $model..."
        ollama pull "$model" || log_error "Failed to pull $model"
    done
    
    # Verify models
    log_info "Verifying installed models..."
    ollama list
    log_success "Ollama models installed"
}

# Install LM Studio
install_lm_studio() {
    log_info "Setting up LM Studio..."
    
    LM_STUDIO_PATH="$HOME/lm-studio"
    mkdir -p "$LM_STUDIO_PATH"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ ! -f "$LM_STUDIO_PATH/lm-studio.AppImage" ]; then
            log_info "Downloading LM Studio for Linux..."
            wget -O "$LM_STUDIO_PATH/lm-studio.AppImage" \
                "https://releases.lmstudio.ai/linux/x86/stable/LM-Studio-linux-x86.AppImage"
            chmod +x "$LM_STUDIO_PATH/lm-studio.AppImage"
        fi
        
        # Create desktop entry
        cat > ~/.local/share/applications/lm-studio.desktop << EOF
[Desktop Entry]
Type=Application
Name=LM Studio
Exec=$LM_STUDIO_PATH/lm-studio.AppImage
Icon=lm-studio
Terminal=false
EOF
        
        # Start server in background
        log_info "Starting LM Studio server..."
        "$LM_STUDIO_PATH/lm-studio.AppImage" server start --port 1234 --cors &
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v lms &> /dev/null; then
            log_info "Please download LM Studio from https://lmstudio.ai"
            log_info "After installation, start the server on port 1234"
        fi
    fi
    
    sleep 5
    
    # Verify server
    if curl -s http://localhost:1234/v1/models &> /dev/null; then
        log_success "LM Studio server running"
    else
        log_error "LM Studio server not accessible"
    fi
}

# Setup vLLM with Docker (GPU only)
setup_vllm() {
    log_info "Setting up vLLM..."
    
    # Check for GPU
    if ! command -v nvidia-smi &> /dev/null; then
        log_info "No NVIDIA GPU detected, skipping vLLM setup"
        return 0
    fi
    
    mkdir -p ~/llmstack/vllm
    
    cat > ~/llmstack/vllm/docker-compose.yml << 'EOF'
version: '3.8'
services:
  vllm:
    image: vllm/vllm-openai:latest
    container_name: vllm-server
    ports:
      - "8000:8000"
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
    environment:
      - HF_HOME=/root/.cache/huggingface
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    command: >
      --model microsoft/Phi-3-mini-4k-instruct
      --gpu-memory-utilization 0.8
      --max-model-len 4096
      --port 8000
    restart: unless-stopped
EOF
    
    log_info "Starting vLLM container..."
    cd ~/llmstack/vllm
    docker compose up -d
    
    sleep 15
    
    # Verify vLLM
    if curl -s http://localhost:8000/v1/models &> /dev/null; then
        log_success "vLLM server running"
    else
        log_error "vLLM server not accessible"
    fi
}

# Install Jan (optional desktop app)
install_jan() {
    log_info "Setting up Jan AI..."
    
    JAN_PATH="$HOME/jan-ai"
    mkdir -p "$JAN_PATH"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ ! -f "$JAN_PATH/jan.AppImage" ]; then
            log_info "Downloading Jan for Linux..."
            wget -O "$JAN_PATH/jan.AppImage" \
                "https://github.com/janhq/jan/releases/latest/download/jan-linux-x86_64.AppImage"
            chmod +x "$JAN_PATH/jan.AppImage"
        fi
        
        # Start Jan API server
        log_info "Starting Jan API server..."
        "$JAN_PATH/jan.AppImage" --serve --port 1337 &
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "Please download Jan from https://jan.ai"
        log_info "After installation, enable the API server on port 1337"
    fi
    
    sleep 5
    
    # Verify Jan
    if curl -s http://localhost:1337/v1/models &> /dev/null; then
        log_success "Jan API server running"
    else
        log_info "Jan API server not accessible (optional component)"
    fi
}

# Main installation
main() {
    log_info "Starting model installation..."
    
    # Install Ollama (primary)
    install_ollama
    
    # Install LM Studio (secondary)
    install_lm_studio
    
    # Setup vLLM (GPU only)
    setup_vllm
    
    # Install Jan (optional)
    install_jan
    
    echo ""
    log_success "Model installation complete!"
    echo ""
    echo "Available endpoints:"
    echo "  Ollama: http://localhost:11434/v1"
    echo "  LM Studio: http://localhost:1234/v1"
    if command -v nvidia-smi &> /dev/null; then
        echo "  vLLM: http://localhost:8000/v1"
    fi
    echo "  Jan: http://localhost:1337/v1"
}

main "$@"