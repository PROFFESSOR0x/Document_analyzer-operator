#!/bin/bash
# Document Analyzer Operator - Redis Setup Script (Linux/Mac)
# This script installs and configures Redis for the application

set -e

echo "================================================"
echo "Document Analyzer Operator - Redis Setup"
echo "================================================"
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

# Configuration
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"
REDIS_BIND="${REDIS_BIND:-127.0.0.1}"

# Check if Redis is installed
check_redis() {
    log_info "Checking Redis installation..."
    
    if command -v redis-server &> /dev/null; then
        REDIS_VERSION=$(redis-server --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        log_info "Redis is installed: $REDIS_VERSION"
    else
        log_error "Redis is not installed"
        log_error "Install Redis:"
        log_error "  Linux: sudo apt-get install redis-server"
        log_error "  Mac: brew install redis"
        exit 1
    fi
}

# Check if Redis is running
check_redis_running() {
    log_info "Checking if Redis is running..."
    
    if redis-cli -p "$REDIS_PORT" ping > /dev/null 2>&1; then
        log_info "Redis is running on port $REDIS_PORT ✓"
        return 0
    else
        log_warn "Redis is not running"
        return 1
    fi
}

# Install Redis (Linux)
install_redis_linux() {
    log_info "Installing Redis..."
    
    if command -v apt-get &> /dev/null; then
        apt-get update && apt-get install -y redis-server
    elif command -v dnf &> /dev/null; then
        dnf install -y redis
    elif command -v yum &> /dev/null; then
        yum install -y redis
    elif command -v pacman &> /dev/null; then
        pacman -Sy --noconfirm redis
    else
        log_error "Unsupported package manager"
        exit 1
    fi
    
    log_info "Redis installed ✓"
}

# Install Redis (Mac)
install_redis_mac() {
    log_info "Installing Redis..."
    
    if ! command -v brew &> /dev/null; then
        log_error "Homebrew is not installed"
        log_error "Install Homebrew: https://brew.sh/"
        exit 1
    fi
    
    brew install redis
    log_info "Redis installed ✓"
}

# Configure Redis
configure_redis() {
    log_info "Configuring Redis..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    REDIS_CONFIG_DIR=""
    
    # Find Redis config directory
    if [ -f "/etc/redis/redis.conf" ]; then
        REDIS_CONFIG_DIR="/etc/redis"
    elif [ -f "/etc/redis.conf" ]; then
        REDIS_CONFIG_DIR="/etc"
    elif [ -f "/usr/local/etc/redis.conf" ]; then
        REDIS_CONFIG_DIR="/usr/local/etc"
    else
        log_warn "Redis config directory not found"
        return
    fi
    
    # Backup original config
    if [ -f "$REDIS_CONFIG_DIR/redis.conf" ]; then
        cp "$REDIS_CONFIG_DIR/redis.conf" "$REDIS_CONFIG_DIR/redis.conf.backup.$(date +%Y%m%d)"
        log_info "Backed up Redis config ✓"
    fi
    
    # Update configuration
    if [ -f "$REDIS_CONFIG_DIR/redis.conf" ]; then
        # Bind to localhost
        sed -i.bak "s/^bind .*/bind $REDIS_BIND/" "$REDIS_CONFIG_DIR/redis.conf" 2>/dev/null || true
        rm -f "$REDIS_CONFIG_DIR/redis.conf.bak"
        
        # Set port
        sed -i.bak "s/^port .*/port $REDIS_PORT/" "$REDIS_CONFIG_DIR/redis.conf" 2>/dev/null || true
        rm -f "$REDIS_CONFIG_DIR/redis.conf.bak"
        
        # Enable persistence
        sed -i.bak "s/^appendonly .*/appendonly yes/" "$REDIS_CONFIG_DIR/redis.conf" 2>/dev/null || true
        rm -f "$REDIS_CONFIG_DIR/redis.conf.bak"
        
        log_info "Redis configuration updated ✓"
    fi
    
    # Copy custom config if exists
    if [ -f "$SCRIPT_DIR/redis_config.conf" ]; then
        cp "$SCRIPT_DIR/redis_config.conf" "$REDIS_CONFIG_DIR/redis.conf.d/document-analyzer.conf" 2>/dev/null || true
        log_info "Custom Redis config copied ✓"
    fi
}

# Start Redis service
start_redis() {
    log_info "Starting Redis service..."
    
    if command -v systemctl &> /dev/null; then
        systemctl start redis-server || systemctl start redis
        systemctl enable redis-server || systemctl enable redis
        log_info "Redis service started and enabled ✓"
    elif command -v brew &> /dev/null; then
        brew services start redis
        log_info "Redis service started ✓"
    else
        log_warn "Could not start Redis service automatically"
        log_warn "Start Redis manually: redis-server"
    fi
}

# Test Redis connection
test_redis() {
    log_info "Testing Redis connection..."
    
    if redis-cli -p "$REDIS_PORT" ping | grep -q "PONG"; then
        log_info "Redis connection test passed ✓"
        
        # Get Redis info
        REDIS_INFO=$(redis-cli -p "$REDIS_PORT" INFO server | grep -E "redis_version|os|gcc_version" | cut -d: -f2 | tr '\n' ' ')
        log_info "Redis info: $REDIS_INFO"
    else
        log_error "Redis connection test failed"
        exit 1
    fi
}

# Generate Redis URL
generate_redis_url() {
    echo ""
    echo "================================================"
    echo "Redis Configuration"
    echo "================================================"
    echo ""
    
    if [ -n "$REDIS_PASSWORD" ]; then
        echo "Redis URL:"
        echo "  redis://:$REDIS_PASSWORD@localhost:$REDIS_PORT/0"
        echo ""
        echo "Update your .env file with:"
        echo "  REDIS_HOST=localhost"
        echo "  REDIS_PORT=$REDIS_PORT"
        echo "  REDIS_PASSWORD=$REDIS_PASSWORD"
        echo "  REDIS_URL=redis://:$REDIS_PASSWORD@localhost:$REDIS_PORT/0"
    else
        echo "Redis URL:"
        echo "  redis://localhost:$REDIS_PORT/0"
        echo ""
        echo "Update your .env file with:"
        echo "  REDIS_HOST=localhost"
        echo "  REDIS_PORT=$REDIS_PORT"
        echo "  REDIS_URL=redis://localhost:$REDIS_PORT/0"
    fi
    
    echo ""
    echo "================================================"
}

# Main execution
main() {
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    check_redis
    
    if ! check_redis_running; then
        if [ "$OS" == "linux" ]; then
            install_redis_linux
        elif [ "$OS" == "macos" ]; then
            install_redis_mac
        fi
        
        configure_redis
        start_redis
    fi
    
    test_redis
    generate_redis_url
    
    log_info "Redis setup complete!"
}

# Run main function
main "$@"
