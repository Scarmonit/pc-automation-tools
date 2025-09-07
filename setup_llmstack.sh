#!/bin/bash
set -e  # Exit on any error

# Set working directory
export LLMSTACK_HOME="$HOME/llmstack"
echo "Setting up LLMStack in: $LLMSTACK_HOME"

# Create directory and navigate
mkdir -p "$LLMSTACK_HOME"
cd "$LLMSTACK_HOME" || {
    echo "ERROR: Failed to navigate to $LLMSTACK_HOME"
    exit 1
}

# Clone LLMStack if not already present
if [ ! -d "LLMStack" ]; then
    echo "Cloning LLMStack repository..."
    git clone https://github.com/trypromptly/LLMStack.git
else
    echo "LLMStack directory already exists, skipping clone"
fi

cd LLMStack || {
    echo "ERROR: Failed to navigate to LLMStack directory"
    exit 1
}

# Create docker directory if it doesn't exist
mkdir -p docker

# Create production configuration
echo "Creating production configuration..."
cat > docker/.env.production << 'EOF'
# Security
SECRET_KEY=$(openssl rand -base64 32)
CIPHER_SALT=$(openssl rand -base64 16)
DATABASE_PASSWORD=$(openssl rand -base64 24)

# Paths
POSTGRES_VOLUME=./data/postgres
REDIS_VOLUME=./data/redis
WEAVIATE_VOLUME=./data/weaviate

# Model endpoints (all local)
OPENAI_API_BASE=http://host.docker.internal:11434/v1
OPENAI_API_KEY=ollama

# Features
ENABLE_SIGNUP=false
ENABLE_ANALYTICS=false
DEFAULT_VECTOR_DB=chroma
EOF

# Generate secure keys
sed -i "s/\$(openssl.*)/$(openssl rand -base64 32)/" docker/.env.production

# Build client assets
cd "$LLMSTACK_HOME/LLMStack/client"
npm install
npm run build
cd ..

# Start LLMStack with Docker
docker compose -f docker/docker-compose.yml --env-file docker/.env.production up -d

# Wait for services
echo "Waiting for services to start..."
sleep 30

# Verify deployment
curl -s http://localhost:3000/api/health | grep -q "ok" && echo "✓ LLMStack running" || exit 1