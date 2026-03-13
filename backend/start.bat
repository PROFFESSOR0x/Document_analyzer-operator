@echo off
REM Quick start script for Document Analyzer Operator Backend (Windows)

echo ==========================================
echo Document Analyzer Operator - Backend Setup
echo ==========================================

REM Check if Docker is available
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed or not in PATH
    echo Please install Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Created .env file
    echo.
    echo IMPORTANT: Please edit .env and set:
    echo   - SECRET_KEY (generate a secure random key)
    echo   - Database credentials (if not using defaults)
    echo.
    pause
)

echo.
echo Starting Docker containers...
docker-compose up -d

echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo Checking API health...
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo API may still be starting up. Check logs with: docker-compose logs -f backend
) else (
    echo API is healthy!
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Services:
echo   - API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - PostgreSQL: localhost:5432
echo   - Redis: localhost:6379
echo   - MinIO Console: http://localhost:9001
echo.
echo Default Credentials:
echo   - PostgreSQL: postgres/postgres
echo   - MinIO: minioadmin/minioadmin
echo.
echo Next Steps:
echo   1. Create a user account via POST /api/v1/auth/register
echo   2. Login via POST /api/v1/auth/login
echo   3. Start creating agents and workflows!
echo.
echo Useful Commands:
echo   - View logs: docker-compose logs -f
echo   - Stop services: docker-compose down
echo   - Restart services: docker-compose restart
echo   - Reset database: docker-compose down -v ^&^& docker-compose up -d
echo.
pause
