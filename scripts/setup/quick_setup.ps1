# Quick Setup Script for Document Analyzer
# PowerShell Version

Write-Host "========================================"
Write-Host "Document Analyzer - Quick Setup"
Write-Host "========================================"
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir

# Check prerequisites
Write-Host "Checking prerequisites..."

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion"
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+"
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion"
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18+"
    exit 1
}

# Check Poetry
try {
    $poetryVersion = poetry --version 2>&1
    Write-Host "✓ Poetry found: $poetryVersion"
} catch {
    Write-Host "Installing Poetry..."
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    Write-Host "✓ Poetry installed"
}

Write-Host ""
Write-Host "Setting up backend..."
Set-Location "$rootDir\backend"
& poetry install

Write-Host ""
Write-Host "Setting up frontend..."
Set-Location "$rootDir\frontend"
npm install

Write-Host ""
Write-Host "========================================"
Write-Host "Setup complete!"
Write-Host "========================================"
Write-Host ""
Write-Host "To start the application:"
Write-Host "  Backend:  cd ..\backend && poetry run uvicorn app.main:app --reload"
Write-Host "  Frontend: cd ..\frontend && npm run dev"
Write-Host ""
