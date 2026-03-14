# Scripts Directory

This directory contains all automation scripts for the Document Analyzer Operator Platform.

## Directory Structure

```
scripts/
├── setup/           # Setup and installation scripts
├── run/             # Application run scripts
├── maintenance/     # Maintenance and cleanup scripts
└── systemd/         # Linux systemd service files
```

## Quick Reference

### Setup Scripts

| Script | Platform | Description |
|--------|----------|-------------|
| `setup/setup_auto.bat` | Windows | Full automated setup |
| `setup/setup_auto.sh` | Linux/Mac | Full automated setup |
| `setup/setup_auto.ps1` | Windows | PowerShell automated setup |
| `setup/quick_setup.bat` | Windows | Quick setup (minimal) |
| `setup/quick_setup.sh` | Linux/Mac | Quick setup (minimal) |
| `setup/quick_setup.ps1` | Windows | PowerShell quick setup |
| `install_prerequisites.bat` | Windows | Install system dependencies |
| `install_prerequisites.sh` | Linux/Mac | Install system dependencies |

### Run Scripts

| Script | Platform | Description |
|--------|----------|-------------|
| `run/run_backend.bat` | Windows | Start backend server |
| `run/run_backend.sh` | Linux/Mac | Start backend server |
| `run/run_frontend.bat` | Windows | Start frontend server |
| `run/run_frontend.sh` | Linux/Mac | Start frontend server |
| `run/run_backend_poetry.bat` | Windows | Start backend with Poetry |

### Maintenance Scripts

| Script | Platform | Description |
|--------|----------|-------------|
| `maintenance/cleanup.bat` | Windows | Clean temporary files |
| `maintenance/cleanup.sh` | Linux/Mac | Clean temporary files |
| `maintenance/stop.bat` | Windows | Stop all services |
| `maintenance/stop.sh` | Linux/Mac | Stop all services |
| `maintenance/fix_env.bat` | Windows | Fix environment issues |
| `maintenance/setup_fallback.bat` | Windows | Fallback setup option |

## Usage

### From Root Directory

Use the root-level shortcut scripts (recommended):

```bash
# Setup
./setup.sh          # Linux/Mac
setup.bat           # Windows

# Start backend
./start.sh          # Linux/Mac
start.bat           # Windows

# Start frontend
./start-frontend.sh # Linux/Mac
start-frontend.bat  # Windows

# Cleanup
./clean.sh          # Linux/Mac
clean.bat           # Windows
```

### Direct Script Execution

Navigate to the scripts directory:

```bash
cd scripts

# Setup
cd setup
./setup_auto.sh     # Linux/Mac
setup_auto.bat      # Windows

# Run
cd ../run
./run_backend.sh    # Linux/Mac
run_backend.bat     # Windows

# Maintenance
cd ../maintenance
./cleanup.sh        # Linux/Mac
cleanup.bat         # Windows
```

## Script Details

### Setup Scripts

#### setup_auto.* (Full Setup)

Complete automated setup process:
- Checks prerequisites (Python, Node.js, Poetry)
- Installs missing dependencies
- Creates virtual environments
- Installs project dependencies
- Sets up environment files
- Runs database migrations
- Verifies installation

**Usage:**
```bash
# Windows
scripts\setup\setup_auto.bat

# Linux/Mac
scripts/setup/setup_auto.sh
```

#### quick_setup.* (Minimal Setup)

Quick setup for users who already have prerequisites:
- Installs project dependencies only
- Skips prerequisite checks
- Faster execution

**Usage:**
```bash
# Windows
scripts\setup\quick_setup.bat

# Linux/Mac
scripts/setup/quick_setup.sh
```

#### install_prerequisites.*

System-level dependency installation:
- Python 3.11+
- Node.js 18+
- Poetry
- PostgreSQL (optional)
- Redis (optional)

