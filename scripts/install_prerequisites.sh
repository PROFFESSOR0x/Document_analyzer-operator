#!/bin/bash
# Document Analyzer Operator - Prerequisites Installer (Linux/Mac)
# This script installs all system dependencies needed for native deployment

set -e

echo "================================================"
echo "Document Analyzer Operator - Prerequisites Installer"
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

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v dnf &> /dev/null; then
            PACKAGE_MANAGER="dnf"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
        elif command -v pacman &> /dev/null; then
            PACKAGE_MANAGER="pacman"
        elif command -v zypper &> /dev/null; then
            PACKAGE_MANAGER="zypper"
        else
            log_error "Unsupported Linux package manager"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    log_info "Detected OS: $OS ($PACKAGE_MANAGER)"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ] && [ "$OS" == "linux" ]; then
        log_warn "This script should be run as root or with sudo"
        log_warn "Re-running with sudo..."
        exec sudo "$0" "$@"
    fi
}

# Install Git
install_git() {
    log_info "Checking Git..."
    
    if command -v git &> /dev/null; then
        log_info "Git is already installed: $(git --version)"
        return
    fi
    
    log_info "Installing Git..."
    case $PACKAGE_MANAGER in
        apt)
            apt-get update && apt-get install -y git
            ;;
        dnf|yum)
            $PACKAGE_MANAGER install -y git
            ;;
        pacman)
            pacman -Sy --noconfirm git
            ;;
        zypper)
            zypper install -y git
            ;;
        brew)
            brew install git
            ;;
    esac
    
    log_info "Git installed: $(git --version)"
}

# Install Python 3.11+
install_python() {
    log_info "Checking Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        REQUIRED_VERSION="3.11"
        
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" == "$REQUIRED_VERSION" ]; then
            log_info "Python is already installed: $PYTHON_VERSION"
            return
        fi
        
        log_warn "Python version $PYTHON_VERSION is below 3.11"
    fi
    
    log_info "Installing Python 3.11+..."
    case $PACKAGE_MANAGER in
        apt)
            apt-get update
            apt-get install -y software-properties-common
            add-apt-repository -y ppa:deadsnakes/ppa
            apt-get update && apt-get install -y python3.11 python3.11-venv python3.11-dev
            ;;
        dnf|yum)
            $PACKAGE_MANAGER install -y python3.11 python3.11-pip
            ;;
        pacman)
            pacman -Sy --noconfirm python
            ;;
        zypper)
            zypper install -y python311
            ;;
        brew)
            brew install python@3.11
            ;;
    esac
    
    log_info "Python installed: $(python3 --version)"
}

# Install Poetry
install_poetry() {
    log_info "Checking Poetry..."
    
    if command -v poetry &> /dev/null; then
        log_info "Poetry is already installed: $(poetry --version)"
        return
    fi
    
    log_info "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add to PATH
    export PATH="$HOME/.local/bin:$PATH"
    
    if command -v poetry &> /dev/null; then
        log_info "Poetry installed: $(poetry --version)"
    else
        log_error "Poetry installation failed"
        exit 1
    fi
}

# Install Node.js 18+
install_nodejs() {
    log_info "Checking Node.js..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        
        if [ "$NODE_VERSION" -ge 18 ]; then
            log_info "Node.js is already installed: $(node --version)"
            return
        fi
        
        log_warn "Node.js version $NODE_VERSION is below 18"
    fi
    
    log_info "Installing Node.js 18+..."
    case $PACKAGE_MANAGER in
        apt)
            curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
            apt-get install -y nodejs
            ;;
        dnf|yum)
            curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
            $PACKAGE_MANAGER install -y nodejs
            ;;
        pacman)
            pacman -Sy --noconfirm nodejs npm
            ;;
        zypper)
            zypper install -y nodejs20 npm20
            ;;
        brew)
            brew install node@20
            ;;
    esac
    
    log_info "Node.js installed: $(node --version)"
}

