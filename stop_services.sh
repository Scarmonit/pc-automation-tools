#!/bin/bash
set -e  # Exit on any error

echo "Stopping all LLMStack services..."

# Stop Docker services
if command -v docker >/dev/null 2>&1; then
    echo "Stopping Docker containers..."
    docker compose down 2>/dev/null || echo "WARNING: No docker-compose services to stop"
else
    echo "WARNING: Docker not available"
fi

# Stop Ollama
echo "Stopping Ollama..."
if pgrep -f "ollama" >/dev/null; then
    killall ollama 2>/dev/null || echo "WARNING: Failed to stop Ollama"
    echo "✓ Ollama stopped"
else
    echo "Ollama not running"
fi

# Stop LM Studio
echo "Stopping LM Studio..."
if pgrep -f "lm-studio.AppImage" >/dev/null; then
    killall lm-studio.AppImage 2>/dev/null || echo "WARNING: Failed to stop LM Studio"
    echo "✓ LM Studio stopped"
else
    echo "LM Studio not running"
fi

echo "✓ All services stopped successfully"