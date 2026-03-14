#!/bin/bash
# Document Analyzer - Cleanup Script (Linux/Mac)
# This script removes temporary files and build caches

echo "========================================"
echo "Document Analyzer - Cleanup"
echo "========================================"
echo ""

cd "$(dirname "$0")/scripts/maintenance"

# Run the cleanup script
if [ -f "cleanup.sh" ]; then
    chmod +x cleanup.sh
    ./cleanup.sh
else
    echo "Error: Cleanup script not found in scripts/maintenance/"
    exit 1
fi
