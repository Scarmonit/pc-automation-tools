
# Windows PowerShell optimization script
$optimizations = @"
# Increase Ollama memory allocation
$env:OLLAMA_MAX_LOADED_MODELS = 1
$env:OLLAMA_NUM_PARALLEL = 4
$env:OLLAMA_MAX_QUEUE = 100
$env:OLLAMA_FLASH_ATTENTION = 1
$env:OLLAMA_KEEP_ALIVE = "24h"

# GPU acceleration (if available)
$env:CUDA_VISIBLE_DEVICES = 0
$env:OLLAMA_GPU_LAYERS = 99

# CPU optimization
$env:OMP_NUM_THREADS = 32
$env:MKL_NUM_THREADS = 32

Write-Host "System optimized for DOLPHIN-MAX"
"@

# Save to file
$optimizations | Out-File -FilePath "optimize_dolphin.ps1"
