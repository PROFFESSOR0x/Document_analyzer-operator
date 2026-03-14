# Document Analyzer Operator - Systemd Service Installation Guide

This guide explains how to install and configure systemd services for production deployment on Linux.

## Prerequisites

- Linux system with systemd (Ubuntu 20.04+, Debian 11+, RHEL 8+, CentOS 8+)
- PostgreSQL 16+ installed and running
- Redis 7+ installed and running
- Python 3.11+ installed
- Node.js 18+ installed
- Application code deployed to `/opt/document-analyzer-operator`

## Installation Steps

### 1. Create Application User

```bash
# Create system user for the application
sudo useradd --system --no-create-home --shell /bin/false document-analyzer
```

### 2. Deploy Application

```bash
# Create application directory
sudo mkdir -p /opt/document-analyzer-operator

# Copy application files
sudo cp -r /path/to/application/* /opt/document-analyzer-operator/

# Set ownership
sudo chown -R document-analyzer:document-analyzer /opt/document-analyzer-operator
```

### 3. Configure Environment

```bash
# Copy environment files
sudo cp /opt/document-analyzer-operator/backend/.env.example /opt/document-analyzer-operator/backend/.env
sudo cp /opt/document-analyzer-operator/frontend/.env.example /opt/document-analyzer-operator/frontend/.env.local

# Edit environment files with production values
sudo nano /opt/document-analyzer-operator/backend/.env
sudo nano /opt/document-analyzer-operator/frontend/.env.local
```

### 4. Install Service Files

```bash
# Copy service files
sudo cp document-analyzer-backend.service /etc/systemd/system/
sudo cp document-analyzer-frontend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload
```

### 5. Enable and Start Services

```bash
# Enable services to start on boot
sudo systemctl enable document-analyzer-backend
sudo systemctl enable document-analyzer-frontend

# Start services
sudo systemctl start document-analyzer-backend
sudo systemctl start document-analyzer-frontend
```

### 6. Verify Services

```bash
# Check service status
sudo systemctl status document-analyzer-backend
sudo systemctl status document-analyzer-frontend

# View logs
sudo journalctl -u document-analyzer-backend -f
sudo journalctl -u document-analyzer-frontend -f
```

## Management Commands

### Start/Stop/Restart

```bash
# Backend
sudo systemctl start document-analyzer-backend
sudo systemctl stop document-analyzer-backend
sudo systemctl restart document-analyzer-backend
sudo systemctl reload document-analyzer-backend

# Frontend
sudo systemctl start document-analyzer-frontend
sudo systemctl stop document-analyzer-frontend
sudo systemctl restart document-analyzer-frontend
```

### View Logs

```bash
# Recent logs
sudo journalctl -u document-analyzer-backend -n 100
sudo journalctl -u document-analyzer-frontend -n 100

# Follow logs
sudo journalctl -u document-analyzer-backend -f
sudo journalctl -u document-analyzer-frontend -f

# Logs from specific time
sudo journalctl -u document-analyzer-backend --since "2024-01-01 00:00:00"
```

### Check Status

```bash
# Service status
sudo systemctl status document-analyzer-backend
sudo systemctl status document-analyzer-frontend

# Service details
sudo systemctl show document-analyzer-backend
```

## Troubleshooting

### Service Won't Start

1. Check logs:
   ```bash
   sudo journalctl -u document-analyzer-backend -n 50 --no-pager
   ```

2. Verify environment file:
   ```bash
   sudo cat /opt/document-analyzer-operator/backend/.env
   ```

3. Check file permissions:
   ```bash
   sudo ls -la /opt/document-analyzer-operator/
   ```

4. Test manually:
   ```bash
   sudo -u document-analyzer bash
   cd /opt/document-analyzer-operator/backend
   source .venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### High Memory Usage

1. Check resource limits:
   ```bash
   sudo systemctl show document-analyzer-backend | grep Limit
   ```

2. Adjust worker count in service file:
   ```bash
   # Edit --workers parameter in ExecStart
   sudo nano /etc/systemd/system/document-analyzer-backend.service
   sudo systemctl daemon-reload
   sudo systemctl restart document-analyzer-backend
   ```

### Database Connection Issues

1. Verify PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Test connection:
   ```bash
   sudo -u document-analyzer bash
   psql -h localhost -U document_analyzer -d document_analyzer
   ```

## Security Considerations

1. **Firewall Configuration**:
   ```bash
   # Allow only necessary ports
   sudo ufw allow 8000/tcp  # Backend API
   sudo ufw allow 3000/tcp  # Frontend
   sudo ufw enable
   ```

2. **SSL/TLS**:
   - Use a reverse proxy (nginx, Apache) for SSL termination
   - Configure Let's Encrypt for automatic certificate renewal

3. **File Permissions**:
   ```bash
   # Ensure proper ownership
   sudo chown -R document-analyzer:document-analyzer /opt/document-analyzer-operator
   
   # Restrict access to sensitive files
   sudo chmod 600 /opt/document-analyzer-operator/backend/.env
   sudo chmod 600 /opt/document-analyzer-operator/frontend/.env.local
   ```

4. **System Hardening**:
   - Keep system packages updated
   - Enable automatic security updates
   - Monitor logs for suspicious activity

## Backup and Recovery

### Create Backup

```bash
# Backup database
sudo -u postgres pg_dump document_analyzer > backup_$(date +%Y%m%d).sql

# Backup application data
sudo tar -czf backup_data_$(date +%Y%m%d).tar.gz /opt/document-analyzer-operator/storage
```

### Restore from Backup

```bash
# Restore database
sudo -u postgres psql document_analyzer < backup_20240101.sql

# Restore application data
sudo tar -xzf backup_data_20240101.tar.gz -C /
```

## Monitoring

### Systemd Monitoring

```bash
# Service uptime
sudo systemctl show document-analyzer-backend | grep ActiveEnterTimestamp

# Resource usage
sudo systemd-cgtop
```

### Application Monitoring

- Configure application metrics endpoint
- Use Prometheus + Grafana for monitoring
- Set up alerting for service failures

## Uninstallation

```bash
# Stop and disable services
sudo systemctl stop document-analyzer-backend
sudo systemctl stop document-analyzer-frontend
sudo systemctl disable document-analyzer-backend
sudo systemctl disable document-analyzer-frontend

# Remove service files
sudo rm /etc/systemd/system/document-analyzer-backend.service
sudo rm /etc/systemd/system/document-analyzer-frontend.service

# Reload systemd
sudo systemctl daemon-reload
```
