# LLMStack Complete Deployment Script for Windows
# Main orchestrator for setting up the entire free AI stack

param(
    [string]$Phase = "all",
    [switch]$SkipModels = $false,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

Write-Host @"
===========================================================
     LLMStack Free AI Stack Deployment for Windows
===========================================================
     Zero API Costs | 100% Local | Production Ready
===========================================================
"@ -ForegroundColor Cyan

# Set deployment directory
$LLMSTACK_HOME = "$PSScriptRoot"
Set-Location $LLMSTACK_HOME

# Function to run phases
function Run-Phase {
    param([string]$PhaseName, [scriptblock]$PhaseScript)
    
    Write-Host ""
    Write-Host "[$PhaseName]" -ForegroundColor Cyan
    Write-Host ("-" * 50) -ForegroundColor Gray
    
    try {
        & $PhaseScript
        Write-Host "[SUCCESS] $PhaseName completed" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] $PhaseName failed: $_" -ForegroundColor Red
        if ($Phase -eq "all") {
            $continue = Read-Host "Continue with next phase? (y/n)"
            if ($continue -ne 'y') {
                exit 1
            }
        } else {
            exit 1
        }
    }
}

# PHASE 0: System Check
if ($Phase -eq "all" -or $Phase -eq "check") {
    Run-Phase "System Requirements Check" {
        & "$PSScriptRoot\deployment\windows\check_system.ps1"
    }
}

# PHASE 1: Install Ollama and Models
if ($Phase -eq "all" -or $Phase -eq "ollama") {
    Run-Phase "Install Ollama & Models" {
        if (-not $SkipModels) {
            & "$PSScriptRoot\deployment\windows\install_ollama.ps1"
        } else {
            Write-Host "Skipping model downloads" -ForegroundColor Yellow
        }
    }
}

# PHASE 2: Set up Docker Environment
if ($Phase -eq "all" -or $Phase -eq "docker") {
    Run-Phase "Docker Environment Setup" {
        Write-Host "Creating Docker configurations..." -ForegroundColor Yellow
        
        # Create docker-compose for LLMStack
        $dockerCompose = @"
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: llmstack-postgres
    environment:
      POSTGRES_DB: llmstack
      POSTGRES_USER: llmstack
      POSTGRES_PASSWORD: ${env:POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U llmstack"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: llmstack-redis
    command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  chroma:
    image: chromadb/chroma:latest
    container_name: llmstack-chroma
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      IS_PERSISTENT: TRUE
      ANONYMIZED_TELEMETRY: FALSE

  flowise:
    image: flowiseai/flowise:latest
    container_name: llmstack-flowise
    ports:
      - "3001:3000"
    volumes:
      - flowise_data:/root/.flowise
    environment:
      FLOWISE_USERNAME: admin
      FLOWISE_PASSWORD: ${env:FLOWISE_PASSWORD}

  monitoring:
    image: grafana/grafana:latest
    container_name: llmstack-monitoring
    ports:
      - "3003:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${env:GRAFANA_PASSWORD}
      GF_INSTALL_PLUGINS: redis-datasource
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  chroma_data:
  flowise_data:
  grafana_data:

networks:
  default:
    name: llmstack-network
"@

        # Generate secure passwords
        $env:POSTGRES_PASSWORD = [System.Web.Security.Membership]::GeneratePassword(24, 4)
        $env:FLOWISE_PASSWORD = [System.Web.Security.Membership]::GeneratePassword(16, 2)
        $env:GRAFANA_PASSWORD = [System.Web.Security.Membership]::GeneratePassword(16, 2)
        
        # Save docker-compose
        Set-Content -Path "$PSScriptRoot\docker-compose.yml" -Value $dockerCompose
        
        # Save credentials
        @"
POSTGRES_PASSWORD=$($env:POSTGRES_PASSWORD)
FLOWISE_PASSWORD=$($env:FLOWISE_PASSWORD)
GRAFANA_PASSWORD=$($env:GRAFANA_PASSWORD)
OLLAMA_API_BASE=http://host.docker.internal:11434/v1
"@ | Set-Content -Path "$PSScriptRoot\.env"
        
        Write-Host "Starting Docker services..." -ForegroundColor Yellow
        docker-compose up -d
        
        Write-Host "Waiting for services to start (30 seconds)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    }
}

# PHASE 3: Install Python Dependencies
if ($Phase -eq "all" -or $Phase -eq "python") {
    Run-Phase "Python Environment Setup" {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
        
        Write-Host "Activating virtual environment..." -ForegroundColor Yellow
        & ".\venv\Scripts\Activate.ps1"
        
        Write-Host "Installing Python packages..." -ForegroundColor Yellow
        pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyautogen autogen-agentchat aider-chat httpx
    }
}

# PHASE 4: Configure AI Agents
if ($Phase -eq "all" -or $Phase -eq "agents") {
    Run-Phase "Configure AI Agents" {
        & "$PSScriptRoot\deployment\windows\setup_agents.ps1"
    }
}

# PHASE 5: Validation
if ($Phase -eq "all" -or $Phase -eq "validate") {
    Run-Phase "System Validation" {
        & "$PSScriptRoot\deployment\windows\validate.ps1"
    }
}

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Yellow
Write-Host "  Main Application: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Flowise UI: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  Monitoring: http://localhost:3003" -ForegroundColor Cyan
Write-Host "  Vector DB: http://localhost:8001" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Yellow
Write-Host "  Ollama: http://localhost:11434/v1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Credentials saved in: .env" -ForegroundColor Yellow
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "  .\run.py" -ForegroundColor Green