@echo off
echo ============================================================
echo Starting Adversarial Knowledge Cartographer API Server
echo                    FINAL VERBOSE MODE
echo ============================================================
echo.
echo Server will be available at:
echo   - Main API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - Health Check: http://localhost:8000/health
echo.
echo New Graph Endpoints Available:
echo   - /api/research/{session_id}/graph - Full graph data
echo   - /api/research/{session_id}/graph/stats - Graph statistics
echo   - /api/research/{session_id}/graph/entities - Entity list
echo   - /api/research/{session_id}/graph/conflicts - Conflict details
echo.
echo FINAL VERBOSE LOGGING - You WILL see:
echo   🚀 API startup messages
echo   🌐 All HTTP requests with emojis
echo   ✅ Response status and timing
echo   🆔 Session ID generation
echo   📋 Research workflow initialization
echo   🔧 Agent initialization and execution
echo   📊 Real-time progress updates
echo   ⚡ Background task execution
echo   💾 Checkpoint saves
echo   🔍 Source collection details
echo   🗺️ Knowledge graph building
echo   ⚔️ Adversarial analysis
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Kill any existing server on port 8000
echo Checking for existing server...
netstat -ano | findstr :8000 >nul 2>&1
if not errorlevel 1 (
    echo Found existing server on port 8000, attempting to stop it...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /PID %%a /F >nul 2>&1
    timeout /t 2 >nul
)

REM Set environment variables for maximum verbosity
set LOG_LEVEL=DEBUG
set PYTHONUNBUFFERED=1

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import uvicorn, fastapi" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Required packages not found
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install requirements
        pause
        exit /b 1
    )
)

echo Starting server with MAXIMUM verbose logging...
echo Environment: LOG_LEVEL=DEBUG, PYTHONUNBUFFERED=1
echo.
echo ============================================================
echo                    VERBOSE SERVER OUTPUT
echo ============================================================

REM Start server with all verbose options enabled
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000 --access-log --log-level debug --use-colors --loop asyncio