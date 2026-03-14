#!/bin/bash
# Document Analyzer Operator - Service Management Script (Linux/Mac)
# This script manages PostgreSQL, Redis, and other services

set -e

echo "================================================"
echo "Document Analyzer Operator - Service Management"
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

# Detect service manager
detect_service_manager() {
    if command -v systemctl &> /dev/null; then
        SERVICE_MANAGER="systemctl"
    elif command -v brew &> /dev/null; then
        SERVICE_MANAGER="brew"
    else
        SERVICE_MANAGER="manual"
    fi
    
    log_info "Service manager: $SERVICE_MANAGER"
}

# Start PostgreSQL
start_postgres() {
    log_info "Starting PostgreSQL..."
    
    case $SERVICE_MANAGER in
        systemctl)
            if systemctl start postgresql 2>/dev/null; then
                log_info "PostgreSQL started ✓"
            else
                log_error "Failed to start PostgreSQL"
                return 1
            fi
            ;;
        brew)
            if brew services start postgresql@16 2>/dev/null; then
                log_info "PostgreSQL started ✓"
            else
                log_error "Failed to start PostgreSQL"
                return 1
            fi
            ;;
        *)
            log_warn "Manual start required"
            log_warn "Run: pg_ctl -D /var/lib/postgresql/data start"
            return 1
            ;;
    esac
}

# Stop PostgreSQL
stop_postgres() {
    log_info "Stopping PostgreSQL..."
    
    case $SERVICE_MANAGER in
        systemctl)
            systemctl stop postgresql 2>/dev/null && log_info "PostgreSQL stopped ✓"
            ;;
        brew)
            brew services stop postgresql@16 2>/dev/null && log_info "PostgreSQL stopped ✓"
            ;;
        *)
            log_warn "Manual stop required"
            log_warn "Run: pg_ctl -D /var/lib/postgresql/data stop"
            ;;
    esac
}

# Restart PostgreSQL
restart_postgres() {
    log_info "Restarting PostgreSQL..."
    
    case $SERVICE_MANAGER in
        systemctl)
            systemctl restart postgresql 2>/dev/null && log_info "PostgreSQL restarted ✓"
            ;;
        brew)
            brew services restart postgresql@16 2>/dev/null && log_info "PostgreSQL restarted ✓"
            ;;
        *)
            log_warn "Manual restart required"
            log_warn "Run: pg_ctl -D /var/lib/postgresql/data restart"
            ;;
    esac
}

# Start Redis
start_redis() {
    log_info "Starting Redis..."
    
    case $SERVICE_MANAGER in
        systemctl)
            if systemctl start redis-server 2>/dev/null || systemctl start redis 2>/dev/null; then
                log_info "Redis started ✓"
            else
                log_error "Failed to start Redis"
                return 1
            fi
            ;;
        brew)
            if brew services start redis 2>/dev/null; then
                log_info "Redis started ✓"
            else
                log_error "Failed to start Redis"
                return 1
            fi
            ;;
        *)
            log_warn "Manual start required"
            log_warn "Run: redis-server"
            return 1
            ;;
    esac
}

# Stop Redis
stop_redis() {
    log_info "Stopping Redis..."
    
    case $SERVICE_MANAGER in
        systemctl)
            systemctl stop redis-server 2>/dev/null || systemctl stop redis 2>/dev/null
            log_info "Redis stopped ✓"
            ;;
        brew)
            brew services stop redis 2>/dev/null && log_info "Redis stopped ✓"
            ;;
        *)
            log_warn "Manual stop required"
            log_warn "Run: redis-cli shutdown"
            ;;
    esac
}

# Restart Redis
restart_redis() {
    log_info "Restarting Redis..."
    
    case $SERVICE_MANAGER in
        systemctl)
            systemctl restart redis-server 2>/dev/null || systemctl restart redis 2>/dev/null
            log_info "Redis restarted ✓"
            ;;
        brew)
            brew services restart redis 2>/dev/null && log_info "Redis restarted ✓"
            ;;
        *)
            log_warn "Manual restart required"
            log_warn "Run: redis-cli shutdown && redis-server"
            ;;
    esac
}

