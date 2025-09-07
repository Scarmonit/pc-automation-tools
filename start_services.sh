#!/bin/bash
# Start all services
cd "$LLMSTACK_HOME"
docker compose up -d
ollama serve
./lm-studio.AppImage server start --port 1234 &