#!/bin/bash
# Essential commands from compass1 artifact PHASE_8

echo "=== LLMStack Essential Commands ==="
echo

case "$1" in
    "start")
        echo "Starting all services..."
        docker compose up -d
        ollama serve &
        ./lm-studio.AppImage server start --port 1234 &
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
