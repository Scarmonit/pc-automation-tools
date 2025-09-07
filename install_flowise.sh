#!/bin/bash
set -e  # Exit on any error

echo "Deploying Flowise with Docker..."

# Check if Docker is available
if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: Docker is required but not installed"
    exit 1
fi

# Create Flowise data directory
mkdir -p ~/.flowise

# Deploy Flowise with Docker
echo "Starting Flowise container..."
docker run -d \
  --name flowise \
  -p 3001:3000 \
  -v ~/.flowise:/root/.flowise \
  --restart unless-stopped \
  flowiseai/flowise || {
    echo "ERROR: Failed to start Flowise container"
    exit 1
}

# Wait for Flowise
echo "Waiting for Flowise to start..."
sleep 10

# Verify Flowise
if curl -s http://localhost:3001 >/dev/null 2>&1; then
    echo "✓ Flowise running and accessible at http://localhost:3001"
else
    echo "⚠ Flowise container started but not accessible yet"
    echo "Check logs with: docker logs flowise"
fi