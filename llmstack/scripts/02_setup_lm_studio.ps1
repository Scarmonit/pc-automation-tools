# LM Studio Setup Script for Windows
Write-Host "Setting up LM Studio for Windows..." -ForegroundColor Green

# Download LM Studio
$lmStudioUrl = "https://releases.lmstudio.ai/windows/x86/stable/LM-Studio-win-x64.exe"
$installerPath = "$env:TEMP\LMStudio-Setup.exe"

Write-Host "Downloading LM Studio installer..."
Invoke-WebRequest -Uri $lmStudioUrl -OutFile $installerPath

# Install LM Studio
Write-Host "Installing LM Studio..."
Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait

# Create config for headless server mode
$lmStudioConfig = @"
{
    "server": {
        "port": 1234,
        "cors": true,
        "autoStart": true
    },
    "models": {
        "autoLoad": true,
        "defaultModel": "auto"
    }
}
"@

$configPath = "$env:APPDATA\LM Studio\server_config.json"
New-Item -Path (Split-Path $configPath) -ItemType Directory -Force | Out-Null
$lmStudioConfig | Out-File -FilePath $configPath -Encoding UTF8

Write-Host "LM Studio installed successfully!" -ForegroundColor Green
Write-Host "LM Studio API will be available at: http://localhost:1234" -ForegroundColor Cyan
Write-Host "Please start LM Studio manually and enable the server mode" -ForegroundColor Yellow