# Install PostgreSQL 16+
install_postgresql() {
    log_info "Checking PostgreSQL..."
    
    if command -v psql &> /dev/null; then
        PG_VERSION=$(psql --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
        PG_MAJOR=$(echo $PG_VERSION | cut -d'.' -f1)
        
        if [ "$PG_MAJOR" -ge 16 ]; then
            log_info "PostgreSQL is already installed: $PG_VERSION"
            return
        fi
        
        log_warn "PostgreSQL version $PG_VERSION is below 16"
    fi
    
    log_info "Installing PostgreSQL 16+..."
    case $PACKAGE_MANAGER in
        apt)
            wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
            echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list
            apt-get update && apt-get install -y postgresql-16 postgresql-contrib-16 postgresql-client-16 postgresql-server-dev-16
            ;;
        dnf|yum)
            $PACKAGE_MANAGER install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-$($PACKAGE_MANAGER --version | grep -oP '\d+' | head -1)-x86_64/pgdg-redhat-repo-latest.noarch.rpm
            $PACKAGE_MANAGER install -y postgresql16 postgresql16-server postgresql16-contrib postgresql16-devel
            ;;
        pacman)
            pacman -Sy --noconfirm postgresql
            ;;
        zypper)
            zypper install -y postgresql postgresql-server postgresql-devel
            ;;
        brew)
            brew install postgresql@16
            ;;
    esac
    
    log_info "PostgreSQL installed: $(psql --version)"
}

# Install Redis 7+
install_redis() {
    log_info "Checking Redis..."
    
    if command -v redis-server &> /dev/null; then
        REDIS_VERSION=$(redis-server --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        REDIS_MAJOR=$(echo $REDIS_VERSION | cut -d'.' -f1)
        
        if [ "$REDIS_MAJOR" -ge 7 ]; then
            log_info "Redis is already installed: $REDIS_VERSION"
            return
        fi
    fi
    
    log_info "Installing Redis 7+..."
    case $PACKAGE_MANAGER in
        apt)
            apt-get update && apt-get install -y redis-server
            ;;
        dnf|yum)
            $PACKAGE_MANAGER install -y redis
            ;;
        pacman)
            pacman -Sy --noconfirm redis
            ;;
        zypper)
            zypper install -y redis
            ;;
        brew)
            brew install redis
            ;;
    esac
    
    if command -v redis-server &> /dev/null; then
        log_info "Redis installed: $(redis-server --version)"
    else
        log_warn "Redis installation may have failed"
    fi
}

# Install additional build tools
install_build_tools() {
    log_info "Installing build tools..."
    
    case $PACKAGE_MANAGER in
        apt)
            apt-get update && apt-get install -y build-essential libpq-dev libssl-dev libffi-dev
            ;;
        dnf|yum)
            $PACKAGE_MANAGER groupinstall -y "Development Tools"
            $PACKAGE_MANAGER install -y postgresql-devel openssl-devel libffi-devel
            ;;
        pacman)
            pacman -Sy --noconfirm base-devel postgresql-libs openssl libffi
            ;;
        zypper)
            zypper install -y -t pattern devel_basis
            zypper install -y postgresql-devel libopenssl-devel libffi-devel
            ;;
        brew)
            brew install postgresql openssl libffi
            ;;
    esac
    
    log_info "Build tools installed"
}

# Start services
start_services() {
    log_info "Starting services..."
    
    # Start PostgreSQL
    if command -v systemctl &> /dev/null; then
        systemctl start postgresql || true
        systemctl enable postgresql || true
        log_info "PostgreSQL service started"
    elif [ "$OS" == "macos" ]; then
        brew services start postgresql@16 || true
        log_info "PostgreSQL service started"
    fi
    
    # Start Redis
    if command -v systemctl &> /dev/null; then
        systemctl start redis || true
        systemctl enable redis || true
        log_info "Redis service started"
    elif [ "$OS" == "macos" ]; then
        brew services start redis || true
        log_info "Redis service started"
    fi
}

# Print summary
print_summary() {
    echo ""
    echo "================================================"
    echo -e "${GREEN}Prerequisites Installation Complete!${NC}"
    echo "================================================"
    echo ""
    echo "Installed components:"
    echo "  - Git: $(git --version 2>/dev/null || echo 'Not found')"
    echo "  - Python: $(python3 --version 2>/dev/null || echo 'Not found')"
    echo "  - Poetry: $(poetry --version 2>/dev/null || echo 'Not found')"
    echo "  - Node.js: $(node --version 2>/dev/null || echo 'Not found')"
    echo "  - npm: $(npm --version 2>/dev/null || echo 'Not found')"
    echo "  - PostgreSQL: $(psql --version 2>/dev/null || echo 'Not found')"
    echo "  - Redis: $(redis-server --version 2>/dev/null || echo 'Not found')"
    echo ""
    echo "Next steps:"
    echo "  1. Run: ./setup.sh"
    echo "  2. Configure database credentials in backend/.env"
    echo "  3. Start services: ./start.sh"
    echo ""
    echo "================================================"
}

# Main execution
main() {
    detect_os
    check_root
    
    install_git
    install_python
    install_poetry
    install_nodejs
    install_postgresql
    install_redis
    install_build_tools
    start_services
    
    print_summary
}

# Run main function
main "$@"
