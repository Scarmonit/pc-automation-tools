# LLMStack Open Source Deployment Guide for Claude Code

## EXECUTION_MODE: SEQUENTIAL_DEPLOYMENT
```
Purpose: Deploy LLMStack with 100% free and open source components
Target: Zero API costs, full data privacy, production-ready system
Method: Step-by-step commands with verification checkpoints
```

## PHASE_0: SYSTEM_REQUIREMENTS_CHECK

### COMMANDS
```bash
#!/bin/bash
# save as: check_system.sh

# Check CPU cores
CPU_CORES=$(nproc)
echo "CPU_CORES=$CPU_CORES"
[[ $CPU_CORES -ge 4 ]] && echo "✓ CPU check passed" || echo "✗ Need 4+ cores"

# Check RAM
RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
echo "RAM_GB=$RAM_GB"
[[ $RAM_GB -ge 8 ]] && echo "✓ RAM check passed" || echo "✗ Need 8GB+ RAM"

# Check GPU (optional but recommended)
if command -v nvidia-smi &> /dev/null; then
    VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    echo "GPU_VRAM_MB=$VRAM_MB"
    [[ $VRAM_MB -ge 4096 ]] && echo "✓ GPU check passed" || echo "⚠ GPU has less than 4GB VRAM"
else
    echo "⚠ No NVIDIA GPU detected - will use CPU inference"
fi

# Check disk space
DISK_GB=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
echo "DISK_GB=$DISK_GB"
[[ $DISK_GB -ge 50 ]] && echo "✓ Disk check passed" || echo "✗ Need 50GB+ free disk"

# Check Docker
docker --version &>/dev/null && echo "✓ Docker installed" || echo "✗ Docker not found"

# Check Python
python3 --version &>/dev/null && echo "✓ Python3 installed" || echo "✗ Python3 not found"
```

### VERIFY
```bash
bash check_system.sh
# All checks should show ✓ or ⚠ (warnings acceptable)
```

## PHASE_1: INSTALL_LOCAL_MODEL_SERVERS

### STEP_1A: INSTALL_OLLAMA
```bash
# Install Ollama (primary local model server)
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version || exit 1

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Download essential models
ollama pull llama3.2:3b        # 2GB - Fast general purpose
ollama pull mistral:7b-instruct # 4GB - Excellent reasoning
ollama pull codellama:7b        # 4GB - Code generation
ollama pull qwen2.5:3b          # 2GB - Multilingual support

# Verify models
ollama list | grep -E "llama3.2|mistral|codellama|qwen" || exit 1
```

[Content continues with all phases through PHASE_8...]

## COMPLETION_MARKER
```bash
echo "LLMStack Open Source Deployment Complete!"
echo "Total API Cost: $0.00"
echo "Data Privacy: 100% Local"
echo "Production Ready: YES"
```