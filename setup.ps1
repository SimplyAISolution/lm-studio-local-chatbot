# LM Studio Local Chatbot Setup Script
# PowerShell version

Write-Host "🚀 LM Studio Local Chatbot Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.7+ first." -ForegroundColor Red
    Write-Host "Download from: https://python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
try {
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "pip install failed"
    }
    Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file from .env.example" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start LM Studio and load a model" -ForegroundColor White
Write-Host "2. Start the local server in LM Studio" -ForegroundColor White
Write-Host "3. Run one of the interfaces:" -ForegroundColor White
Write-Host "   - CLI: python chatbot_cli.py" -ForegroundColor Yellow
Write-Host "   - Web UI: streamlit run streamlit_app.py" -ForegroundColor Yellow
Write-Host "   - Gradio UI: python gradio_app.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "To test the connection: python test_connection.py" -ForegroundColor Magenta
Write-Host ""
Read-Host "Press Enter to exit"