# LLMStack Deployment Script for Windows
Write-Host "Deploying LLMStack with Docker..." -ForegroundColor Green

$LLMSTACK_HOME = "C:\Users\scarm\llmstack"
Set-Location $LLMSTACK_HOME

# Clone LLMStack repository
if (-not (Test-Path "LLMStack")) {
    Write-Host "Cloning LLMStack repository..."
    git clone https://github.com/trypromptly/LLMStack.git
}

Set-Location "LLMStack"

# Create production configuration
Write-Host "Creating production configuration..."

$envContent = @"
# Security
SECRET_KEY=$(openssl rand -base64 32)
CIPHER_SALT=$(openssl rand -base64 16)
DATABASE_PASSWORD=$(openssl rand -base64 24)

# Paths
POSTGRES_VOLUME=./data/postgres
REDIS_VOLUME=./data/redis
WEAVIATE_VOLUME=./data/weaviate

# Model endpoints (all local)
OPENAI_API_BASE=http://host.docker.internal:11434/v1
OPENAI_API_KEY=ollama

# Features
ENABLE_SIGNUP=false
ENABLE_ANALYTICS=false
DEFAULT_VECTOR_DB=chroma
"@

# Generate secure keys using PowerShell
$secretKey = [Convert]::ToBase64String((1..32 | ForEach-Object {Get-Random -Maximum 256}))
$cipherSalt = [Convert]::ToBase64String((1..16 | ForEach-Object {Get-Random -Maximum 256}))
$dbPassword = [Convert]::ToBase64String((1..24 | ForEach-Object {Get-Random -Maximum 256}))

$envContent = $envContent -replace '\$\(openssl rand -base64 32\)', $secretKey
$envContent = $envContent -replace '\$\(openssl rand -base64 16\)', $cipherSalt
$envContent = $envContent -replace '\$\(openssl rand -base64 24\)', $dbPassword

New-Item -Path "docker" -ItemType Directory -Force | Out-Null
$envContent | Out-File -FilePath "docker\.env.production" -Encoding UTF8

# Create docker-compose override for Windows
$dockerComposeOverride = @"
version: '3.8'
services:
  api:
    environment:
      - OPENAI_API_BASE=http://host.docker.internal:11434/v1
    extra_hosts:
      - "host.docker.internal:host-gateway"
  
  worker:
    extra_hosts:
      - "host.docker.internal:host-gateway"
"@

$dockerComposeOverride | Out-File -FilePath "docker\docker-compose.override.yml" -Encoding UTF8

Write-Host "Starting LLMStack with Docker Compose..." -ForegroundColor Yellow
Set-Location docker
docker compose --env-file .env.production up -d

Write-Host "`nWaiting for services to start (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check health
$health = Invoke-RestMethod -Uri "http://localhost:3000/api/health" -Method Get -ErrorAction SilentlyContinue
if ($health) {
    Write-Host "✓ LLMStack is running!" -ForegroundColor Green
    Write-Host "Access LLMStack at: http://localhost:3000" -ForegroundColor Cyan
} else {
    Write-Host "⚠ LLMStack may still be starting. Check logs with: docker compose logs" -ForegroundColor Yellow
}