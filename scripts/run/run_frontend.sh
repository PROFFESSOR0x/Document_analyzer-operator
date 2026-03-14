#!/bin/bash
# Start Frontend Development Server

echo "Starting Document Analyzer Frontend..."

cd "$(dirname "$0")/../.."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start development server
npm run dev
