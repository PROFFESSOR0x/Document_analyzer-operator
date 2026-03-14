#!/bin/bash
# Document Analyzer Operator - Backend Native Run Script (Linux/Mac)
# This script starts the backend server for native (non-Docker) development

set -e

echo "=========================================="
echo "Document Analyzer Operator - Backend"
echo "=========================================="
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

# Check if .env exists
check_env_file() {
    if [ ! -f ".env" ]; then
        log_error ".env file not found!"
        log_error "Please run setup_native.sh first or create .env from .env.example"
        exit 1
    fi
    log_info "Environment file loaded ✓"
}

# Check database connection
check_database() {
    log_info "Checking database connection..."
    
    # Source environment variables
    export $(grep -v '^#' .env | xargs)
    
    # Test database connection
    if poetry run python -c "import asyncio; from app.db.session import get_db; asyncio.run(get_db().__anext__())" 2>/dev/null; then
        log_info "Database connection successful ✓"
    else
        log_error "Database connection failed!"
        log_error "Please ensure PostgreSQL is running:"
        log_error "  Linux: sudo systemctl start postgresql"
        log_error "  Mac: brew services start postgresql@16"
        exit 1
    fi
}

# Check Redis connection
check_redis() {
    log_info "Checking Redis connection..."
    
    # Source environment variables
    export $(grep -v '^#' .env | xargs)
    
    if poetry run python -c "import redis; r = redis.Redis(host='$REDIS_HOST', port=$REDIS_PORT, db=$REDIS_DB); r.ping()" 2>/dev/null; then
        log_info "Redis connection successful ✓"
    else
        log_warn "Redis connection failed. Some features may not work."
        log_warn "Install and start Redis:"
        log_warn "  Linux: sudo systemctl start redis"
        log_warn "  Mac: brew services start redis"
    fi
}

# Health check function
health_check() {
    local max_retries=30
    local retry_count=0
    local port=${APP_PORT:-8000}
    
    log_info "Waiting for server to be ready..."
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s "http://localhost:$port/api/v1/health" > /dev/null 2>&1; then
            log_info "Server is healthy ✓"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        sleep 1
    done
    
    log_error "Health check failed after $max_retries seconds"
    return 1
}

# Graceful shutdown handler
cleanup() {
    echo ""
    log_info "Shutting down gracefully..."
    
    if [ ! -z "$SERVER_PID" ]; then
        kill -TERM $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
    fi
    
    log_info "Server stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main function
main() {
    check_env_file
    
    # Parse command line arguments
    RELOAD=false
    HOST="0.0.0.0"
    PORT="8000"
    WORKERS="1"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --reload)
                RELOAD=true
                shift
                ;;
            --host)
                HOST="$2"
                shift 2
                ;;
            --port)
                PORT="$2"
                shift 2
                ;;
            --workers)
                WORKERS="$2"
                shift 2
                ;;
            --no-check)
                SKIP_CHECKS=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Usage: $0 [--reload] [--host HOST] [--port PORT] [--workers N] [--no-check]"
                exit 1
                ;;
        esac
    done
    
    # Run checks unless skipped
    if [ "$SKIP_CHECKS" != "true" ]; then
        check_database
        check_redis
    fi
    
    # Load environment variables
    export $(grep -v '^#' .env | xargs)
    
    # Start the server
    log_info "Starting Uvicorn server on $HOST:$PORT..."
    log_info "API Documentation: http://localhost:$PORT/docs"
    log_info "ReDoc: http://localhost:$PORT/redoc"
    echo ""
    
    if [ "$RELOAD" = true ]; then
        log_info "Running in development mode with auto-reload"
        poetry run uvicorn app.main:app \
            --host $HOST \
            --port $PORT \
            --reload \
            --log-level info &
    else
        log_info "Running in production mode with $WORKERS workers"
        poetry run uvicorn app.main:app \
            --host $HOST \
            --port $PORT \
            --workers $WORKERS \
            --log-level info &
    fi
    
    SERVER_PID=$!
    
    # Wait for server to start
    sleep 2
    
    # Run health check
    if ! health_check; then
        log_error "Server failed to start. Check logs for details."
        exit 1
    fi
    
    # Wait for server process
    wait $SERVER_PID
}

# Run main function
main "$@"
