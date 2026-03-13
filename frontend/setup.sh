#!/bin/bash

echo "Document Analyzer Operator - Frontend Setup"
echo "==========================================="
echo ""

echo "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed. Please install Node.js 20 or higher."
    exit 1
fi

echo "Node.js found: $(node --version)"
echo ""

echo "Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Dependencies installed successfully!"
echo ""

echo "Copying environment file..."
if [ ! -f .env.local ]; then
    cp .env.example .env.local
    echo ".env.local created. Please update with your settings."
else
    echo ".env.local already exists."
fi

echo ""
echo "==========================================="
echo "Setup complete!"
echo ""
echo "To start the development server:"
echo "  npm run dev"
echo ""
echo "To build for production:"
echo "  npm run build"
echo ""
echo "To run tests:"
echo "  npm run test"
echo ""
echo "==========================================="
