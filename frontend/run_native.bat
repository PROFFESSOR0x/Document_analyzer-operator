@echo off
REM Document Analyzer Operator - Frontend Native Run Script (Windows)
REM This script starts the frontend server for native (non-Docker) development

echo ============================================
echo Document Analyzer Operator - Frontend
echo ============================================
echo.

REM Check if .env.local exists
if not exist ".env.local" (
    echo [ERROR] .env.local file not found!
    echo Please run setup_native.bat first or create .env.local from .env.example
    pause
    exit /b 1
)
echo [INFO] Environment file loaded
echo.

REM Parse command line arguments
set MODE=dev
set PORT=3000
set SKIP_BACKEND_CHECK=false

:parse_args
if "%~1"=="" goto :after_parse
if /i "%~1"=="--build" (
    set MODE=build
    shift
    goto :parse_args
)
if /i "%~1"=="--start" (
    set MODE=start
    shift
    goto :parse_args
)
if /i "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--no-backend-check" (
    set SKIP_BACKEND_CHECK=true
    shift
    goto :parse_args
)
shift
goto :parse_args

:after_parse
echo [INFO] Starting Next.js %MODE% server...
echo [INFO] Application: http://localhost:%PORT%
echo.

if "%MODE%"=="dev" (
    set PORT=%PORT%
    call npm run dev
) else if "%MODE%"=="build" (
    call npm run build
    if errorlevel 1 (
        echo [ERROR] Build failed!
        pause
        exit /b 1
    )
    echo [INFO] Build completed successfully
    echo [INFO] Run 'run_native.bat --start' to start production server
    pause
    exit /b 0
) else if "%MODE%"=="start" (
    set PORT=%PORT%
    call npm run start
)

echo.
echo ============================================
echo Server stopped
echo ============================================
pause
