#!/bin/bash
# Document Analyzer - Cleanup Script (Linux/Mac)
# Clean temporary files and build caches

echo "========================================"
echo "Document Analyzer - Cleanup"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$ROOT_DIR"

echo "Cleaning Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null

echo "Cleaning node_modules..."
rm -rf frontend/node_modules 2>/dev/null

echo "Cleaning build caches..."
rm -rf frontend/.next 2>/dev/null
rm -rf backend/.pytest_cache 2>/dev/null
rm -rf backend/.mypy_cache 2>/dev/null
rm -rf .pytest_cache 2>/dev/null
rm -rf .mypy_cache 2>/dev/null

echo "Cleaning logs..."
find . -type f -name "*.log" -delete 2>/dev/null

echo "Cleaning temporary files..."
find . -type f -name "*.tmp" -delete 2>/dev/null
find . -type f -name "*.bak" -delete 2>/dev/null
find . -type f -name "*.swp" -delete 2>/dev/null

echo "Cleaning coverage reports..."
rm -rf htmlcov/ 2>/dev/null
rm -rf .coverage 2>/dev/null
rm -rf coverage.xml 2>/dev/null

echo "Cleaning test results..."
rm -rf test-results/ 2>/dev/null
rm -rf playwright-report/ 2>/dev/null

echo ""
echo "========================================"
echo "Cleanup complete!"
echo "========================================"
echo ""
echo "Note: The following were NOT removed:"
echo "  - poetry.lock (keep for reproducible builds)"
echo "  - package-lock.json (keep for reproducible builds)"
echo "  - .env files (contains your configuration)"
echo ""
