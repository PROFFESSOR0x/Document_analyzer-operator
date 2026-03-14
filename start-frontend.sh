#!/bin/bash
# Document Analyzer - Start Frontend (Linux/Mac)
# This script starts the frontend development server

echo "========================================"
echo "Document Analyzer - Starting Frontend"
echo "========================================"
echo ""

cd "$(dirname "$0")/scripts/run"

# Run the frontend start script
if [ -f "run_frontend.sh" ]; then
    chmod +x run_frontend.sh
    ./run_frontend.sh
else
    echo "Error: Frontend start script not found in scripts/run/"
    exit 1
fi
