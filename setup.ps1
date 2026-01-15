# Robot Service API Server Setup Script for Windows
Write-Host "🚀 Robot Service API Server Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Check Python
try {
    python --version | Out-Null
} catch {
    Write-Host "❌ Python is not installed." -ForegroundColor Red
    exit 1
}

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate and install
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Please edit .env and add your GEMINI_API_KEY" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Edit .env with your configuration"
Write-Host "  2. Run: .\run.ps1"
