@echo off
REM Document Analyzer - Start Backend (Windows)
REM This script starts the backend server

echo ========================================
echo Document Analyzer - Starting Backend
echo ========================================
echo.

cd /d "%~dp0scripts\run"

REM Run the backend start script
if exist "run_backend.bat" (
    call run_backend.bat
) else (
    echo Error: Backend start script not found in scripts\run\
    exit /b 1
)
