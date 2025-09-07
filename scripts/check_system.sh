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