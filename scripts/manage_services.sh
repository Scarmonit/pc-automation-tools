#!/bin/bash
# Service management script

COMMAND="$1"

show_usage() {
    echo "Usage: $0 {start|stop|restart|status|logs}"
    echo
    echo "Commands:"
    echo "  start   - Start all LLMStack services"
    echo "  stop    - Stop all services gracefully"  
    echo "  restart - Restart all services"
    echo "  status  - Show service status"
    echo "  logs    - Show service logs"
}

start_services() {
    echo "Starting LLMStack services..."
    
    # Start Ollama
    if command -v ollama &> /dev/null; then
        echo "Starting Ollama..."
        ollama serve &
        sleep 3
    fi
    
    # Start LLMStack
    if [ -d ~/llmstack/LLMStack ]; then
        echo "Starting LLMStack..."
        cd ~/llmstack/LLMStack
        docker compose -f docker/docker-compose.yml --env-file docker/.env.production up -d
    fi
    
    # Start monitoring
    if [ -d ~/llmstack/monitoring ]; then
        echo "Starting monitoring..."
        cd ~/llmstack/monitoring
        docker compose up -d
    fi
    
    # Start LM Studio
    if [ -f ~/lm-studio.AppImage ]; then
        echo "Starting LM Studio..."
        ~/lm-studio.AppImage server start --port 1234 --cors &
    fi
    
    # Start vLLM
    if [ -d ~/llmstack/vllm ]; then
        echo "Starting vLLM..."
        cd ~/llmstack/vllm
        docker compose up -d
    fi
    
    echo "✓ Services startup initiated"
}

stop_services() {
    echo "Stopping LLMStack services..."
    
    # Stop Docker containers
    docker compose down 2>/dev/null || true
    
    # Stop Ollama
    killall ollama 2>/dev/null || true
    
    # Stop LM Studio
    killall lm-studio.AppImage 2>/dev/null || true
    
    echo "✓ Services stopped"
}

restart_services() {
    echo "Restarting LLMStack services..."
    stop_services
    sleep 5
    start_services
}

show_status() {
    echo "LLMStack Service Status:"
    echo "======================="
    
    # Check Ollama
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✓ Ollama: Running (http://localhost:11434)"
    else
        echo "✗ Ollama: Not running"
    fi
    
    # Check LLMStack
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo "✓ LLMStack: Running (http://localhost:3000)"
    else
        echo "✗ LLMStack: Not running"
    fi
    
    # Check Flowise
    if curl -s http://localhost:3001 > /dev/null 2>&1; then
        echo "✓ Flowise: Running (http://localhost:3001)"
    else
        echo "✗ Flowise: Not running"
    fi
    
    # Check OpenHands
    if curl -s http://localhost:3002/health > /dev/null 2>&1; then
        echo "✓ OpenHands: Running (http://localhost:3002)"
    else
        echo "✗ OpenHands: Not running"
    fi
    
    # Check Grafana
    if curl -s http://localhost:3003 > /dev/null 2>&1; then
        echo "✓ Grafana: Running (http://localhost:3003)"
    else
        echo "✗ Grafana: Not running"
    fi
    
    # Check LM Studio
    if curl -s http://localhost:1234/v1/models > /dev/null 2>&1; then
        echo "✓ LM Studio: Running (http://localhost:1234)"
    else
        echo "✗ LM Studio: Not running"
    fi
    
    # Check vLLM
    if curl -s http://localhost:8000/v1/models > /dev/null 2>&1; then
        echo "✓ vLLM: Running (http://localhost:8000)"
    else
        echo "✗ vLLM: Not running"
    fi
    
    echo
    echo "Docker containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

show_logs() {
    echo "Recent service logs:"
    echo "==================="
    
    echo
    echo "LLMStack logs:"
    docker logs llmstack-api --tail 20 2>/dev/null || echo "No LLMStack logs available"
    
    echo
    echo "Flowise logs:"
    docker logs flowise --tail 20 2>/dev/null || echo "No Flowise logs available"
    
    echo
    echo "OpenHands logs:"  
    docker logs openhands --tail 20 2>/dev/null || echo "No OpenHands logs available"
}

case "$COMMAND" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    *)
        show_usage
        exit 1
        ;;
esac