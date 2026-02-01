# PowerShell script to start the Adversarial Knowledge Cartographer API Server

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Adversarial Knowledge Cartographer API Server" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Green
Write-Host "  - Main API: http://localhost:8000" -ForegroundColor White
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "New Graph Endpoints Available:" -ForegroundColor Yellow
Write-Host "  - /api/research/{session_id}/graph - Full graph data" -ForegroundColor White
Write-Host "  - /api/research/{session_id}/graph/stats - Graph statistics" -ForegroundColor White
Write-Host "  - /api/research/{session_id}/graph/entities - Entity list" -ForegroundColor White
Write-Host "  - /api/research/{session_id}/graph/conflicts - Conflict details" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required packages are installed
try {
    python -c "import uvicorn, fastapi" 2>$null
    Write-Host "Required packages found" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Required packages not found" -ForegroundColor Yellow
    Write-Host "Installing requirements..." -ForegroundColor Yellow
    
    try {
        pip install -r requirements.txt
        Write-Host "Requirements installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "Failed to install requirements" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "Starting server with verbose logging..." -ForegroundColor Green
Write-Host ""

# Start the server
try {
    python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000 --access-log --log-level debug
} catch {
    Write-Host "Failed to start server: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}