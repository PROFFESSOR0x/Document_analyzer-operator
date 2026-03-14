#!/bin/bash
# Document Analyzer - Start Backend (Linux/Mac)
# This script starts the backend server

echo "========================================"
echo "Document Analyzer - Starting Backend"
echo "========================================"
echo ""

cd "$(dirname "$0")/scripts/run"

# Run the backend start script
if [ -f "run_backend.sh" ]; then
    chmod +x run_backend.sh
    ./run_backend.sh
else
    echo "Error: Backend start script not found in scripts/run/"
    exit 1
fi
