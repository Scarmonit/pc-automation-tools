# AI Agents Installation Script for Windows
Write-Host "Installing AI Agents and Tools..." -ForegroundColor Green

# Install Python packages
Write-Host "Installing Python-based agents..." -ForegroundColor Yellow

pip install --user pyautogen autogen-agentchat aider-chat

# Create AutoGen configuration
Write-Host "Configuring AutoGen..." -ForegroundColor Cyan
$autogenConfig = @"
{
  "model_list": [
    {
      "model": "llama3.2",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "api_type": "openai"
    },
    {
      "model": "mistral",
      "base_url": "http://localhost:11434/v1", 
      "api_key": "ollama",
      "api_type": "openai"
    },
    {
      "model": "codellama",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "api_type": "openai"
    }
  ]
}
"@

$autogenPath = "$env:USERPROFILE\.autogen"
New-Item -Path $autogenPath -ItemType Directory -Force | Out-Null
$autogenConfig | Out-File -FilePath "$autogenPath\config.json" -Encoding UTF8

# Configure Aider
Write-Host "Configuring Aider..." -ForegroundColor Cyan
$aiderConfig = @"
model: ollama/codellama:7b
openai-api-base: http://localhost:11434/v1
openai-api-key: ollama
auto-commits: false
stream: true
"@

$aiderConfig | Out-File -FilePath "$env:USERPROFILE\.aider.conf.yml" -Encoding UTF8

# Deploy Flowise with Docker
Write-Host "Deploying Flowise..." -ForegroundColor Yellow
docker run -d `
  --name flowise `
  -p 3001:3000 `
  -v ${env:USERPROFILE}\.flowise:/root/.flowise `
  --restart unless-stopped `
  flowiseai/flowise

# Deploy OpenHands
Write-Host "Deploying OpenHands..." -ForegroundColor Yellow
docker run -d `
  --name openhands `
  -p 3002:3000 `
  -v //var/run/docker.sock:/var/run/docker.sock `
  -v ${env:USERPROFILE}\.openhands:/app/workspace `
  --restart unless-stopped `
  ghcr.io/all-hands-ai/openhands:latest

# Install Continue for VS Code if available
if (Get-Command code -ErrorAction SilentlyContinue) {
    Write-Host "Installing Continue extension for VS Code..." -ForegroundColor Cyan
    code --install-extension continue.continue
    
    # Configure Continue
    $continueConfig = @"
{
  "models": [
    {
      "title": "Ollama - Llama 3.2",
      "provider": "ollama",
      "model": "llama3.2:3b",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Ollama - CodeLlama",
      "provider": "ollama",
      "model": "codellama:7b",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Ollama - Mistral",
      "provider": "ollama",
      "model": "mistral:7b-instruct",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "CodeLlama",
    "provider": "ollama",
    "model": "codellama:7b",
    "apiBase": "http://localhost:11434"
  }
}
"@
    
    $continuePath = "$env:USERPROFILE\.continue"
    New-Item -Path $continuePath -ItemType Directory -Force | Out-Null
    $continueConfig | Out-File -FilePath "$continuePath\config.json" -Encoding UTF8
    Write-Host "✓ Continue extension configured" -ForegroundColor Green
}

Write-Host "`nAI Agents installation complete!" -ForegroundColor Green
Write-Host "Services available at:" -ForegroundColor Cyan
Write-Host "  Flowise: http://localhost:3001" -ForegroundColor White
Write-Host "  OpenHands: http://localhost:3002" -ForegroundColor White