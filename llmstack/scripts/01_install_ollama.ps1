# Ollama Installation Script for Windows
Write-Host "Installing Ollama for Windows..." -ForegroundColor Green

# Download Ollama installer
$ollamaUrl = "https://ollama.com/download/OllamaSetup.exe"
$installerPath = "$env:TEMP\OllamaSetup.exe"

Write-Host "Downloading Ollama installer..."
Invoke-WebRequest -Uri $ollamaUrl -OutFile $installerPath

# Install Ollama silently
Write-Host "Installing Ollama..."
Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait

# Add Ollama to PATH if not already there
$ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama"
if ($env:PATH -notlike "*$ollamaPath*") {
    [Environment]::SetEnvironmentVariable("PATH", "$env:PATH;$ollamaPath", [EnvironmentVariableTarget]::User)
    $env:PATH = "$env:PATH;$ollamaPath"
}

Write-Host "Ollama installed successfully!" -ForegroundColor Green

# Start Ollama service
Write-Host "Starting Ollama service..."
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden

Start-Sleep -Seconds 5

# Pull essential models
Write-Host "Downloading essential models..." -ForegroundColor Yellow
Write-Host "This may take some time depending on your internet speed..."

$models = @(
    "llama3.2:3b",        # 2GB - Fast general purpose
    "mistral:7b-instruct", # 4GB - Excellent reasoning
    "codellama:7b",       # 4GB - Code generation
    "qwen2.5:3b"          # 2GB - Multilingual support
)

foreach ($model in $models) {
    Write-Host "Pulling model: $model" -ForegroundColor Cyan
    & ollama pull $model
}

# Verify installation
Write-Host "`nVerifying Ollama installation..." -ForegroundColor Green
& ollama list

Write-Host "`nOllama setup complete!" -ForegroundColor Green
Write-Host "Ollama API available at: http://localhost:11434" -ForegroundColor Cyan