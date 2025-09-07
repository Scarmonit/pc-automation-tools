#!/bin/bash
# Install Aider
pip install --user aider-chat

# Configure for Ollama
cat > ~/.aider.conf.yml << 'EOF'
model: ollama/codellama:7b
openai-api-base: http://localhost:11434/v1
openai-api-key: ollama
auto-commits: false
stream: true
EOF

# Test Aider
aider --help && echo "✓ Aider installed" || echo "✗ Aider failed"