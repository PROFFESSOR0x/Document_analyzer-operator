# Native Setup Guide (No Docker)

This guide provides complete instructions for running the Document-Analyzer-Operator Platform without Docker.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Platform-Specific Instructions](#platform-specific-instructions)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 18+ | Frontend runtime |
| **PostgreSQL** | 16+ | Database |
| **Redis** | 7+ | Cache and sessions |
| **Git** | Latest | Version control |

### Optional Software (for advanced features)

| Software | Purpose |
|----------|---------|
| **Qdrant** | Vector database for embeddings |
| **Neo4j** | Graph database for knowledge |
| **Temporal** | Workflow orchestration |
| **MinIO** | S3-compatible file storage |
| **PM2** | Process manager for production |

---

## 🚀 Quick Start

### Windows

```powershell
# 1. Install prerequisites
cd scripts
.\install_prerequisites.bat

# 2. Setup the application
cd ..
.\setup.bat

# 3. Start all services
.\start.bat

# Access services:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000/docs
```

### macOS

```bash
# 1. Install prerequisites
cd scripts
chmod +x install_prerequisites.sh
./install_prerequisites.sh

# 2. Setup the application
cd ..
chmod +x setup.sh
./setup.sh

# 3. Start all services
./start.sh

# Access services:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000/docs
```

### Linux

```bash
# 1. Install prerequisites
cd scripts
chmod +x install_prerequisites.sh
sudo ./install_prerequisites.sh

# 2. Setup the application
cd ..
chmod +x setup.sh
./setup.sh

# 3. Start all services
./start.sh

# Access services:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000/docs
```

---

## 📖 Detailed Setup

### Step 1: Install Prerequisites

#### Windows (using Chocolatey)

```powershell
# Install Python
choco install python --version=3.11

# Install Node.js
choco install nodejs-lts

# Install PostgreSQL
choco install postgresql16

# Install Redis
choco install redis-64

# Install Poetry (Python package manager)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Restart terminal after installation
```

#### macOS (using Homebrew)

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Install Node.js
brew install node@18

# Install PostgreSQL
brew install postgresql@16

# Install Redis
brew install redis

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Start services
brew services start postgresql@16
brew services start redis
```

#### Linux (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib redis-server git curl

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Start services
sudo systemctl start postgresql
sudo systemctl start redis
sudo systemctl enable postgresql
sudo systemctl enable redis
```

### Step 2: Setup PostgreSQL Database

```bash
# Login to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE document_analyzer;
CREATE USER document_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE document_analyzer TO document_user;
\q

# Or use the automated script
cd backend/scripts
./setup_database.sh
```

### Step 3: Setup Redis

```bash
# Check if Redis is running
redis-cli ping

# Should return: PONG

# If not running, start it:
# Linux
sudo systemctl start redis

# macOS
brew services start redis

# Windows (if installed as service)
net start Redis
```

### Step 4: Setup Backend

```bash
cd backend

# Copy environment file
cp .env.example .env

# Edit .env and set:
# - DATABASE_URL=postgresql://document_user:your_password@localhost:5432/document_analyzer
# - REDIS_URL=redis://localhost:6379
# - SECRET_KEY=<generate with: openssl rand -hex 32>
# - ENCRYPTION_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">

# Install dependencies
poetry install

# Run database migrations
poetry run alembic upgrade head

# Test the setup
poetry run uvicorn app.main:app --reload
```

### Step 5: Setup Frontend

```bash
cd frontend

# Copy environment file
cp .env.example .env.local

# Edit .env.local and set:
# - NEXT_PUBLIC_API_URL=http://localhost:8000
# - NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Install dependencies
npm install

# Start development server
npm run dev
```

### Step 6: Verify Installation

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check frontend
curl http://localhost:3000

# Both should return valid responses
```

---

## 💻 Platform-Specific Instructions

### Windows Specific

#### Running as Windows Services

Use PM2 to run as background services:

```powershell
# Install PM2
npm install -g pm2

# Start backend
cd backend
pm2 start ecosystem.config.js --only backend

# Start frontend
cd frontend
pm2 start ecosystem.config.js --only frontend

# Save PM2 configuration
pm2 save

# Setup PM2 to start on Windows boot
pm2 startup
```

#### Using Task Scheduler

Create scheduled tasks to start services on boot:

```powershell
# Create backend task
$action = New-ScheduledTaskAction -Execute "C:\Path\to\backend\run_native.bat"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "DocumentAnalyzer-Backend" -Action $action -Trigger $trigger -RunLevel Highest

# Create frontend task
$action = New-ScheduledTaskAction -Execute "C:\Path\to\frontend\run_native.bat"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "DocumentAnalyzer-Frontend" -Action $action -Trigger $trigger -RunLevel Highest
```

### macOS Specific

#### Using launchd

Create plist files for launchd:

```bash
# Backend service
cat > ~/Library/LaunchAgents/com.documentanalyzer.backend.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.documentanalyzer.backend</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/backend/run_native.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Load and start
launchctl load ~/Library/LaunchAgents/com.documentanalyzer.backend.plist
launchctl start com.documentanalyzer.backend
```

### Linux Specific

#### Using systemd

```bash
# Copy service files
sudo cp scripts/systemd/*.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable document-analyzer-backend
sudo systemctl enable document-analyzer-frontend

# Start services
sudo systemctl start document-analyzer-backend
sudo systemctl start document-analyzer-frontend

# Check status
sudo systemctl status document-analyzer-backend
sudo systemctl status document-analyzer-frontend

# View logs
sudo journalctl -u document-analyzer-backend -f
```

---

## 🏭 Production Deployment

### Option 1: PM2 (Cross-platform)

```bash
# Install PM2 globally
npm install -g pm2

# Setup backend
cd backend
pm2 start ecosystem.config.js
pm2 save

# Setup frontend
cd frontend
pm2 start ecosystem.config.js
pm2 save

# Setup PM2 startup
pm2 startup
pm2 save
```

**PM2 Commands:**
```bash
# View status
pm2 status

# View logs
pm2 logs

# Restart services
pm2 restart all

# Stop services
pm2 stop all

# Monitor
pm2 monit
```

### Option 2: systemd (Linux)

```bash
# Services are already configured in scripts/systemd/
sudo cp scripts/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable document-analyzer-backend document-analyzer-frontend
sudo systemctl start document-analyzer-backend document-analyzer-frontend
```

### Option 3: Supervisor (Linux)

```bash
# Install supervisor
sudo apt install supervisor

# Create config
cat > /etc/supervisor/conf.d/document-analyzer.conf << EOF
[program:document-analyzer-backend]
command=/path/to/backend/run_native.sh
directory=/path/to/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/document-analyzer/backend.err.log
stdout_logfile=/var/log/document-analyzer/backend.out.log

[program:document-analyzer-frontend]
command=/path/to/frontend/run_native.sh
directory=/path/to/frontend
autostart=true
autorestart=true
stderr_logfile=/var/log/document-analyzer/frontend.err.log
stdout_logfile=/var/log/document-analyzer/frontend.out.log
EOF

# Start services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

---

## 🔧 Troubleshooting

### Common Issues

#### PostgreSQL Connection Error

**Problem:** Cannot connect to PostgreSQL

**Solution:**
```bash
# Check if PostgreSQL is running
# Linux
sudo systemctl status postgresql

# macOS
brew services list

# Windows
Get-Service postgresql*

# Start if not running
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Check connection
psql -U document_user -d document_analyzer -h localhost
```

#### Redis Connection Error

**Problem:** Cannot connect to Redis

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# Should return PONG

# Start Redis
sudo systemctl start redis  # Linux
brew services start redis   # macOS
net start Redis             # Windows
```

#### Port Already in Use

**Problem:** Port 8000 or 3000 already in use

**Solution:**
```bash
# Find process using port
# Linux/macOS
lsof -i :8000
lsof -i :3000

# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill process
kill -9 <PID>

# Or change port in .env files
```

#### Python Import Errors

**Problem:** ModuleNotFoundError

**Solution:**
```bash
cd backend
poetry install
poetry run python -m pip install --upgrade pip
```

#### Node.js Version Mismatch

**Problem:** Incompatible Node.js version

**Solution:**
```bash
# Check version
node --version

# Should be 18+
# Update if needed
# Windows: choco upgrade nodejs-lts
# macOS: brew upgrade node
# Linux: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs
```

#### Permission Denied on Scripts

**Problem:** Cannot execute shell scripts

**Solution:**
```bash
# Make scripts executable
chmod +x setup.sh start.sh stop.sh
chmod +x backend/*.sh
chmod +x frontend/*.sh
chmod +x scripts/*.sh
```

### Health Checks

```bash
# Check all services
cd backend/scripts
./health_check.sh

# Check backend API
curl http://localhost:8000/api/v1/health

# Expected response: {"status":"ok","timestamp":"..."}

# Check frontend
curl http://localhost:3000

# Should return HTML
```

### Logs

```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs
tail -f frontend/logs/*.log

# PM2 logs
pm2 logs

# Systemd logs (Linux)
journalctl -u document-analyzer-backend -f
journalctl -u document-analyzer-frontend -f
```

### Database Migration Issues

```bash
cd backend

# Check migration status
poetry run alembic current

# Upgrade to latest
poetry run alembic upgrade head

# If errors, reset and reapply
poetry run alembic downgrade base
poetry run alembic upgrade head
```

---

## 📊 Performance Optimization

### PostgreSQL Optimization

Edit `postgresql.conf`:
```conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
max_connections = 100
```

### Redis Optimization

Edit `redis.conf`:
```conf
maxmemory 512mb
maxmemory-policy allkeys-lru
appendonly yes
```

### Backend Optimization

In `.env`:
```env
# Enable production mode
APP_ENV=production
APP_DEBUG=false

# Optimize workers
UVICORN_WORKERS=4
```

### Frontend Optimization

Build for production:
```bash
cd frontend
npm run build
npm run start
```

---

## 🔒 Security Hardening

### Firewall Configuration

```bash
# Linux (ufw)
sudo ufw allow 5432/tcp  # PostgreSQL
sudo ufw allow 6379/tcp  # Redis
sudo ufw allow 8000/tcp  # Backend API
sudo ufw allow 3000/tcp  # Frontend
sudo ufw enable
```

### SSL/TLS Setup

Use nginx or Apache as reverse proxy with Let's Encrypt:

```bash
# Install nginx
sudo apt install nginx

# Configure SSL
sudo certbot --nginx -d yourdomain.com
```

### Environment Variables Security

```bash
# Set secure permissions on .env files
chmod 600 backend/.env
chmod 600 frontend/.env.local

# Never commit .env files
# Add to .gitignore
```

---

## 📈 Monitoring

### Application Monitoring

```bash
# PM2 monitoring
pm2 monit

# System resources
htop

# Database monitoring
psql -U document_user -d document_analyzer -c "SELECT * FROM pg_stat_activity;"
```

### Log Aggregation

```bash
# Install lnav for log navigation
sudo apt install lnav

# View all logs
lnav backend/logs/*.log frontend/logs/*.log
```

---

## 📝 Additional Resources

- **Main Documentation**: [docs/README.md](README.md)
- **Docker Setup**: [README.md](../README.md) (Docker section)
- **LLM Provider Setup**: [LLM_SETUP_GUIDE.md](LLM_SETUP_GUIDE.md)
- **API Documentation**: http://localhost:8000/docs

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-13  
**Status:** Production Ready
