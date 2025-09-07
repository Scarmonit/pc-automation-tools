#!/bin/bash
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