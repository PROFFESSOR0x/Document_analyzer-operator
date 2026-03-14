@echo off
setlocal enabledelayedexpansion

REM =============================================================================
REM Document Analyzer Operator - Simple Automated Setup (Windows)
REM =============================================================================
REM This script sets up the entire platform automatically
REM No manual .env configuration needed!
REM =============================================================================

echo =============================================================================
echo Document Analyzer Operator - Automated Setup (Windows)
echo =============================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM =============================================================================
REM Step 1: Check Python
REM =============================================================================
echo [STEP 1/6] Checking Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.11+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found
python --version
echo.

REM =============================================================================
REM Step 2: Check Node.js
REM =============================================================================
echo [STEP 2/6] Checking Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js found
node --version
echo.

REM =============================================================================
REM Step 3: Generate Backend .env
REM =============================================================================
echo [STEP 3/6] Generating backend environment...
if exist "backend\scripts\generate_env.py" (
    python backend\scripts\generate_env.py
    if !errorlevel! neq 0 (
        echo [WARNING] Backend env generation had issues, continuing...
    )
) else (
    echo [WARNING] generate_env.py not found, creating basic .env
    (
        echo APP_ENV=development
        echo APP_DEBUG=true
        echo APP_URL=http://localhost:8000
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo DATABASE_URL=postgresql://document_user:document_pass@localhost:5432/document_analyzer
        echo REDIS_URL=redis://localhost:6379
        echo ENCRYPTION_KEY=c2VjcmV0LWtleS1mb3ItZGV2ZWxvcG1lbnQtb25seQ==
        echo JWT_SECRET_KEY=dev-jwt-secret-change-in-production
        echo JWT_ALGORITHM=HS256
        echo JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
        echo OPENAI_API_KEY=
        echo ANTHROPIC_API_KEY=
        echo GROQ_API_KEY=
        echo DEFAULT_LLM_PROVIDER=local
        echo LLM_TEMPERATURE=0.7
        echo LLM_MAX_TOKENS=4096
        echo LOG_LEVEL=INFO
        echo UVICORN_WORKERS=4
        echo MAX_UPLOAD_SIZE_MB=10
        echo ENABLE_WEBSOCKET=true
        echo ENABLE_ANALYTICS=true
    ) > backend\.env
    echo [OK] Created basic backend\.env
)
echo.

REM =============================================================================
REM Step 4: Generate Frontend .env.local
REM =============================================================================
echo [STEP 4/6] Generating frontend environment...
if exist "frontend\scripts\generate_env.js" (
    node frontend\scripts\generate_env.js
    if !errorlevel! neq 0 (
        echo [WARNING] Frontend env generation had issues, continuing...
    )
) else (
    echo [WARNING] generate_env.js not found, creating basic .env.local
    (
        echo NEXT_PUBLIC_API_URL=http://localhost:8000
        echo NEXT_PUBLIC_WS_URL=ws://localhost:8000
        echo NEXT_PUBLIC_ENABLE_WEBSOCKET=true
        echo NEXT_PUBLIC_ENABLE_ANALYTICS=true
    ) > frontend\.env.local
    echo [OK] Created basic frontend\.env.local
)
echo.

REM =============================================================================
REM Step 5: Install Dependencies
REM =============================================================================
echo [STEP 5/6] Installing dependencies...
echo.

echo Installing backend dependencies (this may take a few minutes)...
cd /d "%~dp0\backend"
if exist "pyproject.toml" (
    call poetry install
    if !errorlevel! neq 0 (
        echo [WARNING] Poetry install failed, trying pip...
        python -m pip install -e .
    )
) else (
    echo [WARNING] pyproject.toml not found
)
echo.

echo Installing frontend dependencies...
cd /d "%~dp0\frontend"
if exist "package.json" (
    call npm install
) else (
    echo [WARNING] package.json not found
)
cd /d "%~dp0"
echo.

REM =============================================================================
REM Step 6: Run Database Migrations
REM =============================================================================
echo [STEP 6/6] Running database migrations...
cd /d "%~dp0\backend"
if exist "alembic.ini" (
    call poetry run alembic upgrade head
    if !errorlevel! neq 0 (
        echo [WARNING] Migration failed - you may need to start PostgreSQL first
    ) else (
        echo [OK] Migrations completed
    )
) else (
    echo [WARNING] alembic.ini not found
)
cd /d "%~dp0"
echo.

REM =============================================================================
REM Setup Complete
REM =============================================================================
echo =============================================================================
echo [OK] Setup Complete!
echo =============================================================================
echo.
echo Next steps:
echo.
echo 1. Start PostgreSQL and Redis services
echo    - PostgreSQL: net start postgresql
echo    - Redis: net start Redis
echo.
echo 2. Start the backend (in a new terminal):
echo    cd backend
echo    poetry run uvicorn app.main:app --reload
echo.
echo 3. Start the frontend (in another terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 4. Access the application:
echo    - Frontend: http://localhost:3000
echo    - API Docs: http://localhost:8000/docs
echo.
echo Optional: Configure LLM API keys in backend\.env
echo    - OPENAI_API_KEY=sk-...
echo    - ANTHROPIC_API_KEY=sk-ant-...
echo    - GROQ_API_KEY=...
echo.
echo For more information, see:
echo    - ZERO_CONFIG_SETUP.md
echo    - docs/AUTO_SETUP_GUIDE.md
echo.
echo =============================================================================

pause
