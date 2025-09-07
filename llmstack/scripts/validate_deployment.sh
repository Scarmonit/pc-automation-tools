#!/bin/bash
# LLMStack Deployment Validation Script

set -e

echo "=== LLMStack Free Agent Validation ==="
echo "$(date)"
echo "======================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
ERRORS=0
WARNINGS=0
PASSED=0

# Helper functions
check_service() {
    local name="$1"
    local url="$2"
    local expected="${3:-200}"
    
    printf "Checking %-20s ... " "$name"
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [[ "$response" == "$expected" ]]; then
            echo -e "${GREEN}✓ Running${NC}"
            ((PASSED++))
            return 0
        else
            echo -e "${RED}✗ HTTP $response${NC}"
            ((ERRORS++))
            return 1
        fi
    else
        echo -e "${RED}✗ Not accessible${NC}"
        ((ERRORS++))
        return 1
    fi
}

check_port() {
    local name="$1"
    local port="$2"
    
    printf "Checking %-20s ... " "$name port $port"
    
    if nc -z localhost "$port" 2>/dev/null; then
        echo -e "${GREEN}✓ Open${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠ Closed${NC}"
        ((WARNINGS++))
        return 1
    fi
}

test_inference() {
    local endpoint="$1"
    local model="$2"
    local name="$3"
    
    printf "Testing %-20s ... " "$name inference"
    
    response=$(curl -s -X POST "$endpoint/chat/completions" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"$model\",
            \"messages\": [{\"role\": \"user\", \"content\": \"Say hello\"}],
            \"max_tokens\": 10,
            \"temperature\": 0
        }" 2>/dev/null | jq -r '.choices[0].message.content' 2>/dev/null)
    
    if [[ -n "$response" ]] && [[ "$response" != "null" ]]; then
        echo -e "${GREEN}✓ Working${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        ((ERRORS++))
        return 1
    fi
}

check_docker_container() {
    local container="$1"
    
    printf "Checking %-20s ... " "$container"
    
    if docker ps --format "table {{.Names}}" | grep -q "$container"; then
        status=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null)
        if [[ "$status" == "running" ]]; then
            echo -e "${GREEN}✓ Running${NC}"
            ((PASSED++))
            return 0
        else
            echo -e "${YELLOW}⚠ Status: $status${NC}"
            ((WARNINGS++))
            return 1
        fi
    else
        echo -e "${RED}✗ Not found${NC}"
        ((ERRORS++))
        return 1
    fi
}

check_disk_space() {
    printf "Checking disk space      ... "
    
    available=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    
    if [[ $available -ge 10 ]]; then
        echo -e "${GREEN}✓ ${available}GB available${NC}"
        ((PASSED++))
    elif [[ $available -ge 5 ]]; then
        echo -e "${YELLOW}⚠ ${available}GB available (low)${NC}"
        ((WARNINGS++))
    else
        echo -e "${RED}✗ ${available}GB available (critical)${NC}"
        ((ERRORS++))
    fi
}

check_memory() {
    printf "Checking memory          ... "
    
    if command -v free &> /dev/null; then
        available=$(free -m | awk '/^Mem:/{print $7}')
        total=$(free -m | awk '/^Mem:/{print $2}')
        percent=$((available * 100 / total))
        
        if [[ $percent -ge 20 ]]; then
            echo -e "${GREEN}✓ ${available}MB available (${percent}%)${NC}"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠ ${available}MB available (${percent}%)${NC}"
            ((WARNINGS++))
        fi
    else
        echo -e "${YELLOW}⚠ Cannot check${NC}"
        ((WARNINGS++))
    fi
}

# Main validation
echo -e "${BLUE}=== Core Services ===${NC}"
check_service "LLMStack API" "http://localhost:3000/api/health"
check_service "Ollama" "http://localhost:11434/api/tags"
check_service "LM Studio" "http://localhost:1234/v1/models"
check_service "Flowise" "http://localhost:3001"
check_service "OpenHands" "http://localhost:3002/health"
check_service "Grafana" "http://localhost:3003"
check_service "Prometheus" "http://localhost:9090/-/ready"

