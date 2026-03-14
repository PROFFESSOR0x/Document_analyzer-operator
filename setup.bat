@echo off
REM Document Analyzer Operator - Root Setup Script (Windows)
REM This script sets up both backend and frontend for native (non-Docker) development
REM Updated to integrate with automated environment generators

echo ================================================
echo Document Analyzer Operator - Complete Setup
echo ================================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check prerequisites
echo [INFO] Checking prerequisites...

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Install Python 3.11+: https://www.python.org/downloads/
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed
    echo Install Node.js 18+: https://nodejs.org/
    pause
    exit /b 1
)

git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed
    echo Install Git: https://git-scm.com/downloads
    pause
    exit /b 1
)

echo [INFO] Prerequisites check passed
echo.

REM Create logs directory
echo [INFO] Creating logs directory...
if not exist "logs" mkdir logs
echo [INFO] Logs directory created
echo.

REM Generate environment files
echo ================================================
echo Environment Configuration
echo ================================================
echo.

REM Check if .env files exist
set BACKEND_ENV_EXISTS=false
set FRONTEND_ENV_EXISTS=false

if exist "%SCRIPT_DIR%backend\.env" set BACKEND_ENV_EXISTS=true
if exist "%SCRIPT_DIR%frontend\.env.local" set FRONTEND_ENV_EXISTS=true

if "%BACKEND_ENV_EXISTS%"=="true" (
    echo [INFO] Backend .env already exists
)
if "%FRONTEND_ENV_EXISTS%"=="true" (
    echo [INFO] Frontend .env.local already exists
)

if "%BACKEND_ENV_EXISTS%"=="true" (
    set /p REGENERATE="Regenerate environment files? (y/N): "
    if /i "%REGENERATE%"=="y" (
        echo [INFO] Regenerating environment files...
        
        if exist "%SCRIPT_DIR%backend\.env" (
            echo [INFO] Regenerating backend .env...
            cd /d "%SCRIPT_DIR%backend"
            python scripts\generate_env.py --force
            cd /d "%SCRIPT_DIR%"
        )
        
        if exist "%SCRIPT_DIR%frontend\.env.local" (
            echo [INFO] Regenerating frontend .env.local...
            cd /d "%SCRIPT_DIR%frontend"
            node scripts\generate_env.js --force
            cd /d "%SCRIPT_DIR%"
        )
    ) else (
        echo [INFO] Keeping existing environment files
    )
) else (
    echo [INFO] Generating environment files...
    
    cd /d "%SCRIPT_DIR%backend"
    python scripts\generate_env.py
    cd /d "%SCRIPT_DIR%"
    
    cd /d "%SCRIPT_DIR%frontend"
    node scripts\generate_env.js
    cd /d "%SCRIPT_DIR%"
)

echo.

REM Setup backend
echo ================================================
echo Setting up Backend
echo ================================================
cd /d "%SCRIPT_DIR%backend"

if exist "setup_native.bat" (
    call setup_native.bat
) else (
    echo [ERROR] Backend setup script not found!
    pause
    exit /b 1
)

cd /d "%SCRIPT_DIR%"
echo.

REM Setup frontend
echo ================================================
echo Setting up Frontend
echo ================================================
cd /d "%SCRIPT_DIR%frontend"

if exist "setup_native.bat" (
    call setup_native.bat
) else (
    echo [ERROR] Frontend setup script not found!
    pause
    exit /b 1
)

cd /d "%SCRIPT_DIR%"
echo.

REM Validate setup
echo ================================================
echo Validating Setup
echo ================================================
if exist "%SCRIPT_DIR%scripts\validate_env.py" (
    python "%SCRIPT_DIR%scripts\validate_env.py"
    if errorlevel 1 (
        echo [WARNING] Environment validation found issues
        echo Review the validation output above
    )
) else (
    echo [INFO] Validation script not found, skipping validation
)

echo.

echo ================================================
echo Complete Setup Finished!
echo ================================================
echo.
echo To start all services:
echo   start.bat
echo.
echo To start individual services:
echo   Backend:  cd backend ^&^& run_native.bat
echo   Frontend: cd frontend ^&^& run_native.bat
echo.
echo To stop all services:
echo   stop.bat
echo.
echo Documentation:
echo   - API: http://localhost:8000/docs
echo   - Frontend: http://localhost:3000
echo.
echo ================================================
pause
