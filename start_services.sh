#!/bin/bash
set -e  # Exit on any error

# Start all services
echo "Starting LLMStack services..."

# Check if LLMSTACK_HOME is set
if [ -z "$LLMSTACK_HOME" ]; then
    export LLMSTACK_HOME="$HOME/llmstack"
    echo "LLMSTACK_HOME not set, using default: $LLMSTACK_HOME"
fi

# Navigate to LLMStack directory
if [ -d "$LLMSTACK_HOME" ]; then
    cd "$LLMSTACK_HOME" || {
        echo "ERROR: Failed to navigate to $LLMSTACK_HOME"
        exit 1
    }
    echo "Starting Docker services..."
    docker compose up -d
else
    echo "WARNING: $LLMSTACK_HOME not found, skipping Docker services"
fi

# Start Ollama server
echo "Starting Ollama server..."
if command -v ollama >/dev/null 2>&1; then
    ollama serve &
    echo "✓ Ollama server started"
else
    echo "WARNING: Ollama not found, please install it first"
fi

# Start LM Studio (if available)
if [ -f "./lm-studio.AppImage" ]; then
    echo "Starting LM Studio server..."
    ./lm-studio.AppImage server start --port 1234 &
    echo "✓ LM Studio server started on port 1234"
else
    echo "WARNING: lm-studio.AppImage not found, skipping LM Studio"
fi

echo "✓ Service startup completed"