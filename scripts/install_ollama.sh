#!/bin/bash
set -e
# Install Ollama (primary local model server)
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version || exit 1

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Download essential models
ollama pull llama3.2:3b        # 2GB - Fast general purpose
ollama pull mistral:7b-instruct # 4GB - Excellent reasoning
ollama pull codellama:7b        # 4GB - Code generation
ollama pull qwen2.5:3b          # 2GB - Multilingual support

# Verify models
ollama list | grep -E "llama3.2|mistral|codellama|qwen" || exit 1