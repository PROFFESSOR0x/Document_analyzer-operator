@echo off
REM Document Analyzer Operator - Frontend Native Setup Script (Windows)
REM This script sets up the frontend for native (non-Docker) development

echo ============================================
echo Document Analyzer Operator - Frontend Setup
echo ============================================
echo.

REM Check Node.js installation
echo [INFO] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18 or higher.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=2 delims=v" %%i in ('node --version') do set NODE_VERSION=%%i
for /f "tokens=1 delims=." %%i in ("%NODE_VERSION%") do set NODE_MAJOR=%%i

if %NODE_MAJOR% LSS 18 (
    echo [ERROR] Node.js 18 or higher is required. Found: v%NODE_VERSION%
    pause
    exit /b 1
)

echo [INFO] Node.js version: v%NODE_VERSION%

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not installed
    pause
    exit /b 1
)

echo [INFO] npm version: $(npm --version)
echo.

REM Install dependencies
echo [INFO] Installing dependencies...

if exist "node_modules" (
    echo [WARN] Removing existing node_modules...
    rmdir /s /q node_modules
)

call npm install
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [INFO] Dependencies installed successfully
echo.

REM Setup environment file
echo [INFO] Setting up environment file...
if not exist ".env.local" (
    if exist ".env.example" (
        copy .env.example .env.local
        echo [INFO] Created .env.local from .env.example
        echo [WARN] Please review and update .env.local with your settings
    ) else (
        echo [ERROR] .env.example not found!
        pause
        exit /b 1
    )
) else (
    echo [WARN] .env.local already exists. Skipping...
)
echo.

REM Verify installation
echo [INFO] Verifying installation...

call npm run type-check >nul 2>&1
if errorlevel 1 (
    echo [WARN] TypeScript check has warnings. Review with: npm run type-check
) else (
    echo [INFO] TypeScript check passed
)

call npm run lint >nul 2>&1
if errorlevel 1 (
    echo [WARN] Linting has warnings. Review with: npm run lint
) else (
    echo [INFO] Linting passed
)

echo [INFO] Verification complete
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo To start the development server:
echo   run_native.bat
echo.
echo Or manually:
echo   npm run dev
echo.
echo To build for production:
echo   npm run build
echo.
echo To run tests:
echo   npm run test
echo.
echo ============================================
pause
