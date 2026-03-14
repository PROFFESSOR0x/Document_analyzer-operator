#!/bin/bash
# Document Analyzer Operator - Database Setup Script (Linux/Mac)
# This script creates the PostgreSQL database and user for the application

set -e

echo "================================================"
echo "Document Analyzer Operator - Database Setup"
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

# Default configuration
DB_USER="${DB_USER:-document_analyzer}"
DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -base64 32)}"
DB_NAME="${DB_NAME:-document_analyzer}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Check if PostgreSQL is installed
check_postgresql() {
    log_info "Checking PostgreSQL installation..."
    
    if ! command -v psql &> /dev/null; then
        log_error "PostgreSQL is not installed"
        log_error "Install PostgreSQL 16+ first:"
        log_error "  Linux: sudo apt-get install postgresql-16"
        log_error "  Mac: brew install postgresql@16"
        exit 1
    fi
    
    log_info "PostgreSQL found: $(psql --version)"
}

# Check if PostgreSQL is running
check_postgres_running() {
    log_info "Checking if PostgreSQL is running..."
    
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" > /dev/null 2>&1; then
        log_info "PostgreSQL is running on $DB_HOST:$DB_PORT ✓"
    else
        log_error "PostgreSQL is not running"
        log_error "Start PostgreSQL:"
        log_error "  Linux: sudo systemctl start postgresql"
        log_error "  Mac: brew services start postgresql@16"
        exit 1
    fi
}

# Create database user
create_user() {
    log_info "Creating database user: $DB_USER..."
    
    # Check if user already exists
    if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        log_warn "User $DB_USER already exists"
        
        # Update password
        log_info "Updating password for user $DB_USER..."
        sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    else
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
        log_info "User $DB_USER created ✓"
    fi
}

# Create database
create_database() {
    log_info "Creating database: $DB_NAME..."
    
    # Check if database already exists
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        log_warn "Database $DB_NAME already exists"
    else
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        log_info "Database $DB_NAME created ✓"
    fi
}

# Grant permissions
grant_permissions() {
    log_info "Granting permissions..."
    
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
    
    log_info "Permissions granted ✓"
}

# Run SQL initialization script
run_init_sql() {
    log_info "Running initialization SQL..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if [ -f "$SCRIPT_DIR/setup_database.sql" ]; then
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SCRIPT_DIR/setup_database.sql"
        log_info "Initialization SQL executed ✓"
    else
        log_warn "No initialization SQL file found"
    fi
}

# Generate connection string
generate_connection_string() {
    log_info "Generating connection string..."
    
    CONNECTION_STRING="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    
    echo ""
    echo "================================================"
    echo "Database Configuration"
    echo "================================================"
    echo ""
    echo "Connection String:"
    echo "  $CONNECTION_STRING"
    echo ""
    echo "Update your .env file with:"
    echo "  POSTGRES_USER=$DB_USER"
    echo "  POSTGRES_PASSWORD=$DB_PASSWORD"
    echo "  POSTGRES_HOST=$DB_HOST"
    echo "  POSTGRES_PORT=$DB_PORT"
    echo "  POSTGRES_DB=$DB_NAME"
    echo "  DATABASE_URL=$CONNECTION_STRING"
    echo ""
    echo "================================================"
}

# Save credentials to file
save_credentials() {
    log_info "Saving credentials to .db_credentials..."
    
    cat > .db_credentials << EOF
# Database Credentials
# Generated: $(date)
# DO NOT COMMIT THIS FILE TO VERSION CONTROL!

DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_NAME=$DB_NAME
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
EOF
    
    chmod 600 .db_credentials
    log_info "Credentials saved to .db_credentials ✓"
}

# Main execution
main() {
    check_postgresql
    check_postgres_running
    create_user
    create_database
    grant_permissions
    run_init_sql
    save_credentials
    generate_connection_string
    
    log_info "Database setup complete!"
}

# Run main function
main "$@"
