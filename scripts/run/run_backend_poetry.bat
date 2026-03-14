@echo off
REM Quick start script for running backend with Poetry
REM =============================================================================

echo.
echo =============================================================================
echo Document Analyzer Operator - Backend (Poetry)
echo =============================================================================
echo.

cd /d "%~dp0backend"

REM Check if .env exists
if not exist ".env" (
    echo [INFO] .env not found, generating...
    python scripts\generate_env.py
    if errorlevel 1 (
        echo [ERROR] Failed to generate .env
        pause
        exit /b 1
    )
    echo [OK] .env created
    echo.
)

REM Check if Poetry is installed
where poetry >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Poetry not found!
    echo Please install Poetry from: https://python-poetry.org/docs/
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
call poetry install
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

echo [2/3] Running database migrations...
call poetry run alembic upgrade head
if errorlevel 1 (
    echo [WARNING] Migration failed - make sure PostgreSQL is running
    echo You can run migrations later manually
    echo.
) else (
    echo [OK] Migrations completed
    echo.
)

echo [3/3] Starting backend server...
echo.
echo =============================================================================
echo Server starting...
echo =============================================================================
echo.
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo =============================================================================
echo.

REM Start server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
