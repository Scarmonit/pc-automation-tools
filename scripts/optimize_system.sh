#!/bin/bash
# System optimization script

echo "Optimizing LLMStack deployment..."

# 1. Configure Ollama for performance
mkdir -p ~/.ollama
cat > ~/.ollama/config.json << 'EOF'
{
  "gpu_layers": 35,
  "num_threads": 8,
  "context_size": 4096,
  "batch_size": 512
}
EOF

# 2. Set memory limits for Docker containers
echo "Setting Docker container memory limits..."
docker update --memory="2g" --memory-swap="2g" flowise 2>/dev/null || echo "Flowise container not found"
docker update --memory="2g" --memory-swap="2g" openhands 2>/dev/null || echo "OpenHands container not found"

# 3. Enable response caching in Redis (if available)
if docker ps | grep -q redis; then
    echo "Configuring Redis caching..."
    docker exec -it llmstack-redis redis-cli CONFIG SET maxmemory 1gb 2>/dev/null || echo "Redis not accessible"
    docker exec -it llmstack-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru 2>/dev/null || echo "Redis policy not set"
fi

# 4. Optimize PostgreSQL (if available)
if docker ps | grep -q postgres; then
    echo "Optimizing PostgreSQL..."
    docker exec -it llmstack-postgres psql -U postgres -c "ALTER SYSTEM SET shared_buffers = '512MB';" 2>/dev/null || echo "PostgreSQL optimization skipped"
    docker exec -it llmstack-postgres psql -U postgres -c "ALTER SYSTEM SET work_mem = '16MB';" 2>/dev/null || echo "PostgreSQL work_mem not set"
    docker restart llmstack-postgres 2>/dev/null || echo "PostgreSQL restart skipped"
fi

# 5. System-level optimizations
echo "Applying system optimizations..."

# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf 2>/dev/null || echo "Could not increase file descriptor limits (needs sudo)"
echo "* hard nofile 65536" >> /etc/security/limits.conf 2>/dev/null || echo "Could not increase file descriptor limits (needs sudo)"

# Optimize kernel parameters for AI workloads
echo "vm.swappiness=10" >> /etc/sysctl.conf 2>/dev/null || echo "Could not set swappiness (needs sudo)"
echo "vm.vfs_cache_pressure=50" >> /etc/sysctl.conf 2>/dev/null || echo "Could not set cache pressure (needs sudo)"

echo "✓ Optimization complete"
echo "Note: Some optimizations require sudo and will show warnings if not run as root"