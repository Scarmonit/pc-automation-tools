#!/bin/bash

echo "Optimizing LLMStack deployment..."

# 1. Configure Ollama for performance
cat > ~/.ollama/config.json << 'EOCFG'
{
  "gpu_layers": 35,
  "num_threads": 8,
  "context_size": 4096,
  "batch_size": 512
}
EOCFG

# 2. Set memory limits for Docker containers
docker update --memory="2g" --memory-swap="2g" flowise
docker update --memory="2g" --memory-swap="2g" openhands

# 3. Enable response caching in Redis
docker exec -it llmstack-redis redis-cli CONFIG SET maxmemory 1gb
docker exec -it llmstack-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru

# 4. Optimize PostgreSQL
docker exec -it llmstack-postgres psql -U postgres -c "ALTER SYSTEM SET shared_buffers = '512MB';"
docker exec -it llmstack-postgres psql -U postgres -c "ALTER SYSTEM SET work_mem = '16MB';"
docker restart llmstack-postgres

echo "✓ Optimization complete"