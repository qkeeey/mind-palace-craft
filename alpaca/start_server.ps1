# Quick Start Backend Server
# Run this script to start the API server for the RAG chatbot

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🚀 Starting MindPalace Backend Server" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Change to alpaca directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "📍 Working directory: $PWD" -ForegroundColor Yellow
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if virtual environment should be activated
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🏥 Running diagnostics..." -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Run diagnostic script
python diagnose_rag.py

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
$response = Read-Host "Continue to start server? (Y/n)"
if ($response -eq "n" -or $response -eq "N") {
    Write-Host "❌ Cancelled" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🚀 Starting API Server..." -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Server will be available at:" -ForegroundColor Yellow
Write-Host "   http://localhost:8081" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 API Documentation:" -ForegroundColor Yellow
Write-Host "   http://localhost:8081/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
python api_server.py
