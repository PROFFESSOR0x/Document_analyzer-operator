@echo off
REM Document Analyzer - Cleanup Script (Windows)
REM This script removes temporary files and build caches

echo ========================================
echo Document Analyzer - Cleanup
echo ========================================
echo.

cd /d "%~dp0scripts\maintenance"

REM Run the cleanup script
if exist "cleanup.bat" (
    call cleanup.bat
) else (
    echo Error: Cleanup script not found in scripts\maintenance\
    exit /b 1
)
