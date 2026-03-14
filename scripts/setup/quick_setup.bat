@echo off
REM =============================================================================
REM Document Analyzer Operator - Quick Setup Script (Windows)
REM =============================================================================
REM This script automates the complete setup process:
REM 1. Check prerequisites (Python, Node.js, PostgreSQL, Redis)
REM 2. Generate backend .env file
REM 3. Generate frontend .env.local file
REM 4. Install backend dependencies
REM 5. Install frontend dependencies
REM 6. Run database migrations
REM 7. Validate setup
REM 8. Show success message with next steps
REM =============================================================================

echo =============================================================================
echo Document Analyzer Operator - Quick Setup (Windows)
echo =============================================================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM =============================================================================
REM Check Prerequisites
REM =============================================================================
echo [1/8] Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Install Python 3.11+: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python found: %PYTHON_VERSION%

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed
    echo Install Node.js 18+: https://nodejs.org/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js found: %NODE_VERSION%

REM Check Git
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed
    echo Install Git: https://git-scm.com/downloads
    echo.
    pause
    exit /b 1
)
echo [OK] Git found

REM Check PostgreSQL (basic check)
where psql >nul 2>&1
if errorlevel 1 (
    echo [WARNING] PostgreSQL not found in PATH
    echo Install PostgreSQL 16+: https://www.postgresql.org/download/windows/
    echo Database migrations may fail until PostgreSQL is installed
) else (
    echo [OK] PostgreSQL found
)

REM Check Redis (basic check)
where redis-cli >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Redis not found in PATH
    echo Install Redis: https://github.com/microsoftarchive/redis/releases
    echo Redis features will be unavailable until Redis is installed
) else (
    echo [OK] Redis found
)

echo.

REM =============================================================================
REM Generate Backend Environment
REM =============================================================================
echo [2/8] Generating backend environment...
echo.

cd /d "%SCRIPT_DIR%backend"

if exist ".env" (
    echo [INFO] .env file already exists
    set /p OVERWRITE="Overwrite existing .env? (y/N): "
    if /i "%OVERWRITE%"=="y" (
        python scripts\generate_env.py --force
        if errorlevel 1 (
            echo [ERROR] Failed to generate backend .env
            pause
            exit /b 1
        )
    )
) else (
    python scripts\generate_env.py
    if errorlevel 1 (
        echo [ERROR] Failed to generate backend .env
        pause
        exit /b 1
    )
)

cd /d "%SCRIPT_DIR%"
echo.

REM =============================================================================
REM Generate Frontend Environment
REM =============================================================================
echo [3/8] Generating frontend environment...
echo.

cd /d "%SCRIPT_DIR%frontend"

if exist ".env.local" (
    echo [INFO] .env.local file already exists
    set /p OVERWRITE="Overwrite existing .env.local? (y/N): "
    if /i "%OVERWRITE%"=="y" (
        node scripts\generate_env.js --force
        if errorlevel 1 (
            echo [ERROR] Failed to generate frontend .env.local
            pause
            exit /b 1
        )
    )
) else (
    node scripts\generate_env.js
    if errorlevel 1 (
        echo [ERROR] Failed to generate frontend .env.local
        pause
        exit /b 1
    )
)

cd /d "%SCRIPT_DIR%"
echo.

REM =============================================================================
REM Install Backend Dependencies
REM =============================================================================
echo [4/8] Installing backend dependencies...
echo.

cd /d "%SCRIPT_DIR%backend"

REM Check if Poetry is installed
poetry --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Poetry not found, installing...
    curl -sSL https://install.python-poetry.org | python -
    
    REM Add poetry to PATH for this session
    set PATH=%APPDATA%\Python\Scripts;%PATH%
    
    poetry --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Poetry installation failed
        echo Install manually: https://python-poetry.org/docs/
        pause
        exit /b 1
    )
)

poetry install
if errorlevel 1 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)

cd /d "%SCRIPT_DIR%"
echo.

REM =============================================================================
REM Install Frontend Dependencies
REM =============================================================================
echo [5/8] Installing frontend dependencies...
echo.

cd /d "%SCRIPT_DIR%frontend"

npm install
if errorlevel 1 (
    echo [ERROR] Failed to install frontend dependencies
    pause
    exit /b 1
)

cd /d "%SCRIPT_DIR%"
echo.

REM =============================================================================
REM Run Database Migrations
REM =============================================================================
echo [6/8] Running database migrations...
echo.

cd /d "%SCRIPT_DIR%backend"

REM Try to run migrations (may fail if DB not ready)
poetry run alembic upgrade head
if errorlevel 1 (
    echo [WARNING] Database migrations failed
    echo This is expected if PostgreSQL is not running yet
    echo You can run migrations later with: cd backend ^&^& poetry run alembic upgrade head
) else (
    echo [OK] Database migrations completed
)

cd /d "%SCRIPT_DIR%"
echo.

REM =============================================================================
REM Validate Setup
REM =============================================================================
echo [7/8] Validating setup...
echo.

python scripts\validate_env.py
if errorlevel 1 (
    echo [WARNING] Environment validation found issues
    echo Review the validation output above
) else (
    echo [OK] Environment validation passed
)

echo.

REM =============================================================================
REM Summary
REM =============================================================================
echo [8/8] Setup Summary
echo.
echo =============================================================================
echo Setup Complete!
echo =============================================================================
echo.
echo Next steps:
echo.
echo 1. Start the backend:
echo    cd backend
echo    poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 2. Start the frontend (in a new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Access the application:
echo    Frontend: http://localhost:3000
echo    API Docs: http://localhost:8000/docs
echo.
echo 4. Configure LLM API keys (optional):
echo    Edit backend\.env and add your API keys:
echo    - OPENAI_API_KEY
echo    - ANTHROPIC_API_KEY
echo    - GROQ_API_KEY
echo.
echo =============================================================================
echo.
pause
