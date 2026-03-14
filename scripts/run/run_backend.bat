@echo off
REM Document Analyzer Operator - Root Start Script (Windows)
REM This script starts both backend and frontend for native (non-Docker) development

echo ================================================
echo Document Analyzer Operator - Starting Services
echo ================================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM PID file location
set PID_DIR=%SCRIPT_DIR%.pids
if not exist "%PID_DIR%" mkdir "%PID_DIR%"

REM Parse arguments
set SKIP_BACKEND=false
set SKIP_FRONTEND=false

:parse_args
if "%~1"=="" goto :after_parse
if /i "%~1"=="--backend-only" (
    set SKIP_FRONTEND=true
    shift
    goto :parse_args
)
if /i "%~1"=="--frontend-only" (
    set SKIP_BACKEND=true
    shift
    goto :parse_args
)
shift
goto :parse_args

:after_parse
REM Check if services are already running
if exist "%PID_DIR%\backend.pid" (
    echo [WARN] Backend may already be running. Check Task Manager.
)

if exist "%PID_DIR%\frontend.pid" (
    echo [WARN] Frontend may already be running. Check Task Manager.
)

echo.

REM Start backend
if "%SKIP_BACKEND%"=="false" (
    echo [INFO] Starting backend...
    cd /d "%SCRIPT_DIR%backend"
    
    if exist "run_native.bat" (
        start "Document Analyzer Backend" cmd /k "run_native.bat --no-check"
        echo [INFO] Backend started in new window
    ) else (
        echo [ERROR] Backend run script not found!
        pause
        exit /b 1
    )
    
    cd /d "%SCRIPT_DIR%"
    
    REM Wait for backend
    echo [INFO] Waiting for backend to be ready...
    timeout /t 10 /nobreak >nul
)

REM Start frontend
if "%SKIP_FRONTEND%"=="false" (
    echo [INFO] Starting frontend...
    cd /d "%SCRIPT_DIR%frontend"
    
    if exist "run_native.bat" (
        start "Document Analyzer Frontend" cmd /k "run_native.bat --no-backend-check"
        echo [INFO] Frontend started in new window
    ) else (
        echo [ERROR] Frontend run script not found!
        pause
        exit /b 1
    )
    
    cd /d "%SCRIPT_DIR%"
)

echo.
echo ================================================
echo All Services Started!
echo ================================================
echo.
if "%SKIP_BACKEND%"=="false" (
    echo   - Backend API:  http://localhost:8000
    echo   - API Docs:     http://localhost:8000/docs
)
if "%SKIP_FRONTEND%"=="false" (
    echo   - Frontend:     http://localhost:3000
)
echo.
echo To stop all services:
echo   stop.bat
echo.
echo ================================================
pause
