#!/bin/bash
# Document Analyzer Operator - Root Stop Script (Linux/Mac)
# This script stops all services for native (non-Docker) development

set -e

echo "================================================"
echo "Document Analyzer Operator - Stopping Services"
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

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# PID file location
PID_DIR="$SCRIPT_DIR/.pids"

# Stop backend
stop_backend() {
    if [ -f "$PID_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$PID_DIR/backend.pid")
        
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            log_info "Stopping backend (PID: $BACKEND_PID)..."
            kill -TERM "$BACKEND_PID" 2>/dev/null
            
            # Wait for process to stop
            for i in {1..10}; do
                if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
                    log_info "Backend stopped ✓"
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if kill -0 "$BACKEND_PID" 2>/dev/null; then
                log_warn "Force killing backend..."
                kill -9 "$BACKEND_PID" 2>/dev/null
            fi
        else
            log_warn "Backend process not running"
        fi
        
        rm -f "$PID_DIR/backend.pid"
    else
        log_warn "No backend PID file found"
    fi
}

# Stop frontend
stop_frontend() {
    if [ -f "$PID_DIR/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")
        
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            log_info "Stopping frontend (PID: $FRONTEND_PID)..."
            kill -TERM "$FRONTEND_PID" 2>/dev/null
            
            # Wait for process to stop
            for i in {1..10}; do
                if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
                    log_info "Frontend stopped ✓"
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if kill -0 "$FRONTEND_PID" 2>/dev/null; then
                log_warn "Force killing frontend..."
                kill -9 "$FRONTEND_PID" 2>/dev/null
            fi
        else
            log_warn "Frontend process not running"
        fi
        
        rm -f "$PID_DIR/frontend.pid"
    else
        log_warn "No frontend PID file found"
    fi
}

# Kill any remaining node/python processes related to our app
cleanup_processes() {
    log_info "Cleaning up any remaining processes..."
    
    # Kill node processes on port 3000
    if command -v lsof &> /dev/null; then
        NODE_PID=$(lsof -ti:3000 2>/dev/null)
        if [ ! -z "$NODE_PID" ]; then
            kill -9 $NODE_PID 2>/dev/null
            log_info "Killed node process on port 3000"
        fi
    fi
    
    # Kill python processes on port 8000
    if command -v lsof &> /dev/null; then
        PYTHON_PID=$(lsof -ti:8000 2>/dev/null)
        if [ ! -z "$PYTHON_PID" ]; then
            kill -9 $PYTHON_PID 2>/dev/null
            log_info "Killed python process on port 8000"
        fi
    fi
}

# Main execution
main() {
    stop_backend
    stop_frontend
    cleanup_processes
    
    # Clean up PID directory
    if [ -d "$PID_DIR" ]; then
        rm -rf "$PID_DIR"
    fi
    
    echo ""
    echo "================================================"
    echo -e "${GREEN}All Services Stopped${NC}"
    echo "================================================"
}

# Run main function
main "$@"
