# Description: Validate system configuration and health

# Validation Script for LLMStack Deployment
$ErrorActionPreference = 'Stop'

Write-Host "=== LLMStack Free Agent Validation ===" -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0

function Test-Service {
    param(
        [string]$Name,
        [string]$Url
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ $Name is running" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "✗ $Name is not accessible" -ForegroundColor Red
        $script:errors++
        return $false
    }
}

# Test core services
Write-Host "Checking core services..." -ForegroundColor Yellow
Test-Service -Name "Ollama" -Url "http://localhost:11434/api/tags"
Test-Service -Name "LM Studio" -Url "http://localhost:1234/v1/models"
Test-Service -Name "LLMStack" -Url "http://localhost:3000/api/health"
Test-Service -Name "Flowise" -Url "http://localhost:3001"
Test-Service -Name "OpenHands" -Url "http://localhost:3002/health"
Test-Service -Name "Grafana" -Url "http://localhost:3003"

# Test model inference
Write-Host "`nTesting model inference..." -ForegroundColor Yellow
try {
    $headers = @{
        "Content-Type" = "application/json"
    }
    $body = @{
        model = "llama3.2:3b"
        messages = @(
            @{
                role = "user"
                content = "Say hello"
            }
        )
        max_tokens = 10
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:11434/v1/chat/completions" `
                                 -Method Post `
                                 -Headers $headers `
                                 -Body $body `
                                 -ErrorAction Stop
    
    if ($response.choices[0].message.content) {
        Write-Host "✓ Model inference working: $($response.choices[0].message.content)" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Model inference failed" -ForegroundColor Red
    $errors++
}

# Check Docker containers
Write-Host "`nChecking Docker containers..." -ForegroundColor Yellow
$containers = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-Object -Skip 1
Write-Host $containers

# Summary
Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "Errors: $errors" -ForegroundColor $(if ($errors -eq 0) {"Green"} else {"Red"})
Write-Host "Warnings: $warnings" -ForegroundColor $(if ($warnings -eq 0) {"Green"} else {"Yellow"})

if ($errors -eq 0) {
    Write-Host "`n✓ All systems operational!" -ForegroundColor Green
    Write-Host "`nAccess points:" -ForegroundColor Cyan
    Write-Host "  LLMStack UI: http://localhost:3000" -ForegroundColor White
    Write-Host "  Flowise: http://localhost:3001" -ForegroundColor White
    Write-Host "  OpenHands: http://localhost:3002" -ForegroundColor White
    Write-Host "  Monitoring: http://localhost:3003 (admin/admin)" -ForegroundColor White
    Write-Host "`nAPI Endpoints:" -ForegroundColor Cyan
    Write-Host "  Ollama: http://localhost:11434/v1" -ForegroundColor White
    Write-Host "  LM Studio: http://localhost:1234/v1" -ForegroundColor White
} else {
    Write-Host "`n✗ Validation failed with $errors errors" -ForegroundColor Red
    Write-Host "Please check the logs and troubleshoot failed services" -ForegroundColor Yellow
}