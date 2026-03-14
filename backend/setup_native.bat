@echo off
REM Document Analyzer Operator - Backend Native Setup Script (Windows)
REM This script sets up the backend for native (non-Docker) development

echo ==========================================
echo Document Analyzer Operator - Backend Setup
echo ==========================================
echo.

REM Check Python version
echo [INFO] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.11 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [INFO] Python version: %PYTHON_VERSION%

REM Check Python version is 3.11+
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>nul
if errorlevel 1 (
    echo [ERROR] Python 3.11 or higher is required. Found: %PYTHON_VERSION%
    pause
    exit /b 1
)

echo.
echo [INFO] Checking Poetry installation...
poetry --version >nul 2>&1
if errorlevel 1 (
    echo [WARN] Poetry not found. Installing Poetry...
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing | Invoke-Expression) -replace "`r", ""
    
    REM Add poetry to PATH for this session
    set "PATH=%USERPROFILE%\AppData\Roaming\Python\Scripts;%PATH%"
    
    poetry --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Poetry installation failed. Please install manually.
        echo See: https://python-poetry.org/docs/
        pause
        exit /b 1
    )
    echo [INFO] Poetry installed successfully
) else (
    for /f "tokens=3" %%i in ('poetry --version') do set POETRY_VERSION=%%i
    echo [INFO] Poetry version: %POETRY_VERSION%
)

echo.
echo [INFO] Setting up Python virtual environment...
if exist ".venv" (
    echo [WARN] Virtual environment already exists. Recreating...
    rmdir /s /q .venv
)

poetry install --no-root
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [INFO] Virtual environment created and dependencies installed

echo.
echo [INFO] Setting up environment file...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo [INFO] Created .env file from .env.example
        
        REM Generate secure random keys using Python
        echo [INFO] Generating secure random keys...
        python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" > temp_secret.txt
        set /p SECRET_KEY=<temp_secret.txt
        del temp_secret.txt
        
        python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())" > temp_encrypt.txt
        set /p ENCRYPTION_KEY=<temp_encrypt.txt
        del temp_encrypt.txt
        
        REM Update .env file with generated keys
        powershell -Command "(Get-Content .env) -replace 'your-super-secret-key-change-this-in-production-min-32-chars', '%SECRET_KEY:SECRET_KEY=%' | Set-Content .env"
        powershell -Command "(Get-Content .env) -replace 'ENCRYPTION_KEY=', '%ENCRYPTION_KEY:ENCRYPTION_KEY=%' | Set-Content .env"
        
        echo [INFO] Secure keys generated
    ) else (
        echo [ERROR] .env.example not found!
        pause
        exit /b 1
    )
) else (
    echo [WARN] .env file already exists. Skipping...
)

echo.
echo [INFO] Running database migrations...
poetry run alembic upgrade head
if errorlevel 1 (
    echo [ERROR] Database migrations failed!
    echo Please ensure PostgreSQL is running and credentials are correct.
    pause
    exit /b 1
)
echo [INFO] Database migrations completed successfully

echo.
echo [INFO] Verifying installation...
poetry run python -c "from app.main import app" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Application import failed!
    pause
    exit /b 1
)
echo [INFO] Application import successful

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To start the backend server:
echo   run_native.bat
echo.
echo Or manually:
echo   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo API Documentation: http://localhost:8000/docs
echo.
echo ==========================================
pause
