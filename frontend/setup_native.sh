#!/bin/bash
# Document Analyzer Operator - Frontend Native Setup Script (Linux/Mac)
# This script sets up the frontend for native (non-Docker) development

set -e

echo "============================================"
echo "Document Analyzer Operator - Frontend Setup"
echo "============================================"
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

# Check Node.js installation
check_nodejs() {
    log_info "Checking Node.js installation..."
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js 18 or higher."
        log_error "Download from: https://nodejs.org/"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    
    if [ "$NODE_VERSION" -lt 18 ]; then
        log_error "Node.js 18 or higher is required. Found: $(node --version)"
        exit 1
    fi
    
    log_info "Node.js version: $(node --version) ✓"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed"
        exit 1
    fi
    
    log_info "npm version: $(npm --version) ✓"
}

# Check nvm (optional but recommended)
check_nvm() {
    if command -v nvm &> /dev/null || [ -n "$NVM_DIR" ]; then
        log_info "nvm is available (recommended for managing Node versions)"
    else
        log_warn "nvm not found. Consider installing nvm for easier Node.js version management."
        log_warn "See: https://github.com/nvm-sh/nvm"
    fi
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    # Remove node_modules if exists for clean install
    if [ -d "node_modules" ]; then
        log_warn "Removing existing node_modules..."
        rm -rf node_modules
    fi
    
    # Install with npm
    npm install
    
    if [ $? -ne 0 ]; then
        log_error "Failed to install dependencies"
        exit 1
    fi
    
    log_info "Dependencies installed successfully ✓"
}

# Setup environment file
setup_env_file() {
    log_info "Setting up environment file..."
    
    if [ ! -f ".env.local" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env.local
            log_info "Created .env.local from .env.example"
            log_warn "Please review and update .env.local with your settings"
        else
            log_error ".env.example not found!"
            exit 1
        fi
    else
        log_warn ".env.local already exists. Skipping..."
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    # Check if Next.js can build
    if npm run type-check > /dev/null 2>&1; then
        log_info "TypeScript check passed ✓"
    else
        log_warn "TypeScript check has warnings. Review with: npm run type-check"
    fi
    
    # Check linting
    if npm run lint > /dev/null 2>&1; then
        log_info "Linting passed ✓"
    else
        log_warn "Linting has warnings. Review with: npm run lint"
    fi
    
    log_info "Verification complete ✓"
}

# Main execution
main() {
    check_nodejs
    check_nvm
    install_dependencies
    setup_env_file
    verify_installation
    
    echo ""
    echo "============================================"
    echo -e "${GREEN}Setup Complete!${NC}"
    echo "============================================"
    echo ""
    echo "To start the development server:"
    echo "  ./run_native.sh"
    echo ""
    echo "Or manually:"
    echo "  npm run dev"
    echo ""
    echo "To build for production:"
    echo "  npm run build"
    echo ""
    echo "To run tests:"
    echo "  npm run test"
    echo ""
    echo "============================================"
}

# Run main function
main "$@"
