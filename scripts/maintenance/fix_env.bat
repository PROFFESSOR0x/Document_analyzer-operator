@echo off
REM Fix .env file - correct CORS_ORIGINS format

cd /d "%~dp0backend"

echo Fixing .env file...
echo.

REM Backup existing .env
if exist ".env" (
    copy .env .env.backup
    echo [OK] Backed up .env to .env.backup
)

REM Create new .env with correct format
(
echo APP_NAME=Document Analyzer Operator
echo APP_VERSION=0.1.0
echo.
echo # Application Settings
echo APP_ENV=development
echo APP_DEBUG=true
echo APP_URL=http://localhost:8000
echo.
echo # Server Settings
echo APP_HOST=0.0.0.0
echo APP_PORT=8000
echo APP_WORKERS=4
echo APP_RELOAD=false
echo LOG_LEVEL=INFO
echo.
echo # Database Settings
echo POSTGRES_USER=document_user
echo POSTGRES_PASSWORD=document_pass
echo POSTGRES_HOST=localhost
echo POSTGRES_PORT=5432
echo POSTGRES_DB=document_analyzer
echo DATABASE_URL=postgresql://document_user:document_pass@localhost:5432/document_analyzer
echo.
echo # Redis Settings
echo REDIS_HOST=localhost
echo REDIS_PORT=6379
echo REDIS_DB=0
echo REDIS_URL=redis://localhost:6379
echo.
echo # Security Settings
echo SECRET_KEY=dev-secret-key-change-in-production-12345678901234567890
echo ENCRYPTION_KEY=c2VjcmV0LWtleS1mb3ItZGV2ZWxvcG1lbnQtb25seQ==
echo JWT_SECRET_KEY=dev-jwt-secret-change-in-production-1234567890
echo JWT_ALGORITHM=HS256
echo JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
echo.
echo # CORS Settings - MUST be valid JSON!
echo CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
echo.
echo # LLM Provider Settings
echo DEFAULT_LLM_PROVIDER=local
echo LLM_TEMPERATURE=0.7
echo LLM_MAX_TOKENS=4096
echo OPENAI_API_KEY=
echo ANTHROPIC_API_KEY=
echo GROQ_API_KEY=
echo TOGETHER_API_KEY=
echo ANYSCALE_API_KEY=
echo.
echo # Feature Flags
echo ENABLE_WEBSOCKET=true
echo ENABLE_ANALYTICS=true
echo.
echo # File Storage
echo STORAGE_TYPE=local
echo STORAGE_PATH=./storage
echo MAX_UPLOAD_SIZE_MB=10
) > .env

echo [OK] Created new .env with correct CORS_ORIGINS format
echo.
echo Note: CORS_ORIGINS must be a JSON array, e.g.:
echo CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
echo.
