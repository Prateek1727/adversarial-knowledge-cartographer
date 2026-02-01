@echo off
echo ============================================================
echo Starting Adversarial Knowledge Cartographer API Server
echo                    VERBOSE LOGGING MODE
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
echo VERBOSE LOGGING ENABLED - You will see:
echo   🌐 All HTTP requests (GET, POST, etc.)
echo   ✅ Response status codes and timing
echo   🚀 Background workflow progress
echo   📊 Research session activities
echo   🔧 System operations and debugging info
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

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

echo Starting server with verbose logging...
echo.
echo ============================================================
echo                    SERVER OUTPUT BELOW
echo ============================================================
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000 --access-log --log-level debug