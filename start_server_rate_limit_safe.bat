@echo off
echo ============================================================
echo Starting Adversarial Knowledge Cartographer API Server
echo              RATE LIMIT SAFE MODE
echo ============================================================
echo.
echo Server will be available at:
echo   - Main API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - Health Check: http://localhost:8000/health
echo.
echo RATE LIMITING IMPROVEMENTS:
echo   ✅ Switched to llama-3.1-70b-versatile (more efficient)
echo   ✅ Added exponential backoff retry logic
echo   ✅ Automatic rate limit detection and waiting
echo   ✅ Maximum 3 retries with smart delays
echo   ⏳ Will automatically wait when rate limits hit
echo.
echo GROQ RATE LIMITS (Free Tier):
echo   - 14,400 requests per day
echo   - 6,000 tokens per minute
echo   - Resets every minute for tokens
echo.
echo If you still hit rate limits:
echo   1. Wait 60 seconds for token reset
echo   2. Consider using fewer iterations (MAX_ITERATIONS=1)
echo   3. Use smaller research topics
echo   4. Switch to OpenAI/Anthropic if needed
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

REM Set environment variables for rate limit safe operation
set LOG_LEVEL=INFO
set PYTHONUNBUFFERED=1
set MAX_ITERATIONS=2
set MIN_SOURCES=8

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

echo Starting server with rate limit safe configuration...
echo Environment: MAX_ITERATIONS=2, MIN_SOURCES=8
echo Model: llama-3.1-70b-versatile (more efficient)
echo.
echo ============================================================
echo                    RATE LIMIT SAFE SERVER
echo ============================================================

REM Start server with rate limit safe options
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000 --log-level info