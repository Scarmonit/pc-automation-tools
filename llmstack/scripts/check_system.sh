#!/bin/bash
# System Requirements Check Script

set -e

echo "=== System Requirements Check ==="
echo ""

PASSED=0
FAILED=0
WARNINGS=0

# Check CPU cores
CPU_CORES=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 1)
echo "CPU Cores: $CPU_CORES"
if [[ $CPU_CORES -ge 4 ]]; then
    echo "✓ CPU check passed (4+ cores)"
    ((PASSED++))
else
    echo "✗ Need 4+ cores for optimal performance"
    ((FAILED++))
fi

# Check RAM
if command -v free &> /dev/null; then
    RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
elif command -v sysctl &> /dev/null; then
    RAM_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
    RAM_GB=$((RAM_BYTES / 1073741824))
else
    RAM_GB=0
fi

echo "RAM: ${RAM_GB}GB"
if [[ $RAM_GB -ge 8 ]]; then
    echo "✓ RAM check passed (8GB+)"
    ((PASSED++))
else
    echo "✗ Need 8GB+ RAM"
    ((FAILED++))
fi

# Check GPU (optional but recommended)
if command -v nvidia-smi &> /dev/null; then
    VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 || echo 0)
    echo "GPU VRAM: ${VRAM_MB}MB"
    if [[ $VRAM_MB -ge 4096 ]]; then
        echo "✓ GPU check passed (4GB+ VRAM)"
        ((PASSED++))
    else
        echo "⚠ GPU has less than 4GB VRAM"
        ((WARNINGS++))
    fi
else
    echo "⚠ No NVIDIA GPU detected - will use CPU inference"
    ((WARNINGS++))
fi

# Check disk space
if command -v df &> /dev/null; then
    DISK_GB=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    echo "Free Disk Space: ${DISK_GB}GB"
    if [[ $DISK_GB -ge 50 ]]; then
        echo "✓ Disk check passed (50GB+ free)"
        ((PASSED++))
    else
        echo "✗ Need 50GB+ free disk space"
        ((FAILED++))
    fi
fi

# Check Docker
if docker --version &>/dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    echo "Docker Version: $DOCKER_VERSION"
    echo "✓ Docker installed"
    ((PASSED++))
    
    # Check Docker Compose
    if docker compose version &>/dev/null; then
        echo "✓ Docker Compose installed"
        ((PASSED++))
    else
        echo "✗ Docker Compose not found"
        ((FAILED++))
    fi
else
    echo "✗ Docker not found - please install Docker"
    ((FAILED++))
fi

# Check Python
if python3 --version &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "Python Version: $PYTHON_VERSION"
    echo "✓ Python3 installed"
    ((PASSED++))
else
    echo "✗ Python3 not found"
    ((FAILED++))
fi

# Check Node.js (for some components)
if node --version &>/dev/null; then
    NODE_VERSION=$(node --version)
    echo "Node.js Version: $NODE_VERSION"
    echo "✓ Node.js installed"
    ((PASSED++))
else
    echo "⚠ Node.js not found (optional but recommended)"
    ((WARNINGS++))
fi

# Check Git
if git --version &>/dev/null; then
    echo "✓ Git installed"
    ((PASSED++))
else
    echo "✗ Git not found"
    ((FAILED++))
fi

# Check curl
if curl --version &>/dev/null; then
    echo "✓ curl installed"
    ((PASSED++))
else
    echo "✗ curl not found"
    ((FAILED++))
fi

# Summary
echo ""
echo "=== Summary ==="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Warnings: $WARNINGS"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo "✓ System meets all requirements!"
    echo "You can proceed with installation."
    exit 0
else
    echo "✗ System does not meet all requirements."
    echo "Please address the failed checks before proceeding."
    exit 1
fi