**Usage:**
```bash
# Windows
scripts\install_prerequisites.bat

# Linux/Mac
scripts/install_prerequisites.sh
```

### Run Scripts

#### run_backend.*

Starts the FastAPI backend server:
- Activates virtual environment (if needed)
- Starts uvicorn server
- Enables auto-reload for development

**Usage:**
```bash
# Windows
scripts\run\run_backend.bat

# Linux/Mac
scripts/run/run_backend.sh
```

#### run_frontend.*

Starts the Next.js frontend server:
- Installs dependencies (if needed)
- Starts development server
- Enables hot reload

**Usage:**
```bash
# Windows
scripts\run\run_frontend.bat

# Linux/Mac
scripts/run/run_frontend.sh
```

### Maintenance Scripts

#### cleanup.*

Removes temporary and build files:
- Python cache (`__pycache__`, `*.pyc`)
- node_modules directory
- Next.js build cache (`.next/`)
- Test caches (`.pytest_cache/`, `.mypy_cache/`)
- Log files (`*.log`)
- Temporary files (`*.tmp`, `*.bak`)

**Note:** Does NOT remove:
- `poetry.lock` (reproducible builds)
- `package-lock.json` (reproducible builds)
- `.env` files (configuration)

**Usage:**
```bash
# Windows
scripts\maintenance\cleanup.bat

# Linux/Mac
scripts/maintenance/cleanup.sh
```

#### stop.*

Stops all running services:
- Backend server
- Frontend server
- Docker containers (if using Docker)

**Usage:**
```bash
# Windows
scripts\maintenance\stop.bat

# Linux/Mac
scripts/maintenance/stop.sh
```

#### fix_env.bat

Diagnoses and fixes common environment issues:
- Missing environment variables
- Incorrect paths
- Permission issues
- Dependency conflicts

**Usage:**
```bash
scripts\maintenance\fix_env.bat
```

## Systemd Services (Linux)

For production deployment on Linux, use the systemd service files:

```bash
# Copy service files
sudo cp scripts/systemd/*.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable document-analyzer-backend
sudo systemctl enable document-analyzer-frontend

# Start services
sudo systemctl start document-analyzer-backend
sudo systemctl start document-analyzer-frontend

# Check status
sudo systemctl status document-analyzer-backend
sudo systemctl status document-analyzer-frontend
```

## Script Development Guidelines

### Naming Conventions

- Use lowercase with underscores for script names
- Pair scripts across platforms with same base name
- Include platform extension (`.sh`, `.bat`, `.ps1`)

### Error Handling

All scripts should:
- Check for required dependencies
- Provide clear error messages
- Exit with appropriate error codes
- Log actions when possible

### Cross-Platform Compatibility

When writing scripts:
- Use platform-appropriate path separators
- Handle case sensitivity differences
- Test on all target platforms
- Document platform-specific behavior

## Troubleshooting

### Scripts Not Executing

**Linux/Mac:**
```bash
# Make scripts executable
chmod +x scripts/setup/*.sh
chmod +x scripts/run/*.sh
chmod +x scripts/maintenance/*.sh
```

**Windows:**
```powershell
# Allow script execution (PowerShell)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Permission Denied

**Linux/Mac:**
```bash
# Run with appropriate permissions
sudo ./scripts/setup/setup_auto.sh  # Only if needed
```

**Windows:**
```powershell
# Run as Administrator
# Right-click on .bat file -> "Run as Administrator"
```

### Path Issues

If scripts fail due to path issues:
- Use absolute paths in scripts
- Quote all path variables
- Handle spaces in paths correctly

## Support

For issues with scripts:
1. Check the [Troubleshooting Guide](../docs/troubleshooting/troubleshooting.md)
2. Review logs in the `logs/` directory
3. Run `scripts/maintenance/fix_env.bat` (Windows)
4. Check the [Documentation Hub](../docs/README.md)

---

**Last Updated**: March 2026
**Version**: 2.0.0