echo ""
echo -e "${BLUE}=== Docker Containers ===${NC}"
check_docker_container "llmstack-postgres"
check_docker_container "llmstack-redis"
check_docker_container "llmstack-chroma"
check_docker_container "llmstack-api"
check_docker_container "llmstack-flowise"
check_docker_container "llmstack-openhands"
check_docker_container "llmstack-grafana"
check_docker_container "llmstack-prometheus"

echo ""
echo -e "${BLUE}=== Network Ports ===${NC}"
check_port "PostgreSQL" 5432
check_port "Redis" 6379
check_port "ChromaDB" 8001
check_port "LLMStack" 3000
check_port "Flowise" 3001
check_port "OpenHands" 3002
check_port "Grafana" 3003
check_port "Prometheus" 9090
check_port "Ollama" 11434
check_port "LM Studio" 1234

echo ""
echo -e "${BLUE}=== Model Inference ===${NC}"
test_inference "http://localhost:11434/v1" "llama3.2:3b" "Ollama"
# test_inference "http://localhost:1234/v1" "auto" "LM Studio"

echo ""
echo -e "${BLUE}=== System Resources ===${NC}"
check_disk_space
check_memory

echo ""
echo -e "${BLUE}=== Model Availability ===${NC}"
printf "Checking Ollama models   ... "
models=$(ollama list 2>/dev/null | tail -n +2 | wc -l)
if [[ $models -gt 0 ]]; then
    echo -e "${GREEN}✓ $models models available${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ No models found${NC}"
    ((ERRORS++))
fi

# Performance test
echo ""
echo -e "${BLUE}=== Performance Test ===${NC}"
printf "Testing response time    ... "
start_time=$(date +%s%N)
curl -s -X POST http://localhost:11434/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "llama3.2:3b",
        "messages": [{"role": "user", "content": "Count to 3"}],
        "max_tokens": 20,
        "stream": false
    }' > /dev/null 2>&1
end_time=$(date +%s%N)
response_time=$(( (end_time - start_time) / 1000000 ))

if [[ $response_time -lt 5000 ]]; then
    echo -e "${GREEN}✓ ${response_time}ms${NC}"
    ((PASSED++))
elif [[ $response_time -lt 10000 ]]; then
    echo -e "${YELLOW}⚠ ${response_time}ms (slow)${NC}"
    ((WARNINGS++))
else
    echo -e "${RED}✗ ${response_time}ms (very slow)${NC}"
    ((ERRORS++))
fi

# Summary
echo ""
echo "======================================="
echo -e "${BLUE}=== Validation Summary ===${NC}"
echo "======================================="
echo -e "Passed:   ${GREEN}$PASSED${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo -e "Errors:   ${RED}$ERRORS${NC}"
echo ""

if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}✓ All critical systems operational!${NC}"
    echo ""
    echo "Access Points:"
    echo "  LLMStack UI:  http://localhost:3000"
    echo "  Flowise:      http://localhost:3001"
    echo "  OpenHands:    http://localhost:3002"
    echo "  Grafana:      http://localhost:3003 (admin/admin)"
    echo "  Prometheus:   http://localhost:9090"
    echo ""
    echo "API Endpoints:"
    echo "  Ollama:       http://localhost:11434/v1"
    echo "  LM Studio:    http://localhost:1234/v1"
    echo "  ChromaDB:     http://localhost:8001"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Validation failed with $ERRORS errors${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check service logs: docker logs <container-name>"
    echo "  2. Verify ports: sudo lsof -i :<port>"
    echo "  3. Check resources: docker stats"
    echo "  4. Review configuration: cat docker/.env"
    echo ""
    exit 1
fi