# Install Ollama on Windows
# PowerShell script for installing and configuring Ollama with local models

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Installing Ollama for Windows" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Set installation directory
$ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama"

# Check if Ollama is already installed
Write-Host "Checking for existing Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>$null
    if ($ollamaVersion) {
        Write-Host "Ollama already installed: $ollamaVersion" -ForegroundColor Green
        $install = Read-Host "Reinstall? (y/n)"
        if ($install -ne 'y') {
            Write-Host "Skipping installation" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "Ollama not found, proceeding with installation" -ForegroundColor Yellow
}

# Download Ollama installer
Write-Host "Downloading Ollama installer..." -ForegroundColor Yellow
$installerUrl = "https://ollama.com/download/OllamaSetup.exe"
$installerPath = "$env:TEMP\OllamaSetup.exe"

try {
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "Download complete" -ForegroundColor Green
} catch {
    Write-Host "Download failed: $_" -ForegroundColor Red
    exit 1
}

# Install Ollama
Write-Host "Installing Ollama..." -ForegroundColor Yellow
try {
    Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait
    Write-Host "Installation complete" -ForegroundColor Green
} catch {
    Write-Host "Installation failed: $_" -ForegroundColor Red
    exit 1
}

# Add to PATH if needed
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$ollamaPath*") {
    Write-Host "Adding Ollama to PATH..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$ollamaPath", "User")
    $env:Path = "$env:Path;$ollamaPath"
}

# Start Ollama service
Write-Host "Starting Ollama service..." -ForegroundColor Yellow
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

# Wait for service to start
Start-Sleep -Seconds 5

# Download essential models
Write-Host ""
Write-Host "Downloading essential models..." -ForegroundColor Cyan
Write-Host "This may take some time depending on your internet connection" -ForegroundColor Yellow
Write-Host ""

$models = @(
    @{Name = "llama3.2:3b"; Size = "2GB"; Description = "Fast general purpose"},
    @{Name = "mistral:7b-instruct"; Size = "4GB"; Description = "Excellent reasoning"},
    @{Name = "codellama:7b"; Size = "4GB"; Description = "Code generation"},
    @{Name = "qwen2.5:3b"; Size = "2GB"; Description = "Multilingual support"},
    @{Name = "starcoder2:3b"; Size = "2GB"; Description = "Code completion"}
)

foreach ($model in $models) {
    Write-Host "Downloading $($model.Name) ($($model.Size) - $($model.Description))..." -ForegroundColor Yellow
    try {
        $output = & ollama pull $model.Name 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [SUCCESS] $($model.Name) downloaded" -ForegroundColor Green
        } else {
            Write-Host "  [WARNING] Failed to download $($model.Name): $output" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  [ERROR] Failed to download $($model.Name): $_" -ForegroundColor Red
    }
}

# Verify models
Write-Host ""
Write-Host "Verifying installed models..." -ForegroundColor Yellow
$installedModels = & ollama list 2>$null
if ($installedModels) {
    Write-Host "Installed models:" -ForegroundColor Green
    Write-Host $installedModels
} else {
    Write-Host "No models found" -ForegroundColor Red
}

# Test inference
Write-Host ""
Write-Host "Testing model inference..." -ForegroundColor Yellow
try {
    $response = & ollama run llama3.2:3b "Say hello in one word" --verbose 2>$null
    if ($response) {
        Write-Host "Model test successful: $response" -ForegroundColor Green
    }
} catch {
    Write-Host "Model test failed" -ForegroundColor Red
}

# Create Ollama configuration
Write-Host ""
Write-Host "Creating Ollama configuration..." -ForegroundColor Yellow
$configPath = "$env:USERPROFILE\.ollama"
if (!(Test-Path $configPath)) {
    New-Item -Path $configPath -ItemType Directory -Force | Out-Null
}

$config = @{
    host = "0.0.0.0:11434"
    models_path = "$env:USERPROFILE\.ollama\models"
    gpu_layers = 35
    num_threads = 8
    context_size = 4096
} | ConvertTo-Json

Set-Content -Path "$configPath\config.json" -Value $config
Write-Host "Configuration saved to $configPath\config.json" -ForegroundColor Green

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Ollama Installation Complete!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ollama API: http://localhost:11434" -ForegroundColor Cyan
Write-Host "OpenAI-compatible endpoint: http://localhost:11434/v1" -ForegroundColor Cyan
Write-Host ""
Write-Host "To test: ollama run llama3.2:3b" -ForegroundColor Yellow