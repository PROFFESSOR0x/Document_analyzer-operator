@echo off
REM Document Analyzer - Cleanup Script (Windows)
REM Clean temporary files and build caches

echo ========================================
echo Document Analyzer - Cleanup
echo ========================================
echo.

cd /d "%~dp0..\.."

echo Cleaning Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /q /s *.pyc 2>nul
del /q /s *.pyo 2>nul
del /q /s *.pyd 2>nul

echo Cleaning node_modules...
if exist "frontend\node_modules" rd /s /q "frontend\node_modules"

echo Cleaning build caches...
if exist "frontend\.next" rd /s /q "frontend\.next"
if exist "backend\.pytest_cache" rd /s /q "backend\.pytest_cache"
if exist "backend\.mypy_cache" rd /s /q "backend\.mypy_cache"
if exist ".pytest_cache" rd /s /q ".pytest_cache"
if exist ".mypy_cache" rd /s /q ".mypy_cache"

echo Cleaning logs...
del /q /s *.log 2>nul

echo Cleaning temporary files...
del /q /s *.tmp 2>nul
del /q /s *.bak 2>nul
del /q /s *.swp 2>nul

echo Cleaning coverage reports...
if exist "htmlcov" rd /s /q "htmlcov"
del /q /s .coverage 2>nul
del /q /s coverage.xml 2>nul

echo Cleaning test results...
if exist "test-results" rd /s /q "test-results"
if exist "playwright-report" rd /s /q "playwright-report"

echo.
echo ========================================
echo Cleanup complete!
echo ========================================
echo.
echo Note: The following were NOT removed:
echo   - poetry.lock (keep for reproducible builds)
echo   - package-lock.json (keep for reproducible builds)
echo   - .env files (contains your configuration)
echo.
