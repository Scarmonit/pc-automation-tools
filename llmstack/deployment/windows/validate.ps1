# Validation Script for LLMStack Deployment
# Comprehensive health check and testing

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "LLMStack Deployment Validation" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0
$successes = 0

function Test-Service {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [string]$Body = $null
    )
    
    Write-Host "Testing $Name... " -NoNewline
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            TimeoutSec = 10
        }
        
        if ($Body) {
            $params.Body = $Body
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-RestMethod @params -ErrorAction Stop
        Write-Host "[PASS]" -ForegroundColor Green
        $script:successes++
        return $true
    } catch {
        if ($_.Exception.Response.StatusCode -eq 401) {
            Write-Host "[PASS - Auth Required]" -ForegroundColor Yellow
            $script:warnings++
            return $true
        } else {
            Write-Host "[FAIL] $_" -ForegroundColor Red
            $script:errors++
            return $false
        }
    }
}

function Test-ModelInference {
    Write-Host ""
    Write-Host "Testing Model Inference..." -ForegroundColor Cyan
    
    $body = @{
        model = "llama3.2:3b"
        messages = @(
            @{
                role = "user"
                content = "Say hello in exactly 3 words"
            }
        )
        max_tokens = 10
        temperature = 0
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod `
            -Uri "http://localhost:11434/v1/chat/completions" `
            -Method POST `
            -Body $body `
            -ContentType "application/json" `
            -TimeoutSec 30
        
        if ($response.choices[0].message.content) {
            Write-Host "  Response: $($response.choices[0].message.content)" -ForegroundColor Green
            Write-Host "  [PASS] Model inference working" -ForegroundColor Green
            $script:successes++
        } else {
            Write-Host "  [FAIL] No response content" -ForegroundColor Red
            $script:errors++
        }
    } catch {
        Write-Host "  [FAIL] Inference error: $_" -ForegroundColor Red
        $script:errors++
    }
}

function Test-DockerContainers {
    Write-Host ""
    Write-Host "Checking Docker Containers..." -ForegroundColor Cyan
    
    try {
        $containers = docker ps --format "table {{.Names}}\t{{.Status}}" 2>$null
        if ($containers) {
            Write-Host $containers -ForegroundColor Gray
            
            $requiredContainers = @(
                "llmstack-postgres",
                "llmstack-redis",
                "llmstack-chroma",
                "llmstack-flowise"
            )
            
            foreach ($container in $requiredContainers) {
                if ($containers -like "*$container*") {
                    Write-Host "  [OK] $container is running" -ForegroundColor Green
                    $script:successes++
                } else {
                    Write-Host "  [WARNING] $container not found" -ForegroundColor Yellow
                    $script:warnings++
                }
            }
        } else {
            Write-Host "  [ERROR] No Docker containers running" -ForegroundColor Red
            $script:errors++
        }
    } catch {
        Write-Host "  [ERROR] Docker not accessible: $_" -ForegroundColor Red
        $script:errors++
    }
}

function Test-PythonEnvironment {
    Write-Host ""
    Write-Host "Checking Python Environment..." -ForegroundColor Cyan
    
    # Check if venv exists
    if (Test-Path "$PSScriptRoot\..\..\venv") {
        Write-Host "  [OK] Virtual environment exists" -ForegroundColor Green
        $script:successes++
        
        # Check key packages
        $packages = @("autogen", "aider-chat", "httpx", "fastapi")
        
        foreach ($package in $packages) {
            try {
                $result = & "$PSScriptRoot\..\..\venv\Scripts\python.exe" -c "import $package; print('$package OK')" 2>$null
                if ($result -like "*OK*") {
                    Write-Host "  [OK] $package installed" -ForegroundColor Green
                    $script:successes++
                } else {
                    Write-Host "  [WARNING] $package not found" -ForegroundColor Yellow
                    $script:warnings++
                }
            } catch {
                Write-Host "  [WARNING] Could not check $package" -ForegroundColor Yellow
                $script:warnings++
            }
        }
    } else {
        Write-Host "  [WARNING] Virtual environment not found" -ForegroundColor Yellow
        $script:warnings++
    }
}

function Show-Summary {
    Write-Host ""
    Write-Host "===========================================" -ForegroundColor Cyan
    Write-Host "Validation Summary" -ForegroundColor Cyan
    Write-Host "===========================================" -ForegroundColor Cyan
    
    Write-Host "Successes: $successes" -ForegroundColor Green
    Write-Host "Warnings: $warnings" -ForegroundColor Yellow
    Write-Host "Errors: $errors" -ForegroundColor Red
    
    Write-Host ""
    if ($errors -eq 0) {
        Write-Host "VALIDATION PASSED!" -ForegroundColor Green -BackgroundColor DarkGreen
        Write-Host ""
        Write-Host "Your LLMStack deployment is ready!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Quick Start Commands:" -ForegroundColor Cyan
        Write-Host "  Run main app: python main.py list" -ForegroundColor Yellow
        Write-Host "  Test Ollama: ollama run llama3.2:3b" -ForegroundColor Yellow
        Write-Host "  View Flowise: Start-Process http://localhost:3001" -ForegroundColor Yellow
        Write-Host "  View Monitoring: Start-Process http://localhost:3003" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "API Endpoints:" -ForegroundColor Cyan
        Write-Host "  Ollama API: http://localhost:11434/v1" -ForegroundColor Yellow
        Write-Host "  Chroma Vector DB: http://localhost:8001" -ForegroundColor Yellow
        Write-Host ""
        return 0
    } else {
        Write-Host "VALIDATION FAILED!" -ForegroundColor Red -BackgroundColor DarkRed
        Write-Host ""
        Write-Host "Please fix the errors above and run validation again:" -ForegroundColor Yellow
        Write-Host "  .\deployment\windows\validate.ps1" -ForegroundColor Green
        return 1
    }
}

# Run all tests
Write-Host "Running Service Tests..." -ForegroundColor Cyan
Write-Host ""

# Core services
Test-Service -Name "Ollama API" -Url "http://localhost:11434/api/tags"
Test-Service -Name "Ollama OpenAI API" -Url "http://localhost:11434/v1/models"
Test-Service -Name "Chroma Vector DB" -Url "http://localhost:8001/api/v1"
Test-Service -Name "Flowise" -Url "http://localhost:3001"
Test-Service -Name "Grafana Monitoring" -Url "http://localhost:3003"

# Model inference test
Test-ModelInference

# Docker containers
Test-DockerContainers

# Python environment
Test-PythonEnvironment

# Show summary and exit
$exitCode = Show-Summary
exit $exitCode