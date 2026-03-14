#!/bin/bash
# Document Analyzer Operator - Root Start Script (Linux/Mac)
# This script starts both backend and frontend for native (non-Docker) development

set -e

echo "================================================"
echo "Document Analyzer Operator - Starting Services"
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

# PID file location
PID_DIR="$SCRIPT_DIR/.pids"
mkdir -p "$PID_DIR"

# Cleanup function
cleanup() {
    echo ""
    log_info "Stopping all services..."
    ./stop.sh
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if services are already running
check_running() {
    if [ -f "$PID_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$PID_DIR/backend.pid")
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            log_warn "Backend is already running (PID: $BACKEND_PID)"
            return 1
        else
            rm -f "$PID_DIR/backend.pid"
        fi
    fi
    
    if [ -f "$PID_DIR/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            log_warn "Frontend is already running (PID: $FRONTEND_PID)"
            return 1
        else
            rm -f "$PID_DIR/frontend.pid"
        fi
    fi
    
    return 0
}

# Wait for backend to be ready
wait_for_backend() {
    log_info "Waiting for backend to be ready..."
    
    MAX_RETRIES=60
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -s "http://localhost:8000/api/v1/health" > /dev/null 2>&1; then
            log_info "Backend is healthy ✓"
            return 0
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        sleep 1
    done
    
    log_error "Backend failed to start"
    return 1
}

# Start backend
start_backend() {
    log_info "Starting backend..."
    
    cd "$SCRIPT_DIR/backend"
    
    if [ -f "run_native.sh" ]; then
        chmod +x run_native.sh
        ./run_native.sh --no-check &
        BACKEND_PID=$!
        echo $BACKEND_PID > "$SCRIPT_DIR/.pids/backend.pid"
        log_info "Backend started (PID: $BACKEND_PID)"
    else
        log_error "Backend run script not found!"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
    
    # Wait for backend to be ready
    if ! wait_for_backend; then
        return 1
    fi
}

# Start frontend
start_frontend() {
    log_info "Starting frontend..."
    
    cd "$SCRIPT_DIR/frontend"
    
    if [ -f "run_native.sh" ]; then
        chmod +x run_native.sh
        ./run_native.sh --no-backend-check &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > "$SCRIPT_DIR/.pids/frontend.pid"
        log_info "Frontend started (PID: $FRONTEND_PID)"
    else
        log_error "Frontend run script not found!"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
}

# Main execution
main() {
    # Parse arguments
    SKIP_BACKEND=false
    SKIP_FRONTEND=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend-only)
                SKIP_FRONTEND=true
                shift
                ;;
            --frontend-only)
                SKIP_BACKEND=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Usage: $0 [--backend-only|--frontend-only]"
                exit 1
                ;;
        esac
    done
    
    # Check if already running
    if ! check_running; then
        log_error "Some services are already running. Stop them first with: ./stop.sh"
        exit 1
    fi
    
    # Start services
    if [ "$SKIP_BACKEND" != "true" ]; then
        if ! start_backend; then
            log_error "Failed to start backend"
            exit 1
        fi
    fi
    
    if [ "$SKIP_FRONTEND" != "true" ]; then
        start_frontend
    fi
    
    echo ""
    echo "================================================"
    echo -e "${GREEN}All Services Started!${NC}"
    echo "================================================"
    echo ""
    echo "Services:"
    if [ "$SKIP_BACKEND" != "true" ]; then
        echo "  - Backend API:  http://localhost:8000"
        echo "  - API Docs:     http://localhost:8000/docs"
    fi
    if [ "$SKIP_FRONTEND" != "true" ]; then
        echo "  - Frontend:     http://localhost:3000"
    fi
    echo ""
    echo "To stop all services:"
    echo "  ./stop.sh"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo "================================================"
    
    # Wait for signals
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"
