#!/bin/bash
set -e  # Exit on any error

# Install Ollama (primary local model server)
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
echo "Verifying Ollama installation..."
ollama --version || {
    echo "ERROR: Ollama installation failed"
    exit 1
}

# Start Ollama service (check if systemd is available)
if command -v systemctl >/dev/null 2>&1; then
    echo "Starting Ollama service..."
    sudo systemctl enable ollama
    sudo systemctl start ollama
else
    echo "WARNING: systemctl not available, starting Ollama manually..."
    ollama serve &
    sleep 5
fi

# Download essential models
echo "Downloading essential models..."
ollama pull llama3.2:3b        # 2GB - Fast general purpose
ollama pull mistral:7b-instruct # 4GB - Excellent reasoning  
ollama pull codellama:7b        # 4GB - Code generation

echo "✓ Ollama installation completed successfully"
ollama pull qwen2.5:3b          # 2GB - Multilingual support

# Verify models
ollama list | grep -E "llama3.2|mistral|codellama|qwen" || exit 1