# Check PostgreSQL status
check_postgres() {
    log_info "Checking PostgreSQL status..."
    
    if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        log_info "PostgreSQL is running ✓"
        
        # Get version
        PG_VERSION=$(psql --version)
        log_info "Version: $PG_VERSION"
        
        return 0
    else
        log_warn "PostgreSQL is not running"
        return 1
    fi
}

# Check Redis status
check_redis() {
    log_info "Checking Redis status..."
    
    if redis-cli -p 6379 ping > /dev/null 2>&1; then
        log_info "Redis is running ✓"
        
        # Get version
        REDIS_VERSION=$(redis-server --version)
        log_info "Version: $REDIS_VERSION"
        
        return 0
    else
        log_warn "Redis is not running"
        return 1
    fi
}

# Check all services
check_all_services() {
    echo ""
    echo "================================================"
    echo "Service Status"
    echo "================================================"
    echo ""
    
    POSTGRES_STATUS=0
    REDIS_STATUS=0
    
    check_postgres || POSTGRES_STATUS=1
    check_redis || REDIS_STATUS=1
    
    echo ""
    echo "================================================"
    echo "Summary"
    echo "================================================"
    
    if [ $POSTGRES_STATUS -eq 0 ] && [ $REDIS_STATUS -eq 0 ]; then
        echo -e "${GREEN}All services are running ✓${NC}"
        return 0
    else
        echo -e "${YELLOW}Some services are not running${NC}"
        [ $POSTGRES_STATUS -ne 0 ] && echo "  - PostgreSQL: Not running"
        [ $REDIS_STATUS -ne 0 ] && echo "  - Redis: Not running"
        return 1
    fi
}

# Start all services
start_all() {
    log_info "Starting all services..."
    
    start_postgres
    sleep 2
    start_redis
    sleep 1
    
    check_all_services
}

# Stop all services
stop_all() {
    log_info "Stopping all services..."
    
    stop_redis
    stop_postgres
    
    log_info "All services stopped"
}

# Restart all services
restart_all() {
    log_info "Restarting all services..."
    
    stop_all
    sleep 2
    start_all
}

# Print usage
print_usage() {
    echo "Usage: $0 <command> [service]"
    echo ""
    echo "Commands:"
    echo "  start     - Start service(s)"
    echo "  stop      - Stop service(s)"
    echo "  restart   - Restart service(s)"
    echo "  status    - Check service status"
    echo "  check     - Check all services"
    echo ""
    echo "Services:"
    echo "  postgres  - PostgreSQL database"
    echo "  redis     - Redis cache"
    echo "  all       - All services (default)"
    echo ""
    echo "Examples:"
    echo "  $0 start all"
    echo "  $0 start postgres"
    echo "  $0 stop redis"
    echo "  $0 status all"
    echo ""
}

# Main execution
main() {
    detect_service_manager
    
    COMMAND="${1:-status}"
    SERVICE="${2:-all}"
    
    case $COMMAND in
        start)
            case $SERVICE in
                postgres) start_postgres ;;
                redis) start_redis ;;
                all) start_all ;;
                *) print_usage; exit 1 ;;
            esac
            ;;
        stop)
            case $SERVICE in
                postgres) stop_postgres ;;
                redis) stop_redis ;;
                all) stop_all ;;
                *) print_usage; exit 1 ;;
            esac
            ;;
        restart)
            case $SERVICE in
                postgres) restart_postgres ;;
                redis) restart_redis ;;
                all) restart_all ;;
                *) print_usage; exit 1 ;;
            esac
            ;;
        status|check)
            check_all_services
            ;;
        *)
            print_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
