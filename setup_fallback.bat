@echo off
REM Simple fallback setup if main setup fails

echo =============================================================================
echo Document Analyzer Operator - Simple Fallback Setup
echo =============================================================================
echo.

cd /d "%~dp0"

REM Check Python
echo Checking Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    pause
    exit /b 1
)
echo Python found
echo.

REM Generate backend .env manually
echo Creating backend .env...
(
echo APP_ENV=development
echo APP_DEBUG=true
echo APP_URL=http://localhost:8000
echo SECRET_KEY=dev-secret-key-%RANDOM%%RANDOM%%RANDOM%%RANDOM%
echo DATABASE_URL=postgresql://document_user:document_pass@localhost:5432/document_analyzer
echo REDIS_URL=redis://localhost:6379
echo ENCRYPTION_KEY=c2VjcmV0LWtleS1mb3ItZGV2ZWxvcG1lbnQtb25seQ==
echo JWT_SECRET_KEY=dev-jwt-secret-%RANDOM%%RANDOM%%RANDOM%%RANDOM%
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
echo [OK] Created backend\.env
echo.

REM Generate frontend .env.local manually
echo Creating frontend .env.local...
(
echo NEXT_PUBLIC_API_URL=http://localhost:8000
echo NEXT_PUBLIC_WS_URL=ws://localhost:8000
echo NEXT_PUBLIC_ENABLE_WEBSOCKET=true
echo NEXT_PUBLIC_ENABLE_ANALYTICS=true
) > frontend\.env.local
echo [OK] Created frontend\.env.local
echo.

REM Install backend dependencies
echo Installing backend dependencies...
cd backend
call poetry install
cd ..
echo.

REM Install frontend dependencies (skip if fails)
echo Installing frontend dependencies...
cd frontend
call npm install --legacy-peer-deps
if %errorlevel% neq 0 (
    echo.
    echo WARNING: npm install failed
    echo You can install manually: cd frontend ^&^& npm install
    echo.
) else (
    echo [OK] Frontend dependencies installed
)
cd ..
echo.

echo =============================================================================
echo Setup Complete!
echo =============================================================================
echo.
echo Next steps:
echo 1. Start backend: cd backend ^&^& poetry run uvicorn app.main:app --reload
echo 2. Start frontend: cd frontend ^&^& npm run dev
echo.
pause
