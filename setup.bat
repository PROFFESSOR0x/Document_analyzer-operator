@echo off
REM Document Analyzer - Main Setup Script (Windows)
REM This script calls the full setup automation

echo ========================================
echo Document Analyzer - Setup
echo ========================================
echo.

cd /d "%~dp0scripts\setup"

REM Run the auto setup script
if exist "setup_auto.bat" (
    call setup_auto.bat
) else if exist "quick_setup.bat" (
    call quick_setup.bat
) else (
    echo Error: Setup script not found in scripts\setup\
    exit /b 1
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
