@echo off
REM Document Analyzer Operator - Root Stop Script (Windows)
REM This script stops all services for native (non-Docker) development

echo ================================================
echo Document Analyzer Operator - Stopping Services
echo ================================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM PID file location
set PID_DIR=%SCRIPT_DIR%.pids

REM Stop backend
echo [INFO] Stopping backend...
taskkill /FI "WINDOWTITLE eq Document Analyzer Backend" /T /F >nul 2>&1
if errorlevel 1 (
    echo [WARN] Backend process not found or already stopped
) else (
    echo [INFO] Backend stopped
)

REM Stop frontend
echo [INFO] Stopping frontend...
taskkill /FI "WINDOWTITLE eq Document Analyzer Frontend" /T /F >nul 2>&1
if errorlevel 1 (
    echo [WARN] Frontend process not found or already stopped
) else (
    echo [INFO] Frontend stopped
)

REM Kill any remaining processes on our ports
echo [INFO] Cleaning up processes on ports 8000 and 3000...

REM Kill process on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill process on port 3000
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Clean up PID directory
if exist "%PID_DIR%" rmdir /s /q "%PID_DIR%"

echo.
echo ================================================
echo All Services Stopped
echo ================================================
pause
