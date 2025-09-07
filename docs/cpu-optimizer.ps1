# CPU Optimization Suite for AI Swarm Intelligence System
# Optimized for Intel i9-13900K (32 logical processors)

param(
    [switch]$Full,
    [switch]$Docker,
    [switch]$Windows,
    [switch]$Monitor,
    [switch]$Analyze
)

Write-Host "🚀 AI Swarm CPU Optimizer - Intel i9-13900K Edition" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# System Information
function Get-SystemInfo {
    Write-Host "`n📊 System Analysis:" -ForegroundColor Green
    
    $cpu = Get-ComputerInfo | Select-Object CsProcessors, CsNumberOfProcessors, CsNumberOfLogicalProcessors
    $memory = Get-ComputerInfo | Select-Object TotalPhysicalMemory
    
    Write-Host "CPU: $($cpu.CsProcessors)" -ForegroundColor White
    Write-Host "Physical Cores: $($cpu.CsNumberOfProcessors)" -ForegroundColor White
    Write-Host "Logical Processors: $($cpu.CsNumberOfLogicalProcessors)" -ForegroundColor White
    Write-Host "Total RAM: $([math]::Round($memory.TotalPhysicalMemory / 1GB, 2)) GB" -ForegroundColor White
    
    return $cpu.CsNumberOfLogicalProcessors
}

# Docker CPU Optimization
function Optimize-DockerCPU {
    param($LogicalProcessors)
    
    Write-Host "`n🐳 Optimizing Docker CPU Allocation..." -ForegroundColor Yellow
    
    # Calculate optimal CPU allocation
    $DockerCPUs = [math]::Floor($LogicalProcessors * 0.75)  # Use 75% of cores
    $SwarmCPUs = [math]::Floor($LogicalProcessors * 0.5)    # 50% for Swarm Master
    $WorkerCPUs = [math]::Floor($LogicalProcessors * 0.25)  # 25% for Workers
    $CacheCPUs = 2                                          # 2 cores for Redis
    
    Write-Host "Recommended CPU allocation:" -ForegroundColor Green
    Write-Host "  Docker Total: $DockerCPUs cores" -ForegroundColor White
    Write-Host "  Swarm Master: $SwarmCPUs cores" -ForegroundColor White
    Write-Host "  Workers: $WorkerCPUs cores each" -ForegroundColor White
    Write-Host "  Redis Cache: $CacheCPUs cores" -ForegroundColor White
    
    # Create optimized Docker Compose
    $OptimizedCompose = @"
version: '3.8'

# CPU-Optimized AI Swarm for Intel i9-13900K
services:
  swarm-master:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: swarm-master-optimized
    ports:
      - "8000:8000"
    environment:
      - SWARM_MODE=production
      - CPU_THREADS=$SwarmCPUs
      - WORKER_PROCESSES=$([math]::Min(8, $SwarmCPUs))
      - OMP_NUM_THREADS=$SwarmCPUs
      - NUMBA_NUM_THREADS=$SwarmCPUs
    deploy:
      resources:
        limits:
          cpus: '$SwarmCPUs'
          memory: 8G
        reservations:
          cpus: '$([math]::Floor($SwarmCPUs * 0.5))'
          memory: 2G
    cpuset: "0-$($SwarmCPUs-1)"
    volumes:
      - ./data:/data
      - ./logs:/logs
    networks:
      - swarm-network
    restart: unless-stopped

  swarm-worker-1:
    build:
      context: .
      dockerfile: Dockerfile.worker
    container_name: swarm-worker-1-optimized
    environment:
      - SWARM_MODE=worker
      - MASTER_HOST=swarm-master-optimized
      - CPU_THREADS=$WorkerCPUs
      - WORKER_PROCESSES=$([math]::Min(4, $WorkerCPUs))
    deploy:
      resources:
        limits:
          cpus: '$WorkerCPUs'
          memory: 4G
        reservations:
          cpus: '$([math]::Floor($WorkerCPUs * 0.5))'
          memory: 1G
    cpuset: "$SwarmCPUs-$($SwarmCPUs + $WorkerCPUs - 1)"
    volumes:
      - ./logs:/logs
    networks:
      - swarm-network
    restart: unless-stopped

  swarm-worker-2:
    build:
      context: .
      dockerfile: Dockerfile.worker
    container_name: swarm-worker-2-optimized
    environment:
      - SWARM_MODE=worker
      - MASTER_HOST=swarm-master-optimized
      - CPU_THREADS=$WorkerCPUs
      - WORKER_PROCESSES=$([math]::Min(4, $WorkerCPUs))
    deploy:
      resources:
        limits:
          cpus: '$WorkerCPUs'
          memory: 4G
        reservations:
          cpus: '$([math]::Floor($WorkerCPUs * 0.5))'
          memory: 1G
    cpuset: "$($SwarmCPUs + $WorkerCPUs)-$($SwarmCPUs + $WorkerCPUs * 2 - 1)"
    volumes:
      - ./logs:/logs
    networks:
      - swarm-network
    restart: unless-stopped

  swarm-cache-optimized:
    image: redis:7-alpine
    container_name: swarm-cache-optimized
    ports:
      - "6379:6379"
    command: >
      redis-server 
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
      --io-threads 4
      --io-threads-do-reads yes
    deploy:
      resources:
        limits:
          cpus: '$CacheCPUs'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
    cpuset: "$($LogicalProcessors - $CacheCPUs)-$($LogicalProcessors - 1)"
    volumes:
      - redis-data:/data
    networks:
      - swarm-network
    restart: unless-stopped

  # CPU Monitor
  cpu-monitor:
    image: prom/node-exporter:latest
    container_name: cpu-monitor
    ports:
      - "9100:9100"
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
    networks:
      - swarm-network
    restart: unless-stopped

networks:
  swarm-network:
    driver: bridge

volumes:
  redis-data:
"@

    Write-Host "`n📝 Creating optimized Docker Compose..." -ForegroundColor Green
    $OptimizedCompose | Out-File -FilePath "./docker-compose.cpu-optimized.yml" -Encoding UTF8
    
    Write-Host "✅ Created: docker-compose.cpu-optimized.yml" -ForegroundColor Green
}

