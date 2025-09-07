# Docker Management Script for AI Swarm Intelligence System

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "build", "clean", "backup", "shell")]
    [string]$Action = "status",
    
    [string]$Service = "",
    [switch]$Follow,
    [switch]$Build,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$SwarmPath = "C:\Users\scarm\src\ai_platform"

function Write-SwarmLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO" { "Cyan" }
        default { "White" }
    }
    
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Test-DockerRunning {
    try {
        docker info | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Start-SwarmServices {
    Write-SwarmLog "Starting AI Swarm Intelligence Docker Stack..." "INFO"
    
    if (!(Test-DockerRunning)) {
        Write-SwarmLog "Docker is not running. Please start Docker Desktop." "ERROR"
        return $false
    }
    
    Push-Location $SwarmPath
    
    try {
        # Check if .env file exists
        if (!(Test-Path ".env")) {
            Write-SwarmLog "Creating .env file from template..." "INFO"
            Copy-Item ".env.docker" ".env" -Force
        }
        
        # Build if requested
        if ($Build) {
            Write-SwarmLog "Building Docker images..." "INFO"
            docker-compose build --no-cache
        }
        
        # Start services
        Write-SwarmLog "Starting services..." "INFO"
        docker-compose up -d
        
        # Wait for services to be healthy
        Write-SwarmLog "Waiting for services to be healthy..." "INFO"
        Start-Sleep -Seconds 30
        
        # Check status
        $status = docker-compose ps
        Write-SwarmLog "Services started. Status:" "SUCCESS"
        Write-Host $status
        
        Write-SwarmLog "AI Swarm Stack is starting up!" "SUCCESS"
        Write-SwarmLog "Access points:" "INFO"
        Write-Host "  - Swarm API: http://localhost:8000" -ForegroundColor Green
        Write-Host "  - Grafana Dashboard: http://localhost:3000" -ForegroundColor Green
        Write-Host "  - Prometheus: http://localhost:9090" -ForegroundColor Green
        Write-Host "  - Portainer: http://localhost:9000" -ForegroundColor Green
        Write-Host "  - Jupyter Notebook: http://localhost:8888" -ForegroundColor Green
        Write-Host "  - Kibana Logs: http://localhost:5601" -ForegroundColor Green
        
    } catch {
        Write-SwarmLog "Error starting services: $_" "ERROR"
        return $false
    } finally {
        Pop-Location
    }
    
    return $true
}

function Stop-SwarmServices {
    Write-SwarmLog "Stopping AI Swarm Intelligence Docker Stack..." "INFO"
    
    Push-Location $SwarmPath
    
    try {
        docker-compose down
        Write-SwarmLog "Services stopped successfully." "SUCCESS"
    } catch {
        Write-SwarmLog "Error stopping services: $_" "ERROR"
    } finally {
        Pop-Location
    }
}

function Restart-SwarmServices {
    Write-SwarmLog "Restarting AI Swarm Intelligence Docker Stack..." "INFO"
    Stop-SwarmServices
    Start-Sleep -Seconds 5
    Start-SwarmServices
}

function Get-SwarmStatus {
    Write-SwarmLog "AI Swarm Intelligence Docker Stack Status" "INFO"
    
    if (!(Test-DockerRunning)) {
        Write-SwarmLog "Docker is not running." "ERROR"
        return
    }
    
    Push-Location $SwarmPath
    
    try {
        Write-Host "`n=== Service Status ===" -ForegroundColor Cyan
        $status = docker-compose ps
        Write-Host $status
        
        Write-Host "`n=== Docker System Info ===" -ForegroundColor Cyan
        $systemInfo = docker system df
        Write-Host $systemInfo
        
        Write-Host "`n=== Network Status ===" -ForegroundColor Cyan
        $networks = docker network ls | Select-String "swarm"
        Write-Host $networks
        
        Write-Host "`n=== Volume Status ===" -ForegroundColor Cyan
        $volumes = docker volume ls | Select-String "swarm"
        Write-Host $volumes
        
        Write-Host "`n=== Access Points ===" -ForegroundColor Green
        Write-Host "  - AI Swarm API: http://localhost:8000/health"
        Write-Host "  - Database Manager: http://localhost:8000/database"
        Write-Host "  - Grafana Dashboard: http://localhost:3000 (admin/admin)"
        Write-Host "  - Prometheus Metrics: http://localhost:9090"
        Write-Host "  - Docker Manager: http://localhost:9000"
        Write-Host "  - Jupyter Notebook: http://localhost:8888"
        Write-Host "  - Log Dashboard: http://localhost:5601"
        
    } catch {
        Write-SwarmLog "Error getting status: $_" "ERROR"
    } finally {
        Pop-Location
    }
}

function Get-SwarmLogs {
    param(
        [string]$ServiceName = "",
        [bool]$FollowLogs = $false
    )
    
    Write-SwarmLog "Fetching logs for AI Swarm services..." "INFO"
    
    Push-Location $SwarmPath
    
    try {
        $followFlag = if ($FollowLogs) { "--follow" } else { "--tail=100" }
        
        if ($ServiceName) {
            docker-compose logs $followFlag $ServiceName
        } else {
            docker-compose logs $followFlag
        }
    } catch {
        Write-SwarmLog "Error fetching logs: $_" "ERROR"
    } finally {
        Pop-Location
    }
}

function Build-SwarmImages {
    Write-SwarmLog "Building AI Swarm Docker images..." "INFO"
    
    Push-Location $SwarmPath
    
    try {
        docker-compose build --no-cache
        Write-SwarmLog "Images built successfully." "SUCCESS"
    } catch {
        Write-SwarmLog "Error building images: $_" "ERROR"
    } finally {
        Pop-Location
    }
}

function Clean-SwarmDocker {
    Write-SwarmLog "Cleaning up Docker resources..." "INFO"
    
    if ($Force) {
        Write-SwarmLog "Force cleanup - removing all containers and volumes..." "WARN"
        
        Push-Location $SwarmPath
        
        try {
            # Stop and remove everything
            docker-compose down -v --remove-orphans
            
            # Remove images
            docker images | Select-String "swarm" | ForEach-Object {
                $imageId = ($_ -split '\s+')[2]
                docker rmi $imageId -f
            }
            
            # Clean system
            docker system prune -f
            docker volume prune -f
            
            Write-SwarmLog "Force cleanup completed." "SUCCESS"
            
        } catch {
            Write-SwarmLog "Error during cleanup: $_" "ERROR"
        } finally {
            Pop-Location
        }
    } else {
        Write-SwarmLog "Standard cleanup - removing unused resources..." "INFO"
        docker system prune -f
        Write-SwarmLog "Cleanup completed." "SUCCESS"
    }
}

function Backup-SwarmData {
    Write-SwarmLog "Creating backup of AI Swarm data..." "INFO"
    
    $backupDir = "C:\Automation\Data\docker-backups\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    try {
        # Backup volumes
        $volumes = @("swarm-database-volume", "postgres-data-volume", "redis-data-volume", "grafana-data-volume")
        
        foreach ($volume in $volumes) {
            Write-SwarmLog "Backing up volume: $volume" "INFO"
            docker run --rm -v ${volume}:/source -v ${backupDir}:/backup alpine tar czf /backup/${volume}.tar.gz -C /source .
        }
        
        # Backup configurations
        Copy-Item "$SwarmPath\*.yml" $backupDir -Force
        Copy-Item "$SwarmPath\.env" $backupDir -Force -ErrorAction SilentlyContinue
        
        # Create backup manifest
        @{
            BackupTime = Get-Date
            Volumes = $volumes
            BackupPath = $backupDir
        } | ConvertTo-Json | Out-File "$backupDir\manifest.json"
        
        Write-SwarmLog "Backup created successfully: $backupDir" "SUCCESS"
        
    } catch {
        Write-SwarmLog "Error creating backup: $_" "ERROR"
    }
}

function Open-SwarmShell {
    param([string]$ServiceName = "swarm-master")
    
    Write-SwarmLog "Opening shell in $ServiceName..." "INFO"
    
    Push-Location $SwarmPath
    
    try {
        docker-compose exec $ServiceName /bin/bash
    } catch {
        try {
            docker-compose exec $ServiceName /bin/sh
        } catch {
            Write-SwarmLog "Error opening shell: $_" "ERROR"
        }
    } finally {
        Pop-Location
    }
}

# Main script execution
Write-SwarmLog "AI Swarm Docker Manager" "INFO"
Write-SwarmLog "Action: $Action" "INFO"

switch ($Action.ToLower()) {
    "start" { 
        Start-SwarmServices 
    }
    "stop" { 
        Stop-SwarmServices 
    }
    "restart" { 
        Restart-SwarmServices 
    }
    "status" { 
        Get-SwarmStatus 
    }
    "logs" { 
        Get-SwarmLogs -ServiceName $Service -FollowLogs $Follow 
    }
    "build" { 
        Build-SwarmImages 
    }
    "clean" { 
        Clean-SwarmDocker 
    }
    "backup" { 
        Backup-SwarmData 
    }
    "shell" { 
        Open-SwarmShell -ServiceName $(if($Service){"$Service"}else{"swarm-master"})
    }
    default { 
        Write-SwarmLog "Unknown action: $Action" "ERROR"
        Write-SwarmLog "Valid actions: start, stop, restart, status, logs, build, clean, backup, shell" "INFO"
    }
}