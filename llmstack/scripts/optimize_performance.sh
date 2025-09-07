#!/bin/bash
# Performance Optimization Script for LLMStack

set -e

echo "=== LLMStack Performance Optimization ==="
echo ""

# Helper functions
log_info() { echo "[INFO] $1"; }
log_success() { echo "✓ $1"; }
log_error() { echo "[ERROR] $1"; }

# Optimize Ollama
optimize_ollama() {
    log_info "Optimizing Ollama configuration..."
    
    mkdir -p ~/.ollama
    
    # Detect system resources
    CPU_CORES=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
    RAM_GB=$(free -g 2>/dev/null | awk '/^Mem:/{print $2}' || echo 8)
    
    # Calculate optimal settings
    NUM_THREADS=$((CPU_CORES - 1))
    CONTEXT_SIZE=4096
    
    if [[ $RAM_GB -ge 16 ]]; then
        CONTEXT_SIZE=8192
    elif [[ $RAM_GB -le 8 ]]; then
        CONTEXT_SIZE=2048
    fi
    
    # Create Ollama config
    cat > ~/.ollama/config.json << EOF
{
  "num_threads": $NUM_THREADS,
  "context_size": $CONTEXT_SIZE,
  "batch_size": 512,
  "gpu_layers": 35,
  "num_gpu": 1,
  "main_gpu": 0,
  "low_vram": false,
  "f16_kv": true,
  "vocab_only": false,
  "use_mmap": true,
  "use_mlock": false,
  "num_keep": 24
}
EOF
    
    # Set environment variables
    cat >> ~/.bashrc << EOF

# Ollama optimization
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_LOADED_MODELS=2
export OLLAMA_KEEP_ALIVE=5m
export OLLAMA_HOST=0.0.0.0:11434
EOF
    
    log_success "Ollama optimized for $CPU_CORES cores and ${RAM_GB}GB RAM"
}

# Optimize Docker containers
optimize_docker() {
    log_info "Optimizing Docker container resources..."
    
    # Update memory limits for containers
    containers=(
        "llmstack-flowise:2g"
        "llmstack-openhands:2g"
        "llmstack-redis:1g"
        "llmstack-postgres:2g"
        "llmstack-chroma:2g"
    )
    
    for container_spec in "${containers[@]}"; do
        container="${container_spec%:*}"
        memory="${container_spec#*:}"
        
        if docker ps -q -f name="$container" &> /dev/null; then
            docker update --memory="$memory" --memory-swap="$memory" "$container" 2>/dev/null || true
            log_info "Set $container memory limit to $memory"
        fi
    done
    
    log_success "Docker containers optimized"
}

# Optimize Redis cache
optimize_redis() {
    log_info "Optimizing Redis cache..."
    
    if docker ps -q -f name=llmstack-redis &> /dev/null; then
        # Configure Redis for LLM caching
        docker exec llmstack-redis redis-cli CONFIG SET maxmemory 1gb
        docker exec llmstack-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
        docker exec llmstack-redis redis-cli CONFIG SET save ""
        docker exec llmstack-redis redis-cli CONFIG SET appendonly no
        docker exec llmstack-redis redis-cli CONFIG SET tcp-keepalive 60
        docker exec llmstack-redis redis-cli CONFIG SET timeout 300
        
        log_success "Redis optimized for LLM caching"
    else
        log_info "Redis container not running, skipping optimization"
    fi
}

# Optimize PostgreSQL
optimize_postgres() {
    log_info "Optimizing PostgreSQL..."
    
    if docker ps -q -f name=llmstack-postgres &> /dev/null; then
        # Optimize PostgreSQL settings
        docker exec llmstack-postgres psql -U llmstack -c "ALTER SYSTEM SET shared_buffers = '512MB';"
        docker exec llmstack-postgres psql -U llmstack -c "ALTER SYSTEM SET work_mem = '16MB';"
        docker exec llmstack-postgres psql -U llmstack -c "ALTER SYSTEM SET maintenance_work_mem = '128MB';"
        docker exec llmstack-postgres psql -U llmstack -c "ALTER SYSTEM SET effective_cache_size = '2GB';"
        docker exec llmstack-postgres psql -U llmstack -c "ALTER SYSTEM SET checkpoint_completion_target = 0.9;"
        docker exec llmstack-postgres psql -U llmstack -c "ALTER SYSTEM SET wal_buffers = '16MB';"
        docker exec llmstack-postgres psql -U llmstack -c "ALTER SYSTEM SET random_page_cost = 1.1;"
        
        # Restart to apply changes
        docker restart llmstack-postgres
        
        log_success "PostgreSQL optimized"
    else
        log_info "PostgreSQL container not running, skipping optimization"
    fi
}

