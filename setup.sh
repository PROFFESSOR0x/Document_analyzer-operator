#!/bin/bash
# Document Analyzer - Main Setup Script (Linux/Mac)
# This script calls the full setup automation

echo "========================================"
echo "Document Analyzer - Setup"
echo "========================================"
echo ""

cd "$(dirname "$0")/scripts/setup"

# Run the auto setup script
if [ -f "setup_auto.sh" ]; then
    chmod +x setup_auto.sh
    ./setup_auto.sh
elif [ -f "quick_setup.sh" ]; then
    chmod +x quick_setup.sh
    ./quick_setup.sh
else
    echo "Error: Setup script not found in scripts/setup/"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
