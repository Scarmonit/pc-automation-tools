#!/bin/bash
set -e  # Exit on any error

echo "Deploying OpenHands..."

# Check if Docker is available
if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: Docker is required but not installed"
    exit 1
fi

# Create workspace directory
mkdir -p ~/.openhands

# Deploy OpenHands
echo "Starting OpenHands container..."
docker run -d \
  --name openhands \
  -p 3002:3000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands:/app/workspace \
  --restart unless-stopped \
  ghcr.io/all-hands-ai/openhands:latest || {
    echo "ERROR: Failed to start OpenHands container"
    exit 1
}

# Verify OpenHands
echo "Verifying OpenHands deployment..."
sleep 10

if curl -s http://localhost:3002/health >/dev/null 2>&1; then
    echo "✓ OpenHands running and accessible"
else
    echo "⚠ OpenHands container started but health check failed"
    echo "Check logs with: docker logs openhands"
fi