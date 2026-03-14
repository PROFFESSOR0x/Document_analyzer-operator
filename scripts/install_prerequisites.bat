@echo off
REM Document Analyzer Operator - Prerequisites Installer (Windows)
REM This script installs all system dependencies needed for native deployment

echo ================================================
echo Document Analyzer Operator - Prerequisites Installer
echo ================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if errorlevel 1 (
    echo [WARN] This script should be run as Administrator
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [INFO] Running as Administrator
echo.

REM Check Chocolatey
echo [INFO] Checking Chocolatey package manager...
choco --version >nul 2>&1
if errorlevel 1 (
    echo [WARN] Chocolatey not found. Installing Chocolatey...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    echo [INFO] Chocolatey installed
) else (
    for /f "tokens=3" %%i in ('choco --version') do set CHOCO_VERSION=%%i
    echo [INFO] Chocolatey version: %CHOCO_VERSION%
)
echo.

REM Install Git
echo [INFO] Checking Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Git...
    choco install -y git
    echo [INFO] Git installed
) else (
    for /f "tokens=3" %%i in ('git --version') do set GIT_VERSION=%%i
    echo [INFO] Git is already installed: %GIT_VERSION%
)
echo.

REM Install Python 3.11
echo [INFO] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Python 3.11...
    choco install -y python311
    echo [INFO] Python installed
) else (
    for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [INFO] Python is already installed: %PYTHON_VERSION%
)
echo.

REM Install Poetry
echo [INFO] Checking Poetry...
poetry --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Poetry...
    powershell -Command "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
    echo [INFO] Poetry installed
) else (
    for /f "tokens=3" %%i in ('poetry --version') do set POETRY_VERSION=%%i
    echo [INFO] Poetry is already installed: %POETRY_VERSION%
)
echo.

REM Install Node.js 20
echo [INFO] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Node.js 20...
    choco install -y nodejs-lts
    echo [INFO] Node.js installed
) else (
    for /f "tokens=2 delims=v" %%i in ('node --version') do set NODE_VERSION=%%i
    for /f "tokens=1 delims=." %%j in ("%NODE_VERSION%") do set NODE_MAJOR=%%j
    if %NODE_MAJOR% GEQ 18 (
        echo [INFO] Node.js is already installed: v%NODE_VERSION%
    ) else (
        echo [WARN] Node.js version is below 18. Installing Node.js 20...
        choco install -y nodejs-lts
        echo [INFO] Node.js installed
    )
)
echo.

REM Install PostgreSQL 16
echo [INFO] Checking PostgreSQL...
psql --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PostgreSQL 16...
    choco install -y postgresql16
    echo [INFO] PostgreSQL installed
) else (
    for /f "tokens=3" %%i in ('psql --version') do set PG_VERSION=%%i
    echo [INFO] PostgreSQL is already installed: %PG_VERSION%
)
echo.

REM Install Redis
echo [INFO] Checking Redis...
redis-server --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Redis...
    choco install -y redis-64
    echo [INFO] Redis installed
) else (
    for /f "tokens=4" %%i in ('redis-server --version') do set REDIS_VERSION=%%i
    echo [INFO] Redis is already installed: %REDIS_VERSION%
)
echo.

REM Install additional tools
echo [INFO] Installing additional tools...
choco install -y visualstudio2022buildtools visualstudio2022-workload-vctools --ignore-checksums
echo [INFO] Build tools installed
echo.

REM Start services
echo [INFO] Starting services...

REM Start PostgreSQL
net start postgresql-x64-16 >nul 2>&1
if errorlevel 1 (
    echo [WARN] Could not start PostgreSQL service
) else (
    echo [INFO] PostgreSQL service started
)

REM Start Redis
net start Redis >nul 2>&1
if errorlevel 1 (
    echo [WARN] Could not start Redis service
) else (
    echo [INFO] Redis service started
)

echo.
echo ================================================
echo Prerequisites Installation Complete!
echo ================================================
echo.
echo Installed components:
git --version
python --version
poetry --version
node --version
npm --version
psql --version
redis-server --version
echo.
echo Next steps:
echo   1. Run: setup.bat
echo   2. Configure database credentials in backend\.env
echo   3. Start services: start.bat
echo.
echo ================================================
pause
