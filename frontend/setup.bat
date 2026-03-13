@echo off
echo Document Analyzer Operator - Frontend Setup
echo ===========================================
echo.

echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed. Please install Node.js 20 or higher.
    exit /b 1
)

echo Node.js found!
echo.

echo Installing dependencies...
call npm install

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

echo Copying environment file...
if not exist .env.local (
    copy .env.example .env.local
    echo .env.local created. Please update with your settings.
) else (
    echo .env.local already exists.
)

echo.
echo ===========================================
echo Setup complete!
echo.
echo To start the development server:
echo   npm run dev
echo.
echo To build for production:
echo   npm run build
echo.
echo To run tests:
echo   npm run test
echo.
echo ===========================================
