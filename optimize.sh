#!/bin/bash
set -e  # Exit on any error

echo "Optimizing LLMStack deployment..."

# 1. Configure Ollama for performance
echo "Configuring Ollama for optimal performance..."
mkdir -p ~/.ollama
cat > ~/.ollama/config.json << 'EOCFG'
{
  "gpu_layers": 35,
  "num_threads": 8,
  "context_size": 4096,
  "batch_size": 512
}
EOCFG
echo "✓ Ollama configuration updated"

# 2. Set memory limits for Docker containers (check if containers exist first)
echo "Setting memory limits for Docker containers..."
if docker ps --format "{{.Names}}" | grep -q "flowise"; then
    docker update --memory="2g" --memory-swap="2g" flowise || echo "WARNING: Failed to update flowise memory limits"
else
    echo "WARNING: flowise container not found"
fi

if docker ps --format "{{.Names}}" | grep -q "openhands"; then
    docker update --memory="2g" --memory-swap="2g" openhands || echo "WARNING: Failed to update openhands memory limits"
else
    echo "WARNING: openhands container not found"
fi

# 3. Enable response caching in Redis (check if Redis is running)
echo "Configuring Redis caching..."
if docker ps --format "{{.Names}}" | grep -q "redis"; then
    docker exec llmstack-redis redis-cli CONFIG SET maxmemory 1gb || echo "WARNING: Failed to configure Redis memory"
    docker exec llmstack-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru || echo "WARNING: Failed to set Redis eviction policy"
    echo "✓ Redis caching configured"
else
    echo "WARNING: Redis container not found, skipping Redis optimization"
fi

# 4. Optimize PostgreSQL (check if PostgreSQL is running)
echo "Optimizing PostgreSQL..."
if docker ps --format "{{.Names}}" | grep -q "postgres"; then
    docker exec llmstack-postgres psql -U postgres -c "ALTER SYSTEM SET shared_buffers = '512MB';" || echo "WARNING: Failed to set shared_buffers"
    docker exec llmstack-postgres psql -U postgres -c "ALTER SYSTEM SET work_mem = '16MB';" || echo "WARNING: Failed to set work_mem"
    docker restart llmstack-postgres || echo "WARNING: Failed to restart PostgreSQL"
    echo "✓ PostgreSQL optimized"
else
    echo "WARNING: PostgreSQL container not found, skipping PostgreSQL optimization"
fi

echo "✓ Optimization complete"