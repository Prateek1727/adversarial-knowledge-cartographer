@echo off
echo ========================================
echo Adversarial Knowledge Cartographer
echo Starting Frontend Visualization...
echo ========================================
echo.

cd frontend

echo Installing dependencies (if needed)...
call npm install

echo.
echo Starting React development server...
echo Frontend will open at http://localhost:3000
echo.
echo Make sure the backend server is running on port 8000!
echo.
echo Press Ctrl+C to stop the server
echo.

call npm start

pause
