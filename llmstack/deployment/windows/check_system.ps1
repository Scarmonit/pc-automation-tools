# LLMStack Windows System Requirements Check
# PowerShell script for checking system compatibility

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "LLMStack System Requirements Check" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

$requirements = @{
    CPUCores = 4
    RAMGb = 8
    DiskGb = 50
}

$passed = $true

# Check CPU cores
$cpuCores = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
Write-Host "CPU Cores: $cpuCores" -NoNewline
if ($cpuCores -ge $requirements.CPUCores) {
    Write-Host " [PASS]" -ForegroundColor Green
} else {
    Write-Host " [FAIL] Need $($requirements.CPUCores)+ cores" -ForegroundColor Red
    $passed = $false
}

# Check RAM
$ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
Write-Host "RAM: ${ram}GB" -NoNewline
if ($ram -ge $requirements.RAMGb) {
    Write-Host " [PASS]" -ForegroundColor Green
} else {
    Write-Host " [FAIL] Need $($requirements.RAMGb)GB+ RAM" -ForegroundColor Red
    $passed = $false
}

# Check GPU (optional)
try {
    $gpu = Get-CimInstance Win32_VideoController | Where-Object {$_.Name -like "*NVIDIA*"}
    if ($gpu) {
        $vram = [math]::Round($gpu.AdapterRAM / 1GB, 2)
        Write-Host "GPU: $($gpu.Name) with ${vram}GB VRAM" -ForegroundColor Yellow
        Write-Host "  [INFO] GPU detected - will enable GPU acceleration" -ForegroundColor Cyan
    } else {
        Write-Host "GPU: No NVIDIA GPU detected" -ForegroundColor Yellow
        Write-Host "  [INFO] Will use CPU inference" -ForegroundColor Cyan
    }
} catch {
    Write-Host "GPU: Detection failed - will use CPU" -ForegroundColor Yellow
}

# Check disk space
$disk = Get-PSDrive C | Select-Object @{Name="FreeGB";Expression={[math]::Round($_.Free / 1GB, 2)}}
Write-Host "Free Disk Space: $($disk.FreeGB)GB" -NoNewline
if ($disk.FreeGB -ge $requirements.DiskGb) {
    Write-Host " [PASS]" -ForegroundColor Green
} else {
    Write-Host " [FAIL] Need $($requirements.DiskGb)GB+ free space" -ForegroundColor Red
    $passed = $false
}

# Check Docker
Write-Host "Docker Desktop: " -NoNewline
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "$dockerVersion [PASS]" -ForegroundColor Green
    } else {
        Write-Host "Not found [FAIL]" -ForegroundColor Red
        Write-Host "  Install from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
        $passed = $false
    }
} catch {
    Write-Host "Not installed [FAIL]" -ForegroundColor Red
    Write-Host "  Install from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    $passed = $false
}

# Check Python
Write-Host "Python: " -NoNewline
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "$pythonVersion [PASS]" -ForegroundColor Green
    } else {
        Write-Host "Not found [FAIL]" -ForegroundColor Red
        Write-Host "  Install from: https://www.python.org/downloads/" -ForegroundColor Yellow
        $passed = $false
    }
} catch {
    Write-Host "Not installed [FAIL]" -ForegroundColor Red
    Write-Host "  Install from: https://www.python.org/downloads/" -ForegroundColor Yellow
    $passed = $false
}

# Check Git
Write-Host "Git: " -NoNewline
try {
    $gitVersion = git --version 2>$null
    if ($gitVersion) {
        Write-Host "$gitVersion [PASS]" -ForegroundColor Green
    } else {
        Write-Host "Not found [FAIL]" -ForegroundColor Red
        $passed = $false
    }
} catch {
    Write-Host "Not installed [FAIL]" -ForegroundColor Red
    $passed = $false
}

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
if ($passed) {
    Write-Host "System Check: PASSED" -ForegroundColor Green
    Write-Host "Ready to install LLMStack!" -ForegroundColor Green
} else {
    Write-Host "System Check: FAILED" -ForegroundColor Red
    Write-Host "Please install missing requirements" -ForegroundColor Yellow
    exit 1
}