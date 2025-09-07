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

# Generate secure keys (fix the sed command)
echo "Generating secure keys..."
SECRET_KEY=$(openssl rand -base64 32)
CIPHER_SALT=$(openssl rand -base64 16)
DATABASE_PASSWORD=$(openssl rand -base64 24)

# Update the configuration with actual values
sed -i "s/SECRET_KEY=\$(openssl rand -base64 32)/SECRET_KEY=$SECRET_KEY/" docker/.env.production
sed -i "s/CIPHER_SALT=\$(openssl rand -base64 16)/CIPHER_SALT=$CIPHER_SALT/" docker/.env.production
sed -i "s/DATABASE_PASSWORD=\$(openssl rand -base64 24)/DATABASE_PASSWORD=$DATABASE_PASSWORD/" docker/.env.production

# Build client assets (check if client directory exists)
if [ -d "client" ]; then
    echo "Building client assets..."
    cd client || {
        echo "ERROR: Failed to navigate to client directory"
        exit 1
    }
    
    if command -v npm >/dev/null 2>&1; then
        npm install || {
            echo "ERROR: npm install failed"
            exit 1
        }
        npm run build || {
            echo "ERROR: npm build failed"
            exit 1
        }
    else
        echo "ERROR: npm not found, please install Node.js"
        exit 1
    fi
    
    cd .. || {
        echo "ERROR: Failed to navigate back to LLMStack directory"
        exit 1
    }
else
    echo "WARNING: client directory not found, skipping client build"
fi

# Check if docker-compose file exists
if [ ! -f "docker/docker-compose.yml" ]; then
    echo "ERROR: docker/docker-compose.yml not found"
    exit 1
fi

# Start LLMStack with Docker
echo "Starting LLMStack with Docker..."
docker compose -f docker/docker-compose.yml --env-file docker/.env.production up -d || {
    echo "ERROR: Failed to start Docker services"
    exit 1
}

# Wait for services
echo "Waiting for services to start..."
sleep 30

# Verify deployment
echo "Verifying deployment..."
if curl -s http://localhost:3000/api/health | grep -q "ok"; then
    echo "✓ LLMStack running and accessible"
else
    echo "⚠ LLMStack started but health check failed"
    echo "Check logs with: docker logs llmstack-api"
    exit 1
fi