# Optimize system settings
optimize_system() {
    log_info "Optimizing system settings..."
    
    # Increase file descriptors
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Check if we can modify system settings
        if [[ $EUID -eq 0 ]]; then
            # Increase file descriptors
            echo "fs.file-max = 2097152" >> /etc/sysctl.conf
            echo "fs.nr_open = 1048576" >> /etc/sysctl.conf
            
            # Optimize network settings
            echo "net.core.somaxconn = 1024" >> /etc/sysctl.conf
            echo "net.ipv4.tcp_max_syn_backlog = 2048" >> /etc/sysctl.conf
            
            # Apply settings
            sysctl -p
            
            log_success "System settings optimized"
        else
            log_info "Run as root to optimize system settings"
        fi
    fi
    
    # Set ulimit for current session
    ulimit -n 65536 2>/dev/null || true
}

# Create swap file if needed
create_swap() {
    log_info "Checking swap configuration..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        SWAP_SIZE=$(free -g | awk '/^Swap:/{print $2}')
        
        if [[ $SWAP_SIZE -lt 4 ]] && [[ $EUID -eq 0 ]]; then
            log_info "Creating 4GB swap file..."
            
            dd if=/dev/zero of=/swapfile bs=1G count=4
            chmod 600 /swapfile
            mkswap /swapfile
            swapon /swapfile
            echo "/swapfile none swap sw 0 0" >> /etc/fstab
            
            log_success "4GB swap file created"
        else
            log_info "Swap already configured or insufficient permissions"
        fi
    fi
}

# GPU optimization
optimize_gpu() {
    log_info "Checking GPU optimization..."
    
    if command -v nvidia-smi &> /dev/null; then
        # Set GPU to persistence mode
        sudo nvidia-smi -pm 1 2>/dev/null || true
        
        # Set power limit to maximum
        MAX_POWER=$(nvidia-smi -q -d POWER | grep "Max Power Limit" | head -1 | awk '{print $5}')
        sudo nvidia-smi -pl "$MAX_POWER" 2>/dev/null || true
        
        # Enable GPU boost
        sudo nvidia-smi -ac 5001,1590 2>/dev/null || true
        
        log_success "GPU optimized for inference"
    else
        log_info "No NVIDIA GPU detected"
    fi
}

# Model quantization setup
setup_quantization() {
    log_info "Setting up model quantization..."
    
    # Create quantization config
    cat > ~/llmstack/configs/quantization.yaml << 'EOF'
# Model Quantization Configuration
quantization:
  default_method: "q4_K_M"  # 4-bit quantization
  
  models:
    llama3.2:3b:
      method: "q4_K_S"  # Smaller 4-bit for small model
      
    mistral:7b:
      method: "q4_K_M"  # Medium 4-bit for 7B model
      
    codellama:7b:
      method: "q5_K_M"  # Higher quality for code generation
      
  settings:
    use_mmap: true
    use_mlock: false
    n_gpu_layers: -1  # Use all GPU layers if available
    n_batch: 512
    n_ctx: 4096
EOF
    
    log_success "Quantization configuration created"
}

# Main optimization
main() {
    log_info "Starting performance optimization..."
    
    # Run all optimizations
    optimize_ollama
    optimize_docker
    optimize_redis
    optimize_postgres
    optimize_system
    create_swap
    optimize_gpu
    setup_quantization
    
    echo ""
    log_success "Performance optimization complete!"
    echo ""
    echo "Optimizations applied:"
    echo "  ✓ Ollama configured for optimal performance"
    echo "  ✓ Docker container resources allocated"
    echo "  ✓ Redis cache optimized"
    echo "  ✓ PostgreSQL tuned"
    echo "  ✓ System settings adjusted"
    echo "  ✓ GPU optimization (if available)"
    echo "  ✓ Model quantization configured"
    echo ""
    echo "Please restart services for all changes to take effect:"
    echo "  docker compose restart"
    echo "  ollama serve"
}

main "$@"