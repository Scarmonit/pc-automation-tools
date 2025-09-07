#!/bin/bash
set -e  # Exit on any error

echo "=== LLMStack Free Agent Validation ==="
echo

ERRORS=0
WARNINGS=0

# Function to check service
check_service() {
    local name="$1"
    local url="$2"
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✓ $name is running"
        return 0
    else
        echo "✗ $name is not accessible"
        ((ERRORS++))
        return 1
    fi
}

# Core services
check_service "LLMStack" "http://localhost:3000/api/health"
check_service "Ollama" "http://localhost:11434/api/tags"
check_service "LM Studio" "http://localhost:1234/v1/models"
check_service "Flowise" "http://localhost:3001"
check_service "OpenHands" "http://localhost:3002/health"
check_service "Grafana" "http://localhost:3003"

# Test model inference
echo
echo "Testing model inference..."
response=$(curl -s -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 10
  }' | jq -r '.choices[0].message.content' 2>/dev/null)

if [[ -n "$response" ]]; then
    echo "✓ Model inference working: $response"
else
    echo "✗ Model inference failed"
    ((ERRORS++))
fi

# Summary
echo
echo "=== Validation Summary ==="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [[ $ERRORS -eq 0 ]]; then
    echo "✓ All systems operational!"
    echo
    echo "Access points:"
    echo "  LLMStack UI: http://localhost:3000"
    echo "  Flowise: http://localhost:3001"
    echo "  Monitoring: http://localhost:3003 (admin/admin)"
    echo
    echo "API Endpoints:"
    echo "  Ollama: http://localhost:11434/v1"
    echo "  LM Studio: http://localhost:1234/v1"
    echo "  Jan: http://localhost:1337/v1"
    exit 0
else
    echo "✗ Validation failed with $ERRORS errors"
    exit 1
fi