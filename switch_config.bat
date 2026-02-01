@echo off
REM Switch between standard and optimized configuration

echo ========================================
echo Configuration Switcher
echo ========================================
echo.
echo Current configuration:
echo.
findstr /C:"MAX_ITERATIONS" .env
findstr /C:"MIN_SOURCES" .env
findstr /C:"MAX_SOURCES_PER_QUERY" .env
echo.
echo ========================================
echo.
echo Choose configuration:
echo 1. STANDARD (Fast, 10 sources, 3 iterations)
echo 2. OPTIMIZED (Better quality, 30 sources, 5 iterations)
echo 3. MAXIMUM (Best quality, 50 sources, 7 iterations)
echo 4. Cancel
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" goto standard
if "%choice%"=="2" goto optimized
if "%choice%"=="3" goto maximum
if "%choice%"=="4" goto end
echo Invalid choice!
goto end

:standard
echo.
echo Switching to STANDARD configuration...
powershell -Command "(Get-Content .env) -replace 'MAX_ITERATIONS=.*', 'MAX_ITERATIONS=3' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'MIN_SOURCES=.*', 'MIN_SOURCES=10' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'MAX_SOURCES_PER_QUERY=.*', 'MAX_SOURCES_PER_QUERY=10' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'DOMAIN_WEIGHT=.*', 'DOMAIN_WEIGHT=0.4' | Set-Content .env"
echo.
echo ✓ Configuration updated to STANDARD
echo   - Processing time: ~2-3 minutes
echo   - Sources: ~10
echo   - Iterations: 3
goto end

:optimized
echo.
echo Switching to OPTIMIZED configuration...
powershell -Command "(Get-Content .env) -replace 'MAX_ITERATIONS=.*', 'MAX_ITERATIONS=5' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'MIN_SOURCES=.*', 'MIN_SOURCES=30' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'MAX_SOURCES_PER_QUERY=.*', 'MAX_SOURCES_PER_QUERY=15' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'DOMAIN_WEIGHT=.*', 'DOMAIN_WEIGHT=0.5' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'RECENCY_WEIGHT=.*', 'RECENCY_WEIGHT=0.2' | Set-Content .env"
echo.
echo ✓ Configuration updated to OPTIMIZED
echo   - Processing time: ~5-10 minutes
echo   - Sources: ~30
echo   - Iterations: 5
goto end

:maximum
echo.
echo Switching to MAXIMUM configuration...
powershell -Command "(Get-Content .env) -replace 'MAX_ITERATIONS=.*', 'MAX_ITERATIONS=7' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'MIN_SOURCES=.*', 'MIN_SOURCES=50' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'MAX_SOURCES_PER_QUERY=.*', 'MAX_SOURCES_PER_QUERY=20' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'DOMAIN_WEIGHT=.*', 'DOMAIN_WEIGHT=0.5' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'RECENCY_WEIGHT=.*', 'RECENCY_WEIGHT=0.2' | Set-Content .env"
echo.
echo ✓ Configuration updated to MAXIMUM
echo   - Processing time: ~10-15 minutes
echo   - Sources: ~50
echo   - Iterations: 7
echo   - WARNING: Uses more API credits!
goto end

:end
echo.
echo ========================================
echo.
echo New configuration:
echo.
findstr /C:"MAX_ITERATIONS" .env
findstr /C:"MIN_SOURCES" .env
findstr /C:"MAX_SOURCES_PER_QUERY" .env
echo.
echo ========================================
echo.
echo IMPORTANT: Restart your server for changes to take effect!
echo Run: start_server.bat
echo.
pause
