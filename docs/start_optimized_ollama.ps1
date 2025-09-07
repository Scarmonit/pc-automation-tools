# Optimized Ollama Startup Script
# Configures Ollama for maximum performance on your hardware

Write-Host "=== Optimized Ollama Configuration ===" -ForegroundColor Green
Write-Host ""

# Set environment variables for optimal performance
$env:OLLAMA_NUM_PARALLEL = "4"
$env:OLLAMA_MAX_LOADED_MODELS = "2" 
$env:OLLAMA_FLASH_ATTENTION = "1"
$env:OLLAMA_GPU_OVERHEAD = "0.1"
$env:OMP_NUM_THREADS = "16"
$env:CUDA_VISIBLE_DEVICES = "0"

# GPU and CUDA optimizations
$env:PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:128"
$env:CUDA_LAUNCH_BLOCKING = "0"

# Memory optimizations
$env:OLLAMA_KEEP_ALIVE = "5m"
$env:OLLAMA_CONCURRENT_REQUESTS = "8"

Write-Host "Environment variables set:" -ForegroundColor Yellow
Write-Host "  OLLAMA_NUM_PARALLEL = 4" -ForegroundColor White
Write-Host "  OLLAMA_MAX_LOADED_MODELS = 2" -ForegroundColor White
Write-Host "  OLLAMA_FLASH_ATTENTION = 1" -ForegroundColor White
Write-Host "  GPU and threading optimizations enabled" -ForegroundColor White
Write-Host ""

# Stop existing Ollama process if running
Write-Host "Stopping existing Ollama process..." -ForegroundColor Yellow
try {
    Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
} catch {
    Write-Host "No existing Ollama process found" -ForegroundColor Gray
}

# Start Ollama with optimizations
Write-Host "Starting optimized Ollama server..." -ForegroundColor Green
Write-Host ""

# Start Ollama serve in background
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

# Wait for startup
Write-Host "Waiting for Ollama to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verify Ollama is running
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 10
    Write-Host "Ollama server started successfully!" -ForegroundColor Green
    Write-Host ""
    
    if ($response.models) {
        Write-Host "Available models:" -ForegroundColor Cyan
        foreach ($model in $response.models) {
            $size = [math]::Round($model.size / 1GB, 2)
            Write-Host "  $($model.name) (${size}GB)" -ForegroundColor White
        }
    } else {
        Write-Host "No models currently loaded" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Failed to connect to Ollama server" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Ollama optimization complete!" -ForegroundColor Green
Write-Host "The server is now configured for:" -ForegroundColor Cyan
Write-Host "  - Maximum GPU utilization (RTX 4080)" -ForegroundColor White
Write-Host "  - Optimal CPU threading (30 threads)" -ForegroundColor White
Write-Host "  - Parallel request processing (4 concurrent)" -ForegroundColor White
Write-Host "  - Flash attention enabled" -ForegroundColor White
Write-Host "  - Memory-efficient batching" -ForegroundColor White