#!/bin/bash
# Document Analyzer Operator - Health Check Script
# This script performs health checks on all application services

set -e

echo "================================================"
echo "Document Analyzer Operator - Health Check"
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

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

# Check backend API
check_backend() {
    log_info "Checking Backend API..."
    
    MAX_RETRIES=3
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/health" 2>/dev/null || echo "000")
        
        if [ "$RESPONSE" = "200" ]; then
            log_info "Backend API is healthy ✓ (HTTP $RESPONSE)"
            
            # Get API version
            VERSION=$(curl -s "$BACKEND_URL/api/v1/health" 2>/dev/null | grep -o '"version":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
            log_info "API Version: $VERSION"
            
            return 0
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        sleep 1
    done
    
    log_error "Backend API is not responding (HTTP $RESPONSE)"
    return 1
}

# Check frontend
check_frontend() {
    log_info "Checking Frontend..."
    
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "000")
    
    if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "302" ]; then
        log_info "Frontend is accessible ✓ (HTTP $RESPONSE)"
        return 0
    else
        log_warn "Frontend is not responding (HTTP $RESPONSE)"
        return 1
    fi
}

# Check PostgreSQL
check_postgres() {
    log_info "Checking PostgreSQL..."
    
    if command -v pg_isready &> /dev/null; then
        if pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" > /dev/null 2>&1; then
            log_info "PostgreSQL is running ✓"
            return 0
        else
            log_error "PostgreSQL is not responding"
            return 1
        fi
    else
        log_warn "pg_isready not available, skipping PostgreSQL check"
        return 0
    fi
}

# Check Redis
check_redis() {
    log_info "Checking Redis..."
    
    if command -v redis-cli &> /dev/null; then
        RESPONSE=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping 2>/dev/null || echo "FAILED")
        
        if [ "$RESPONSE" = "PONG" ]; then
            log_info "Redis is running ✓"
            
            # Get memory info
            MEMORY=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO memory 2>/dev/null | grep "used_memory_human" | cut -d: -f2 | tr -d '\r')
            log_info "Redis Memory: $MEMORY"
            
            return 0
        else
            log_error "Redis is not responding"
            return 1
        fi
    else
        log_warn "redis-cli not available, skipping Redis check"
        return 0
    fi
}

# Check disk space
check_disk_space() {
    log_info "Checking disk space..."
    
    DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | tr -d '%')
    
    if [ "$DISK_USAGE" -lt 80 ]; then
        log_info "Disk usage: ${DISK_USAGE}% ✓"
        return 0
    elif [ "$DISK_USAGE" -lt 90 ]; then
        log_warn "Disk usage: ${DISK_USAGE}% (warning)"
        return 0
    else
        log_error "Disk usage: ${DISK_USAGE}% (critical)"
        return 1
    fi
}

# Check Python environment
check_python_env() {
    log_info "Checking Python environment..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        log_info "Python: $PYTHON_VERSION"
    else
        log_error "Python3 not found"
        return 1
    fi
    
    if command -v poetry &> /dev/null; then
        POETRY_VERSION=$(poetry --version)
        log_info "Poetry: $POETRY_VERSION"
    else
        log_warn "Poetry not found"
    fi
    
    return 0
}

# Check Node.js environment
check_node_env() {
    log_info "Checking Node.js environment..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_info "Node.js: $NODE_VERSION"
    else
        log_warn "Node.js not found"
    fi
    
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        log_info "npm: $NPM_VERSION"
    else
        log_warn "npm not found"
    fi
    
    return 0
}

# Run all checks
run_all_checks() {
    echo ""
    echo "================================================"
    echo "Running All Health Checks"
    echo "================================================"
    echo ""
    
    ISSUES=0
    
    check_python_env || ISSUES=$((ISSUES + 1))
    check_node_env || ISSUES=$((ISSUES + 1))
    check_postgres || ISSUES=$((ISSUES + 1))
    check_redis || ISSUES=$((ISSUES + 1))
    check_backend || ISSUES=$((ISSUES + 1))
    check_frontend || ISSUES=$((ISSUES + 1))
    check_disk_space || ISSUES=$((ISSUES + 1))
    
    echo ""
    echo "================================================"
    echo "Health Check Summary"
    echo "================================================"
    
    if [ $ISSUES -eq 0 ]; then
        echo -e "${GREEN}All health checks passed ✓${NC}"
        return 0
    else
        echo -e "${YELLOW}$ISSUES issue(s) detected${NC}"
        return 1
    fi
}

# Print usage
print_usage() {
    echo "Usage: $0 [check]"
    echo ""
    echo "Checks:"
    echo "  all       - Run all checks (default)"
    echo "  backend   - Check backend API"
    echo "  frontend  - Check frontend"
    echo "  postgres  - Check PostgreSQL"
    echo "  redis     - Check Redis"
    echo "  disk      - Check disk space"
    echo "  env       - Check environment"
    echo ""
}

# Main execution
main() {
    CHECK="${1:-all}"
    
    case $CHECK in
        all)
            run_all_checks
            ;;
        backend)
            check_backend
            ;;
        frontend)
            check_frontend
            ;;
        postgres)
            check_postgres
            ;;
        redis)
            check_redis
            ;;
        disk)
            check_disk_space
            ;;
        env)
            check_python_env
            check_node_env
            ;;
        *)
            print_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