# Windows CPU Optimization
function Optimize-WindowsCPU {
    Write-Host "`n🖥️ Optimizing Windows CPU Settings..." -ForegroundColor Yellow
    
    # Set Windows to High Performance mode
    try {
        powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
        Write-Host "✅ Set power plan to High Performance" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Could not set power plan (requires admin)" -ForegroundColor Yellow
    }
    
    # CPU Core Parking - Disable for better performance
    $CoreParkingScript = @"
# Disable CPU Core Parking for Intel i9-13900K
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\0cc5b647-c1df-4637-891a-dec35c318583" -Name "ValueMax" -Value 0
Write-Host "✅ CPU Core Parking disabled"

# Set processor performance boost mode to aggressive
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\be337238-0d82-4146-a960-4f3749d470c7" -Name "ValueMax" -Value 2
Write-Host "✅ Processor boost mode set to aggressive"

# Set minimum processor state to 100%
powercfg -setacvalueindex scheme_current 54533251-82be-4824-96c1-47b60b740d00 893dee8e-2bef-41e0-89c6-b55d0929964c 100
powercfg -setactive scheme_current
Write-Host "✅ Minimum processor state set to 100%"
"@

    Write-Host "📝 Creating CPU optimization script (requires admin)..." -ForegroundColor Green
    $CoreParkingScript | Out-File -FilePath "./windows-cpu-optimize.ps1" -Encoding UTF8
    
    Write-Host "ℹ️ To apply Windows optimizations, run as Administrator:" -ForegroundColor Cyan
    Write-Host "   PowerShell -ExecutionPolicy Bypass -File .\windows-cpu-optimize.ps1" -ForegroundColor White
    
    # Process Priority Optimization
    Write-Host "`n🔧 Optimizing process priorities..." -ForegroundColor Yellow
    
    # Set Docker processes to high priority
    try {
        $dockerProcesses = Get-Process | Where-Object {$_.ProcessName -like "*docker*" -or $_.ProcessName -like "*swarm*"}
        foreach ($process in $dockerProcesses) {
            $process.PriorityClass = "High"
        }
        Write-Host "✅ Set Docker processes to high priority" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Could not modify process priorities" -ForegroundColor Yellow
    }
}

