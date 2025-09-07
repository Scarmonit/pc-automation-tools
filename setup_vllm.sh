#!/bin/bash
# Create vLLM configuration
mkdir -p ~/llmstack/vllm
cat > ~/llmstack/vllm/docker-compose.yml << 'EOF'
version: '3.8'
services:
  vllm:
    image: vllm/vllm-openai:latest
    ports:
      - "8000:8000"
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
    environment:
      - HF_HOME=/root/.cache/huggingface
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    command: >
      --model microsoft/Phi-3-mini-4k-instruct
      --gpu-memory-utilization 0.8
      --max-model-len 4096
      --port 8000
EOF

# Start vLLM (only if GPU available)
if command -v nvidia-smi &> /dev/null; then
    cd ~/llmstack/vllm
    docker compose up -d
    sleep 10
    curl http://localhost:8000/v1/models && echo "✓ vLLM running" || echo "⚠ vLLM not available"
fi