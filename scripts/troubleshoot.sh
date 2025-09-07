#!/bin/bash
# Troubleshooting script for LLMStack deployment

echo "================================================================="
echo "  LLMSTACK TROUBLESHOOTING TOOL"
echo "================================================================="

run_diagnostics() {
    echo "Running system diagnostics..."
    echo
    
    # System resources
    echo "=== SYSTEM RESOURCES ==="
    echo "CPU cores: $(nproc)"
    echo "Memory: $(free -h | awk 'NR==2{printf "%.1fG used / %.1fG total (%.1f%%)", $3/1024/1024, $2/1024/1024, $3*100/$2 }')"
    echo "Disk space: $(df -h . | awk 'NR==2{print $4 " available"}')"
    
    if command -v nvidia-smi &> /dev/null; then
        echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits)"
        echo "GPU memory: $(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | head -1)"
    else
        echo "GPU: Not available"
    fi
    echo
    
    # Docker status
    echo "=== DOCKER STATUS ==="
    if command -v docker &> /dev/null; then
        echo "Docker version: $(docker --version)"
        echo "Docker status: $(systemctl is-active docker 2>/dev/null || echo "Unknown")"
        echo "Running containers: $(docker ps --format 'table {{.Names}}\t{{.Status}}' | wc -l) containers"
        docker ps --format "  - {{.Names}}: {{.Status}}"
    else
        echo "Docker: Not installed"
    fi
    echo
    
    # Port usage
    echo "=== PORT USAGE ==="
    check_port() {
        local port=$1
        local service=$2
        if lsof -i :$port >/dev/null 2>&1; then
            echo "  Port $port ($service): IN USE"
        else
            echo "  Port $port ($service): Available"
        fi
    }
    
    check_port 3000 "LLMStack"
    check_port 3001 "Flowise" 
    check_port 3002 "OpenHands"
    check_port 3003 "Grafana"
    check_port 9090 "Prometheus"
    check_port 11434 "Ollama"
    check_port 1234 "LM Studio"
    check_port 8000 "vLLM"
    echo
}

check_services() {
    echo "=== SERVICE HEALTH CHECK ==="
    
    services=(
        "http://localhost:11434/api/tags|Ollama"
        "http://localhost:3000/api/health|LLMStack"
        "http://localhost:3001|Flowise"
        "http://localhost:3002/health|OpenHands"  
        "http://localhost:3003|Grafana"
        "http://localhost:9090|Prometheus"
        "http://localhost:1234/v1/models|LM Studio"
        "http://localhost:8000/v1/models|vLLM"
    )
    
    for service in "${services[@]}"; do
        url=$(echo $service | cut -d'|' -f1)
        name=$(echo $service | cut -d'|' -f2)
        
        if curl -s -f "$url" >/dev/null 2>&1; then
            echo "  ✓ $name: Healthy"
        else
            echo "  ✗ $name: Not responding"
        fi
    done
    echo
}

test_models() {
    echo "=== MODEL TESTING ==="
    
    # Test Ollama models
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "Ollama models:"
        curl -s http://localhost:11434/api/tags | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for model in data.get('models', []):
        print(f'  - {model[\"name\"]}')
except:
    print('  Error reading models')
"
        
        # Test inference
        echo "Testing Ollama inference..."
        response=$(curl -s -X POST http://localhost:11434/v1/chat/completions \
            -H "Content-Type: application/json" \
            -d '{"model":"llama3.2:3b","messages":[{"role":"user","content":"Hello"}],"max_tokens":5}' | \
            python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data['choices'][0]['message']['content'][:50])
except:
    print('Inference test failed')
")
        echo "  Response: $response"
    else
        echo "Ollama: Not available"
    fi
    echo
}

fix_common_issues() {
    echo "=== FIXING COMMON ISSUES ==="
    
    # Fix Docker permissions
    echo "Checking Docker permissions..."
    if ! docker ps >/dev/null 2>&1; then
        echo "  Adding user to docker group..."
        sudo usermod -aG docker $USER || echo "  Failed to add user to docker group"
        echo "  Please log out and back in for docker group changes to take effect"
    else
        echo "  Docker permissions: OK"
    fi
    
    # Clean up old containers
    echo "Cleaning up old containers..."
    docker system prune -f >/dev/null 2>&1 || echo "  Docker cleanup failed"
    echo "  Docker cleanup: Done"
    
    # Free up memory
    echo "Freeing up system memory..."
    sync
    echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || echo "  Memory cleanup requires sudo"
    echo "  Memory cleanup: Attempted"
    
    # Restart stuck services
    echo "Restarting potentially stuck services..."
    systemctl restart docker 2>/dev/null || echo "  Docker restart requires sudo"
    
    echo
}

generate_report() {
    local report_file="troubleshoot_report_$(date +%Y%m%d_%H%M%S).txt"
    
    echo "Generating troubleshooting report: $report_file"
    
    {
        echo "LLMStack Troubleshooting Report"
        echo "Generated: $(date)"
        echo "==============================="
        echo
        
        run_diagnostics
        check_services  
        test_models
        
        echo "=== DOCKER LOGS ==="
        echo "Recent Docker container logs:"
        for container in $(docker ps --format "{{.Names}}"); do
            echo
            echo "--- $container ---"
            docker logs "$container" --tail 10 2>&1
        done
        
        echo
        echo "=== SYSTEM LOGS ==="
        journalctl -u docker --no-pager --lines 10 2>/dev/null || echo "System logs not accessible"
        
    } > "$report_file"
    
    echo "Report saved to: $report_file"
    echo "You can share this report when seeking help."
}

# Interactive menu
while true; do
    echo
    echo "Choose an option:"
    echo "1. Run diagnostics"
    echo "2. Check service health" 
    echo "3. Test model inference"
    echo "4. Fix common issues"
    echo "5. Generate full report"
    echo "6. Exit"
    echo
    read -p "Enter choice (1-6): " choice
    
    case $choice in
        1) run_diagnostics ;;
        2) check_services ;;
        3) test_models ;;
        4) fix_common_issues ;;
        5) generate_report ;;
        6) echo "Exiting troubleshooting tool"; exit 0 ;;
        *) echo "Invalid choice. Please enter 1-6." ;;
    esac
done