# AI Swarm Optimization
function Optimize-AISwarm {
    param($LogicalProcessors)
    
    Write-Host "`n🧠 Optimizing AI Swarm Configuration..." -ForegroundColor Yellow
    
    # Calculate optimal threading
    $AIThreads = [math]::Floor($LogicalProcessors * 0.6)
    $WorkerThreads = [math]::Floor($LogicalProcessors * 0.3)
    $IOThreads = [math]::Min(8, [math]::Floor($LogicalProcessors * 0.1))
    
    # Create AI Swarm configuration
    $AIConfig = @{
        "cpu_optimization" = @{
            "total_cores" = $LogicalProcessors
            "ai_threads" = $AIThreads
            "worker_threads" = $WorkerThreads
            "io_threads" = $IOThreads
            "numa_enabled" = $true
            "cpu_affinity" = $true
        }
        "performance_settings" = @{
            "batch_size" = 32
            "queue_size" = 1000
            "connection_pool_size" = 50
            "async_workers" = $WorkerThreads
        }
        "threading_config" = @{
            "OMP_NUM_THREADS" = $AIThreads
            "NUMBA_NUM_THREADS" = $AIThreads
            "MKL_NUM_THREADS" = $AIThreads
            "OPENBLAS_NUM_THREADS" = $AIThreads
            "VECLIB_MAXIMUM_THREADS" = $AIThreads
        }
    } | ConvertTo-Json -Depth 3
    
    Write-Host "📊 Optimal AI Swarm Configuration:" -ForegroundColor Green
    Write-Host "  AI Processing Threads: $AIThreads" -ForegroundColor White
    Write-Host "  Worker Threads: $WorkerThreads" -ForegroundColor White
    Write-Host "  I/O Threads: $IOThreads" -ForegroundColor White
    Write-Host "  Batch Size: 32" -ForegroundColor White
    Write-Host "  Queue Size: 1000" -ForegroundColor White
    
    Write-Host "`n📝 Creating AI configuration file..." -ForegroundColor Green
    $AIConfig | Out-File -FilePath "./ai-swarm-cpu-config.json" -Encoding UTF8
    
    # Create environment variables file
    $EnvVars = @"
# AI Swarm CPU Optimization Environment Variables
# Intel i9-13900K Optimized Settings

# Threading Configuration
OMP_NUM_THREADS=$AIThreads
NUMBA_NUM_THREADS=$AIThreads
MKL_NUM_THREADS=$AIThreads
OPENBLAS_NUM_THREADS=$AIThreads
VECLIB_MAXIMUM_THREADS=$AIThreads

# Performance Settings
AI_WORKER_THREADS=$WorkerThreads
AI_IO_THREADS=$IOThreads
AI_BATCH_SIZE=32
AI_QUEUE_SIZE=1000
AI_CONNECTION_POOL_SIZE=50

# CPU Affinity (enable NUMA awareness)
NUMA_ENABLED=true
CPU_AFFINITY_ENABLED=true

# Memory Settings
AI_MEMORY_LIMIT=8G
REDIS_MEMORY_LIMIT=2G

# Python Performance
PYTHONHASHSEED=0
PYTHONUNBUFFERED=1
PYTHONASYNCIODEBUG=0
"@

    Write-Host "📝 Creating environment variables file..." -ForegroundColor Green
    $EnvVars | Out-File -FilePath "./.env.cpu-optimized" -Encoding UTF8
    
    Write-Host "✅ Created: ai-swarm-cpu-config.json" -ForegroundColor Green
    Write-Host "✅ Created: .env.cpu-optimized" -ForegroundColor Green
}

# CPU Monitoring
function Start-CPUMonitoring {
    Write-Host "`n📊 Setting up CPU Monitoring..." -ForegroundColor Yellow
    
    $MonitoringScript = @"
# Real-time CPU Monitoring for AI Swarm
# Updates every 5 seconds

Write-Host "🖥️ CPU Monitoring Started - Press Ctrl+C to stop" -ForegroundColor Cyan

while (`$true) {
    Clear-Host
    Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "     AI SWARM CPU MONITOR" -ForegroundColor Cyan
    Write-Host "     Intel i9-13900K (32 Cores)" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "Time: `$(Get-Date -Format 'HH:mm:ss')" -ForegroundColor White
    Write-Host ""
    
    # Overall CPU usage
    `$cpu = Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 1 -MaxSamples 1
    `$cpuPercent = [math]::Round(100 - `$cpu.CounterSamples.CookedValue, 2)
    
    Write-Host "Overall CPU Usage: `$cpuPercent%" -ForegroundColor Green
    
    # Top processes
    Write-Host "`nTop CPU Consumers:" -ForegroundColor Yellow
    Get-Process | Sort-Object CPU -Descending | Select-Object -First 8 Name, CPU, WorkingSet | Format-Table -AutoSize
    
    # Docker containers
    Write-Host "Docker Container Stats:" -ForegroundColor Yellow
    try {
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    } catch {
        Write-Host "Docker not running or accessible" -ForegroundColor Red
    }
    
    # Memory usage
    `$mem = Get-Counter '\Memory\Available MBytes' -SampleInterval 1 -MaxSamples 1
    `$availableMem = `$mem.CounterSamples.CookedValue
    `$totalMem = (Get-ComputerInfo).TotalPhysicalMemory / 1MB
    `$usedMemPercent = [math]::Round(((`$totalMem - `$availableMem) / `$totalMem) * 100, 2)
    
    Write-Host "`nMemory Usage: `$usedMemPercent%" -ForegroundColor Green
    Write-Host "Available: `$([math]::Round(`$availableMem / 1024, 2)) GB / `$([math]::Round(`$totalMem / 1024, 2)) GB" -ForegroundColor White
    
    Write-Host "`nPress Ctrl+C to stop monitoring..." -ForegroundColor DarkGray
    Start-Sleep -Seconds 5
}
"@

    Write-Host "📝 Creating CPU monitoring script..." -ForegroundColor Green
    $MonitoringScript | Out-File -FilePath "./cpu-monitor.ps1" -Encoding UTF8
    
    Write-Host "✅ Created: cpu-monitor.ps1" -ForegroundColor Green
    Write-Host "ℹ️ To start monitoring: PowerShell -File .\cpu-monitor.ps1" -ForegroundColor Cyan
}

