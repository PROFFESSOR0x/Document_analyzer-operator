#!/bin/bash
# Document Analyzer Operator - Backend Native Setup Script (Linux/Mac)
# This script sets up the backend for native (non-Docker) development

set -e

echo "=========================================="
echo "Document Analyzer Operator - Backend Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
check_python_version() {
    log_info "Checking Python version..."
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.11 or higher."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.11"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        log_error "Python 3.11 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    log_info "Python version: $PYTHON_VERSION ✓"
}

# Check and install Poetry
setup_poetry() {
    log_info "Checking Poetry installation..."
    if ! command -v poetry &> /dev/null; then
        log_warn "Poetry not found. Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        
        # Add poetry to PATH
        export PATH="$HOME/.local/bin:$PATH"
        
        if ! command -v poetry &> /dev/null; then
            log_error "Poetry installation failed. Please install manually."
            exit 1
        fi
        log_info "Poetry installed successfully ✓"
    else
        POETRY_VERSION=$(poetry --version | cut -d' ' -f3)
        log_info "Poetry version: $POETRY_VERSION ✓"
    fi
}

# Create virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    if [ -d ".venv" ]; then
        log_warn "Virtual environment already exists. Recreating..."
        rm -rf .venv
    fi
    
    poetry install --no-root
    log_info "Virtual environment created and dependencies installed ✓"
}

# Setup environment file
setup_env_file() {
    log_info "Setting up environment file..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_info "Created .env file from .env.example"
            
            # Generate secure random keys
            log_info "Generating secure random keys..."
            
            # Generate SECRET_KEY
            SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
            sed -i.bak "s/your-super-secret-key-change-this-in-production-min-32-chars/$SECRET_KEY/" .env
            rm -f .env.bak
            
            # Generate ENCRYPTION_KEY
            ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
            sed -i.bak "s/ENCRYPTION_KEY=/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
            rm -f .env.bak
            
            log_info "Secure keys generated ✓"
        else
            log_error ".env.example not found!"
            exit 1
        fi
    else
        log_warn ".env file already exists. Skipping..."
    fi
}

# Check database connectivity
check_database() {
    log_info "Checking database connectivity..."
    
    # Source environment variables
    export $(grep -v '^#' .env | xargs)
    
    # Wait for PostgreSQL to be ready
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if python3 -c "import psycopg2; psycopg2.connect(host='$POSTGRES_HOST', port=$POSTGRES_PORT, user='$POSTGRES_USER', password='$POSTGRES_PASSWORD', dbname='$POSTGRES_DB')" 2>/dev/null; then
            log_info "Database connection successful ✓"
            return 0
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        log_warn "Database not ready. Retrying in 2 seconds... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done
    
    log_error "Database connection failed after $MAX_RETRIES attempts."
    log_error "Please ensure PostgreSQL is running and credentials are correct."
    exit 1
}

# Check Redis connectivity
check_redis() {
    log_info "Checking Redis connectivity..."
    
    # Source environment variables
    export $(grep -v '^#' .env | xargs)
    
    if python3 -c "import redis; r = redis.Redis(host='$REDIS_HOST', port=$REDIS_PORT, db=$REDIS_DB); r.ping()" 2>/dev/null; then
        log_info "Redis connection successful ✓"
    else
        log_warn "Redis connection failed. Please ensure Redis is running."
        log_warn "Install Redis: sudo apt-get install redis-server (Linux) or brew install redis (Mac)"
    fi
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    poetry run alembic upgrade head
    
    if [ $? -eq 0 ]; then
        log_info "Database migrations completed successfully ✓"
    else
        log_error "Database migrations failed!"
        exit 1
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    # Check if main app can be imported
    if poetry run python -c "from app.main import app" 2>/dev/null; then
        log_info "Application import successful ✓"
    else
        log_error "Application import failed!"
        exit 1
    fi
}

# Main execution
main() {
    check_python_version
    setup_poetry
    setup_venv
    setup_env_file
    run_migrations
    check_database
    check_redis
    verify_installation
    
    echo ""
    echo "=========================================="
    echo -e "${GREEN}Setup Complete!${NC}"
    echo "=========================================="
    echo ""
    echo "To start the backend server:"
    echo "  ./run_native.sh"
    echo ""
    echo "Or manually:"
    echo "  poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "API Documentation: http://localhost:8000/docs"
    echo ""
    echo "=========================================="
}

# Run main function
main "$@"
