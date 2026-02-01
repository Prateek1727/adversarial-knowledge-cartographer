@echo off
echo ========================================
echo Adversarial Knowledge Cartographer
echo Starting Backend Server...
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the server
echo Starting FastAPI server on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

pause
