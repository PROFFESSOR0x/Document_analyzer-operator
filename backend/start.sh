#!/bin/bash
# Quick start script for Document Analyzer Operator Backend

set -e

echo "=========================================="
echo "Document Analyzer Operator - Backend Setup"
echo "=========================================="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    echo "Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    echo "Please install Docker Desktop or docker-compose"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "IMPORTANT: Please edit .env and set:"
    echo "  - SECRET_KEY (generate a secure random key)"
    echo "  - Database credentials (if not using defaults)"
    echo ""
    read -p "Press Enter to continue with default settings..."
fi

# Start services
echo ""
echo "Starting Docker containers..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check health
echo ""
echo "Checking API health..."
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "✓ API is healthy!"
else
    echo "⚠ API may still be starting up. Check logs with: docker-compose logs -f backend"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Services:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - MinIO Console: http://localhost:9001"
echo ""
echo "Default Credentials:"
echo "  - PostgreSQL: postgres/postgres"
echo "  - MinIO: minioadmin/minioadmin"
echo ""
echo "Next Steps:"
echo "  1. Create a user account via POST /api/v1/auth/register"
echo "  2. Login via POST /api/v1/auth/login"
echo "  3. Start creating agents and workflows!"
echo ""
echo "Useful Commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Reset database: docker-compose down -v && docker-compose up -d"
echo ""
