#!/bin/bash
# =============================================================================
# Document Analyzer Operator - Quick Setup Script (Linux/Mac)
# =============================================================================
# This script automates the complete setup process:
# 1. Check prerequisites (Python, Node.js, PostgreSQL, Redis)
# 2. Generate backend .env file
# 3. Generate frontend .env.local file
# 4. Install backend dependencies
# 5. Install frontend dependencies
# 6. Run database migrations
# 7. Validate setup
# 8. Show success message with next steps
# =============================================================================

set -e

echo "============================================================================="
echo "Document Analyzer Operator - Quick Setup (Linux/Mac)"
echo "============================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP $1/8]${NC} $2"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# =============================================================================
# Check Prerequisites
# =============================================================================
log_step 1 "Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed"
    log_error "Install Python 3.11+: https://www.python.org/downloads/"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_info "Python found: $PYTHON_VERSION"

# Check Node.js
if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed"
    log_error "Install Node.js 18+: https://nodejs.org/"
    exit 1
fi
NODE_VERSION=$(node --version)
log_info "Node.js found: $NODE_VERSION"

# Check Git
if ! command -v git &> /dev/null; then
    log_error "Git is not installed"
    log_error "Install Git: https://git-scm.com/downloads"
    exit 1
fi
log_info "Git found"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    log_warn "PostgreSQL not found in PATH"
    log_warn "Install PostgreSQL 16+: https://www.postgresql.org/download/"
    log_warn "Database migrations may fail until PostgreSQL is installed"
else
    log_info "PostgreSQL found"
fi

# Check Redis
if ! command -v redis-cli &> /dev/null; then
    log_warn "Redis not found in PATH"
    log_warn "Install Redis: https://redis.io/download/"
    log_warn "Redis features will be unavailable until Redis is installed"
else
    log_info "Redis found"
fi

echo ""

# =============================================================================
# Generate Backend Environment
# =============================================================================
log_step 2 "Generating backend environment..."
echo ""

cd "$SCRIPT_DIR/backend"

if [ -f ".env" ]; then
    log_info ".env file already exists"
    read -p "Overwrite existing .env? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 scripts/generate_env.py --force
        if [ $? -ne 0 ]; then
            log_error "Failed to generate backend .env"
            exit 1
        fi
    fi
else
    python3 scripts/generate_env.py
    if [ $? -ne 0 ]; then
        log_error "Failed to generate backend .env"
        exit 1
    fi
fi

cd "$SCRIPT_DIR"
echo ""

# =============================================================================
# Generate Frontend Environment
# =============================================================================
log_step 3 "Generating frontend environment..."
echo ""

cd "$SCRIPT_DIR/frontend"

if [ -f ".env.local" ]; then
    log_info ".env.local file already exists"
    read -p "Overwrite existing .env.local? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        node scripts/generate_env.js --force
        if [ $? -ne 0 ]; then
            log_error "Failed to generate frontend .env.local"
            exit 1
        fi
    fi
else
    node scripts/generate_env.js
    if [ $? -ne 0 ]; then
        log_error "Failed to generate frontend .env.local"
        exit 1
    fi
fi

cd "$SCRIPT_DIR"
echo ""

# =============================================================================
# Install Backend Dependencies
# =============================================================================
log_step 4 "Installing backend dependencies..."
echo ""

cd "$SCRIPT_DIR/backend"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    log_info "Poetry not found, installing..."
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add poetry to PATH
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v poetry &> /dev/null; then
        log_error "Poetry installation failed"
        log_error "Install manually: https://python-poetry.org/docs/"
        exit 1
    fi
fi

poetry install
if [ $? -ne 0 ]; then
    log_error "Failed to install backend dependencies"
    exit 1
fi

cd "$SCRIPT_DIR"
echo ""

# =============================================================================
# Install Frontend Dependencies
# =============================================================================
log_step 5 "Installing frontend dependencies..."
echo ""

cd "$SCRIPT_DIR/frontend"

npm install
if [ $? -ne 0 ]; then
    log_error "Failed to install frontend dependencies"
    exit 1
fi

cd "$SCRIPT_DIR"
echo ""

# =============================================================================
# Run Database Migrations
# =============================================================================
log_step 6 "Running database migrations..."
echo ""

cd "$SCRIPT_DIR/backend"

# Try to run migrations (may fail if DB not ready)
if poetry run alembic upgrade head 2>/dev/null; then
    log_info "Database migrations completed"
else
    log_warn "Database migrations failed"
    log_warn "This is expected if PostgreSQL is not running yet"
    log_warn "You can run migrations later with: cd backend && poetry run alembic upgrade head"
fi

cd "$SCRIPT_DIR"
echo ""

# =============================================================================
# Validate Setup
# =============================================================================
log_step 7 "Validating setup..."
echo ""

if python3 scripts/validate_env.py; then
    log_info "Environment validation passed"
else
    log_warn "Environment validation found issues"
    log_warn "Review the validation output above"
fi

echo ""

# =============================================================================
# Summary
# =============================================================================
log_step 8 "Setup Summary"
echo ""
echo "============================================================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "============================================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the backend:"
echo "   cd backend"
echo "   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. Start the frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "4. Configure LLM API keys (optional):"
echo "   Edit backend/.env and add your API keys:"
echo "   - OPENAI_API_KEY"
echo "   - ANTHROPIC_API_KEY"
echo "   - GROQ_API_KEY"
echo ""
echo "============================================================================="
echo ""
