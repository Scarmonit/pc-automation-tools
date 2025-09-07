#!/bin/bash
# Install Continue for VS Code (if code command available)
if command -v code &> /dev/null; then
    code --install-extension continue.continue
    
    # Configure Continue for local models
    mkdir -p ~/.continue
    cat > ~/.continue/config.json << 'EOF'
{
  "models": [
    {
      "title": "Ollama - Llama 3.2",
      "provider": "ollama",
      "model": "llama3.2:3b",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Ollama - CodeLlama",
      "provider": "ollama",
      "model": "codellama:7b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Starcoder",
    "provider": "ollama",
    "model": "starcoder2:3b",
    "apiBase": "http://localhost:11434"
  }
}
EOF
    echo "✓ Continue configured"
else
    echo "⚠ VS Code not found - skip Continue"
fi