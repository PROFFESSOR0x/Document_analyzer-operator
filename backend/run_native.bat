@echo off
REM Document Analyzer Operator - Backend Native Run Script (Windows)
REM This script starts the backend server for native (non-Docker) development

echo ==========================================
echo Document Analyzer Operator - Backend
echo ==========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please run setup_native.bat first or create .env from .env.example
    pause
    exit /b 1
)
echo [INFO] Environment file loaded

REM Parse command line arguments
set RELOAD=false
set HOST=0.0.0.0
set PORT=8000
set WORKERS=1
set SKIP_CHECKS=false

:parse_args
if "%~1"=="" goto :after_parse
if /i "%~1"=="--reload" (
    set RELOAD=true
    shift
    goto :parse_args
)
if /i "%~1"=="--host" (
    set HOST=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--workers" (
    set WORKERS=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--no-check" (
    set SKIP_CHECKS=true
    shift
    goto :parse_args
)
shift
goto :parse_args

:after_parse
echo.
echo [INFO] Starting Uvicorn server on %HOST%:%PORT%...
echo [INFO] API Documentation: http://localhost:%PORT%/docs
echo [INFO] ReDoc: http://localhost:%PORT%/redoc
echo.

if "%RELOAD%"=="true" (
    echo [INFO] Running in development mode with auto-reload
    poetry run uvicorn app.main:app --host %HOST% --port %PORT% --reload --log-level info
) else (
    echo [INFO] Running in production mode with %WORKERS% workers
    poetry run uvicorn app.main:app --host %HOST% --port %PORT% --workers %WORKERS% --log-level info
)

echo.
echo ==========================================
echo Server stopped
echo ==========================================
pause
