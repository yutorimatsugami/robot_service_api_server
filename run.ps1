# Robot Service API Server Run Script for Windows
Write-Host "🚀 Starting Robot Service API Server..." -ForegroundColor Cyan

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Load environment variables
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
}

# Start server
Set-Location src
$host_addr = if ($env:HOST) { $env:HOST } else { "0.0.0.0" }
$port = if ($env:PORT) { $env:PORT } else { "8000" }
uvicorn main:app --reload --host $host_addr --port $port
