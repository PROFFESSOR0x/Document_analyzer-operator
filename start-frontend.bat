@echo off
REM Document Analyzer - Start Frontend (Windows)
REM This script starts the frontend development server

echo ========================================
echo Document Analyzer - Starting Frontend
echo ========================================
echo.

cd /d "%~dp0scripts\run"

REM Run the frontend start script
if exist "run_frontend.bat" (
    call run_frontend.bat
) else (
    echo Error: Frontend start script not found in scripts\run\
    exit /b 1
)
