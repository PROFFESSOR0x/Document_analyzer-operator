#!/bin/bash
# Document Analyzer Operator - Frontend Native Run Script (Linux/Mac)
# This script starts the frontend server for native (non-Docker) development

set -e

echo "============================================"
echo "Document Analyzer Operator - Frontend"
echo "============================================"
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

# Check if .env.local exists
check_env_file() {
    if [ ! -f ".env.local" ]; then
        log_error ".env.local file not found!"
        log_error "Please run setup_native.sh first or create .env.local from .env.example"
        exit 1
    fi
    log_info "Environment file loaded ✓"
}

# Check if backend is running
check_backend() {
    log_info "Checking backend connectivity..."
    
    # Source environment variables
    export $(grep -v '^#' .env.local | grep -v '^#' | xargs)
    
    BACKEND_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"
    
    MAX_RETRIES=5
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -s "$BACKEND_URL/api/v1/health" > /dev/null 2>&1; then
            log_info "Backend is healthy at $BACKEND_URL ✓"
            return 0
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        log_warn "Backend not ready. Retrying... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done
    
    log_warn "Backend is not responding at $BACKEND_URL"
    log_warn "Some features may not work until backend is started"
    log_warn "Start backend with: cd ../backend && ./run_native.sh"
}

# Health check function
health_check() {
    local max_retries=30
    local retry_count=0
    local port=3000
    
    log_info "Waiting for frontend server to be ready..."
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s "http://localhost:$port" > /dev/null 2>&1; then
            log_info "Frontend server is ready ✓"
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
    MODE="dev"
    PORT="3000"
    SKIP_BACKEND_CHECK=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --build)
                MODE="build"
                shift
                ;;
            --start)
                MODE="start"
                shift
                ;;
            --port)
                PORT="$2"
                shift 2
                ;;
            --no-backend-check)
                SKIP_BACKEND_CHECK=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Usage: $0 [--dev|--build|--start] [--port PORT] [--no-backend-check]"
                exit 1
                ;;
        esac
    done
    
    # Check backend connectivity unless skipped
    if [ "$SKIP_BACKEND_CHECK" != "true" ] && [ "$MODE" = "dev" ]; then
        check_backend
    fi
    
    echo ""
    
    case $MODE in
        dev)
            log_info "Starting Next.js development server..."
            log_info "Application: http://localhost:$PORT"
            echo ""
            
            PORT=$PORT npm run dev &
            SERVER_PID=$!
            ;;
        build)
            log_info "Building for production..."
            npm run build
            
            if [ $? -eq 0 ]; then
                log_info "Build completed successfully ✓"
                log_info "Run './run_native.sh --start' to start production server"
            else
                log_error "Build failed!"
                exit 1
            fi
            exit 0
            ;;
        start)
            log_info "Starting Next.js production server..."
            log_info "Application: http://localhost:$PORT"
            echo ""
            
            PORT=$PORT npm run start &
            SERVER_PID=$!
            ;;
    esac
    
    # Wait for server to start (only for dev and start modes)
    if [ "$MODE" = "dev" ] || [ "$MODE" = "start" ]; then
        sleep 3
        
        # Run health check
        if ! health_check; then
            log_error "Server failed to start. Check logs for details."
            exit 1
        fi
        
        # Wait for server process
        wait $SERVER_PID
    fi
}

# Run main function
main "$@"
