#!/bin/bash
# Document Analyzer Operator - Root Setup Script (Linux/Mac)
# This script sets up both backend and frontend for native (non-Docker) development
# Updated to integrate with automated environment generators

set -e

echo "================================================"
echo "Document Analyzer Operator - Complete Setup"
echo "================================================"
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

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        log_error "Install Python 3.11+: https://www.python.org/downloads/"
        exit 1
    fi

    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        log_error "Install Node.js 18+: https://nodejs.org/"
        exit 1
    fi

    # Check Git
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        log_error "Install Git: https://git-scm.com/downloads"
        exit 1
    fi

    log_info "Prerequisites check passed ✓"
}

# Generate or update environment files
generate_env_files() {
    echo ""
    echo "================================================"
    echo "Environment Configuration"
    echo "================================================"
    
    # Check if .env files exist
    BACKEND_ENV_EXISTS=false
    FRONTEND_ENV_EXISTS=false
    
    if [ -f "$SCRIPT_DIR/backend/.env" ]; then
        BACKEND_ENV_EXISTS=true
    fi
    
    if [ -f "$SCRIPT_DIR/frontend/.env.local" ]; then
        FRONTEND_ENV_EXISTS=true
    fi
    
    # Ask if user wants to regenerate
    if [ "$BACKEND_ENV_EXISTS" = true ] || [ "$FRONTEND_ENV_EXISTS" = true ]; then
        echo ""
        log_warn "Environment files already exist."
        read -p "Regenerate environment files? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Regenerate backend .env
            if [ "$BACKEND_ENV_EXISTS" = true ]; then
                log_info "Regenerating backend .env..."
                cd "$SCRIPT_DIR/backend"
                python3 scripts/generate_env.py --force
                cd "$SCRIPT_DIR"
            fi
            
            # Regenerate frontend .env.local
            if [ "$FRONTEND_ENV_EXISTS" = true ]; then
                log_info "Regenerating frontend .env.local..."
                cd "$SCRIPT_DIR/frontend"
                node scripts/generate_env.js --force
                cd "$SCRIPT_DIR"
            fi
        else
            log_info "Keeping existing environment files"
        fi
    else
        # Generate new environment files
        log_info "Generating environment files..."
        
        # Generate backend .env
        cd "$SCRIPT_DIR/backend"
        python3 scripts/generate_env.py
        cd "$SCRIPT_DIR"
        
        # Generate frontend .env.local
        cd "$SCRIPT_DIR/frontend"
        node scripts/generate_env.js
        cd "$SCRIPT_DIR"
    fi
}

# Setup backend
setup_backend() {
    echo ""
    echo "================================================"
    echo "Setting up Backend"
    echo "================================================"

    cd "$SCRIPT_DIR/backend"

    if [ -f "setup_native.sh" ]; then
        chmod +x setup_native.sh
        # Skip env file creation in backend setup since we already did it
        ./setup_native.sh
    else
        log_error "Backend setup script not found!"
        exit 1
    fi

    cd "$SCRIPT_DIR"
}

# Setup frontend
setup_frontend() {
    echo ""
    echo "================================================"
    echo "Setting up Frontend"
    echo "================================================"

    cd "$SCRIPT_DIR/frontend"

    if [ -f "setup_native.sh" ]; then
        chmod +x setup_native.sh
        # Skip env file creation in frontend setup since we already did it
        ./setup_native.sh
    else
        log_error "Frontend setup script not found!"
        exit 1
    fi

    cd "$SCRIPT_DIR"
}

# Create logs directory
setup_logs() {
    log_info "Creating logs directory..."

    if [ ! -d "logs" ]; then
        mkdir -p logs
    fi

    log_info "Logs directory created ✓"
}

# Validate setup
validate_setup() {
    echo ""
    echo "================================================"
    echo "Validating Setup"
    echo "================================================"
    
    if [ -f "$SCRIPT_DIR/scripts/validate_env.py" ]; then
        python3 "$SCRIPT_DIR/scripts/validate_env.py" || {
            log_warn "Environment validation found issues"
            log_warn "Review the validation output above"
        }
    else
        log_info "Validation script not found, skipping validation"
    fi
}

# Main execution
main() {
    check_prerequisites
    setup_logs
    generate_env_files
    setup_backend
    setup_frontend
    validate_setup

    echo ""
    echo "================================================"
    echo -e "${GREEN}Complete Setup Finished!${NC}"
    echo "================================================"
    echo ""
    echo "To start all services:"
    echo "  ./start.sh"
    echo ""
    echo "To start individual services:"
    echo "  Backend:  cd backend && ./run_native.sh"
    echo "  Frontend: cd frontend && ./run_native.sh"
    echo ""
    echo "To stop all services:"
    echo "  ./stop.sh"
    echo ""
    echo "Documentation:"
    echo "  - API: http://localhost:8000/docs"
    echo "  - Frontend: http://localhost:3000"
    echo ""
    echo "================================================"
}

# Run main function
main "$@"
