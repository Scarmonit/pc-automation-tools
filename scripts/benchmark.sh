#!/bin/bash
set -e


# Logging functions
# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=== LLMStack Performance Benchmark ==="

# Function to test endpoint performance
test_endpoint() {
    local endpoint=$1
    local model=$2
    local name=$3
    
    echo "Testing $name..."
    
    start_time=$(date +%s.%N)
    response=$(curl -s -X POST "$endpoint/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"$model\",
            \"messages\": [{\"role\": \"user\", \"content\": \"Count to 5\"}],
            \"max_tokens\": 50,
            \"temperature\": 0
        }")
    end_time=$(date +%s.%N)
    
    if [ $? -eq 0 ] && echo "$response" | grep -q "choices"; then
        duration=$(echo "$end_time - $start_time" | bc -l)
        printf "  ✓ %s: %.2fs\n" "$name" "$duration"
        return 0
    else
        echo "  ❌ $name: Failed"
        return 1
    fi
}

# Test Ollama
echo "Benchmarking Ollama models..."
test_endpoint "http://localhost:11434" "llama3.2:3b" "Llama 3.2 3B"
test_endpoint "http://localhost:11434" "mistral:7b-instruct" "Mistral 7B"
test_endpoint "http://localhost:11434" "codellama:7b" "CodeLlama 7B"

# Test vLLM if running
if docker ps | grep -q vllm; then
    echo "Benchmarking vLLM GPU acceleration..."
    test_endpoint "http://localhost:8000" "mistral:7b" "vLLM Mistral 7B"
fi

# Memory usage check
echo "Checking system resources..."
echo "  Memory usage:"
free -h | grep -E "(Mem|Swap)"

echo "  GPU usage:"
if nvidia-smi > /dev/null 2>&1; then
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits
else
    echo "    No GPU detected"
fi

# Container resource usage
echo "  Container resource usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -10

echo "=== Benchmark Complete ==="