# Performance Analysis
function Analyze-Performance {
    Write-Host "`n🔍 Performance Analysis..." -ForegroundColor Yellow
    
    # Current CPU usage
    $cpuCounter = Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 2 -MaxSamples 3
    $avgCPU = ($cpuCounter.CounterSamples | Measure-Object CookedValue -Average).Average
    $cpuUsage = [math]::Round(100 - $avgCPU, 2)
    
    # Memory analysis
    $memory = Get-ComputerInfo
    $totalRAM = [math]::Round($memory.TotalPhysicalMemory / 1GB, 2)
    $availableRAM = [math]::Round($memory.AvailablePhysicalMemory / 1GB, 2)
    $usedRAM = $totalRAM - $availableRAM
    $memUsage = [math]::Round(($usedRAM / $totalRAM) * 100, 2)
    
    Write-Host "📈 Current Performance Metrics:" -ForegroundColor Green
    Write-Host "  CPU Usage: $cpuUsage%" -ForegroundColor White
    Write-Host "  Memory Usage: $memUsage% ($usedRAM GB / $totalRAM GB)" -ForegroundColor White
    
    # Docker stats if available
    try {
        Write-Host "`n🐳 Docker Container Performance:" -ForegroundColor Green
        docker stats --no-stream
    } catch {
        Write-Host "  Docker containers not running" -ForegroundColor Yellow
    }
    
    # Performance recommendations
    Write-Host "`n💡 Performance Recommendations:" -ForegroundColor Cyan
    
    if ($cpuUsage -lt 20) {
        Write-Host "  ✅ CPU usage is optimal" -ForegroundColor Green
        Write-Host "  💡 Consider increasing AI worker threads for better utilization" -ForegroundColor Yellow
    } elseif ($cpuUsage -lt 60) {
        Write-Host "  ✅ CPU usage is good" -ForegroundColor Green
    } elseif ($cpuUsage -lt 80) {
        Write-Host "  ⚠️ CPU usage is high - consider optimization" -ForegroundColor Yellow
    } else {
        Write-Host "  🔴 CPU usage is very high - immediate optimization needed" -ForegroundColor Red
    }
    
    if ($memUsage -lt 70) {
        Write-Host "  ✅ Memory usage is good" -ForegroundColor Green
    } elseif ($memUsage -lt 85) {
        Write-Host "  ⚠️ Memory usage is high - monitor closely" -ForegroundColor Yellow
    } else {
        Write-Host "  🔴 Memory usage is critical - optimization required" -ForegroundColor Red
    }
}

# Main execution logic
$LogicalProcessors = Get-SystemInfo

if ($Analyze -or $Full) {
    Analyze-Performance
}

if ($Docker -or $Full) {
    Optimize-DockerCPU -LogicalProcessors $LogicalProcessors
}

if ($Windows -or $Full) {
    Optimize-WindowsCPU
}

if ($Full) {
    Optimize-AISwarm -LogicalProcessors $LogicalProcessors
    Start-CPUMonitoring
}

if (-not ($Full -or $Docker -or $Windows -or $Monitor -or $Analyze)) {
    Write-Host "`n📖 Usage Options:" -ForegroundColor Cyan
    Write-Host "  -Full      : Complete CPU optimization suite" -ForegroundColor White
    Write-Host "  -Docker    : Optimize Docker CPU allocation" -ForegroundColor White
    Write-Host "  -Windows   : Optimize Windows CPU settings" -ForegroundColor White
    Write-Host "  -Monitor   : Set up CPU monitoring" -ForegroundColor White
    Write-Host "  -Analyze   : Analyze current performance" -ForegroundColor White
    Write-Host "`nExample:" -ForegroundColor Green
    Write-Host "  .\cpu-optimizer.ps1 -Full" -ForegroundColor White
}

Write-Host "`n🎯 CPU Optimization Complete!" -ForegroundColor Green
Write-Host "Your Intel i9-13900K is ready for maximum AI Swarm performance!" -ForegroundColor Cyan