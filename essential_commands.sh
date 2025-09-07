#!/bin/bash
set -e  # Exit on any error

# Essential commands from compass1 artifact PHASE_8

echo "=== LLMStack Essential Commands ==="
echo

case "$1" in
    "start")
        echo "Starting all services..."
        if [ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ]; then
            docker compose up -d || {
                echo "ERROR: Failed to start Docker services"
                exit 1
            }
        else
            echo "WARNING: No docker-compose file found in current directory"
        fi
        
        if command -v ollama >/dev/null 2>&1; then
            echo "Starting Ollama..."
            ollama serve &
        else
            echo "WARNING: Ollama not found"
        fi
        
        if [ -f "./lm-studio.AppImage" ]; then
            echo "Starting LM Studio..."
            ./lm-studio.AppImage server start --port 1234 &
        else
            echo "WARNING: LM Studio AppImage not found"
        fi
        ;;
    "stop")
        echo "Stopping all services..."
        docker compose down
        killall ollama
        killall lm-studio.AppImage
        ;;
    "logs")
        echo "Viewing logs..."
        docker logs llmstack-api
        docker logs flowise
        docker logs openhands
        ;;
    "models")
        echo "Available models:"
        ollama list
        curl http://localhost:1234/v1/models | jq '.data[].id'
        ;;
    "test")
        echo "Testing inference..."
        curl -X POST http://localhost:11434/v1/chat/completions \
          -H "Content-Type: application/json" \
          -d '{"model":"llama3.2:3b","messages":[{"role":"user","content":"Hello"}]}'
        ;;
    "monitor")
        echo "Monitoring resources..."
        docker stats
        nvidia-smi 2>/dev/null || echo "No GPU detected"
        ;;
    "backup")
        echo "Creating backup..."
        tar -czf llmstack-backup-$(date +%Y%m%d).tar.gz \
          ~/.ollama \
          ~/.flowise \
          ~/.continue \
          ~/llmstack/data
        ;;
    *)
        echo "Usage: $0 {start|stop|logs|models|test|monitor|backup}"
        ;;
esac
