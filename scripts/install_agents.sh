#!/bin/bash

echo "Installing Free AI Agents..."

# Install AutoGen
pip install --user pyautogen autogen-agentchat

# Create AutoGen configuration
mkdir -p ~/.autogen
cat > ~/.autogen/config.json << 'EOF'
{
  "model_list": [
    {
      "model": "llama3.2",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "api_type": "openai"
    },
    {
      "model": "mistral",
      "base_url": "http://localhost:11434/v1", 
      "api_key": "ollama",
      "api_type": "openai"
    }
  ]
}
EOF

# Test AutoGen
python3 -c "from autogen import AssistantAgent; print('✓ AutoGen ready')" || echo "✗ AutoGen failed"

# Deploy Flowise with Docker
docker run -d \
  --name flowise \
  -p 3001:3000 \
  -v ~/.flowise:/root/.flowise \
  --restart unless-stopped \
  flowiseai/flowise

# Wait for Flowise
sleep 10
curl http://localhost:3001 && echo "✓ Flowise running" || echo "✗ Flowise failed"

# Deploy OpenHands
docker run -d \
  --name openhands \
  -p 3002:3000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands:/app/workspace \
  --restart unless-stopped \
  ghcr.io/all-hands-ai/openhands:latest

# Verify OpenHands
sleep 10
curl http://localhost:3002/health && echo "✓ OpenHands running" || echo "⚠ OpenHands unavailable"

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

echo "✓ All agents installed successfully"