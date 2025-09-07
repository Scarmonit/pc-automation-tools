#!/bin/bash
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