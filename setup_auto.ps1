# Document Analyzer Operator - Automated Setup (PowerShell)
# This script sets up the entire platform automatically
# No manual .env configuration needed!

Write-Host "=============================================================================" -ForegroundColor Cyan
Write-Host "Document Analyzer Operator - Automated Setup (PowerShell)" -ForegroundColor Cyan
Write-Host "=============================================================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location -Path $PSScriptRoot

# Step 1: Check Python
Write-Host "[STEP 1/6] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.11+" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host ""

# Step 2: Check Node.js
Write-Host "[STEP 2/6] Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    Write-Host "Download from: https://nodejs.org/" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host ""

# Step 3: Generate Backend .env
Write-Host "[STEP 3/6] Generating backend environment..." -ForegroundColor Yellow
if (Test-Path "backend\scripts\generate_env.py") {
    try {
        python backend\scripts\generate_env.py
        Write-Host "[OK] Backend environment generated" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Backend env generation had issues" -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] Creating basic backend .env..." -ForegroundColor Cyan
    $envContent = @"
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost:8000
SECRET_KEY=dev-secret-key-$(Get-Random -Count 32 -InputObject ([char[]]"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") | ForEach-Object { $_ })
DATABASE_URL=postgresql://document_user:document_pass@localhost:5432/document_analyzer
REDIS_URL=redis://localhost:6379
ENCRYPTION_KEY=c2VjcmV0LWtleS1mb3ItZGV2ZWxvcG1lbnQtb25seQ==
JWT_SECRET_KEY=dev-jwt-secret-key-$(Get-Random -Count 32 -InputObject ([char[]]"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") | ForEach-Object { $_ })
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=
DEFAULT_LLM_PROVIDER=local
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
LOG_LEVEL=INFO
UVICORN_WORKERS=4
MAX_UPLOAD_SIZE_MB=10
ENABLE_WEBSOCKET=true
ENABLE_ANALYTICS=true
"@
    $envContent | Out-File -FilePath "backend\.env" -Encoding utf8
    Write-Host "[OK] Created backend\.env" -ForegroundColor Green
}
Write-Host ""

# Step 4: Generate Frontend .env.local
Write-Host "[STEP 4/6] Generating frontend environment..." -ForegroundColor Yellow
if (Test-Path "frontend\scripts\generate_env.js") {
    try {
        node frontend\scripts\generate_env.js
        Write-Host "[OK] Frontend environment generated" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Frontend env generation had issues" -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] Creating basic frontend .env.local..." -ForegroundColor Cyan
    $frontendEnv = @"
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_ENABLE_WEBSOCKET=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
"@
    $frontendEnv | Out-File -FilePath "frontend\.env.local" -Encoding utf8
    Write-Host "[OK] Created frontend\.env.local" -ForegroundColor Green
}
Write-Host ""

# Step 5: Install Dependencies
Write-Host "[STEP 5/6] Installing dependencies..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Installing backend dependencies (this may take a few minutes)..." -ForegroundColor Cyan
Set-Location -Path ".\backend"
if (Test-Path "pyproject.toml") {
    try {
        poetry install
        Write-Host "[OK] Backend dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Poetry install failed" -ForegroundColor Yellow
        Write-Host "Trying pip install..." -ForegroundColor Cyan
        python -m pip install -e .
    }
} else {
    Write-Host "[WARNING] pyproject.toml not found" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
Set-Location -Path "..\frontend"
if (Test-Path "package.json") {
    try {
        npm install
        Write-Host "[OK] Frontend dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] npm install failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARNING] package.json not found" -ForegroundColor Yellow
}
Set-Location -Path $PSScriptRoot
Write-Host ""

# Step 6: Run Database Migrations
Write-Host "[STEP 6/6] Running database migrations..." -ForegroundColor Yellow
Set-Location -Path ".\backend"
if (Test-Path "alembic.ini") {
    try {
        poetry run alembic upgrade head
        Write-Host "[OK] Migrations completed" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Migration failed - you may need to start PostgreSQL first" -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARNING] alembic.ini not found" -ForegroundColor Yellow
}
Set-Location -Path $PSScriptRoot
Write-Host ""

# Setup Complete
Write-Host "=============================================================================" -ForegroundColor Cyan
Write-Host "[OK] Setup Complete!" -ForegroundColor Green
Write-Host "=============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host ""
Write-Host "1. Start PostgreSQL and Redis services:" -ForegroundColor Yellow
Write-Host "   - PostgreSQL: net start postgresql" -ForegroundColor White
Write-Host "   - Redis: net start Redis" -ForegroundColor White
Write-Host ""
Write-Host "2. Start the backend (in a new terminal):" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   poetry run uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "3. Start the frontend (in another terminal):" -ForegroundColor Yellow
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "4. Access the application:" -ForegroundColor Yellow
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Optional: Configure LLM API keys in backend\.env" -ForegroundColor Yellow
Write-Host "   - OPENAI_API_KEY=sk-..." -ForegroundColor White
Write-Host "   - ANTHROPIC_API_KEY=sk-ant-..." -ForegroundColor White
Write-Host "   - GROQ_API_KEY=..." -ForegroundColor White
Write-Host ""
Write-Host "For more information, see:" -ForegroundColor Yellow
Write-Host "   - ZERO_CONFIG_SETUP.md" -ForegroundColor White
Write-Host "   - docs/AUTO_SETUP_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "=============================================================================" -ForegroundColor Cyan

pause
