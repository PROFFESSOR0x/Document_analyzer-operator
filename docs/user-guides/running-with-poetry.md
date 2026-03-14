# Running the Project with Poetry

## 🎯 Quick Start

### 1. Install Poetry (if not installed)

```powershell
# Windows
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Add to PATH
$env:Path += ";$env:APPDATA\Python\Scripts"

# Verify installation
poetry --version
```

### 2. Setup the Project

```powershell
# Navigate to backend directory
cd backend

# Generate .env file (if not exists)
python scripts\generate_env.py

# Install dependencies
poetry install

# Run database migrations
poetry run alembic upgrade head
```

### 3. Start the Backend

```powershell
# Development mode (with auto-reload)
poetry run uvicorn app.main:app --reload

# Or without auto-reload
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📋 All Poetry Commands

### Installation & Setup

```powershell
# Install all dependencies
poetry install

# Install only production dependencies
poetry install --only main

# Install with development dependencies
poetry install --with dev

# Update dependencies
poetry update

# Show installed packages
poetry show
```

### Running the Application

```powershell
# Start development server
poetry run uvicorn app.main:app --reload

# Start with specific host/port
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start with multiple workers (production)
poetry run uvicorn app.main:app --workers 4

# Start with log level
poetry run uvicorn app.main:app --log-level debug
```

### Database Operations

```powershell
# Run migrations
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# Rollback last migration
poetry run alembic downgrade -1

# Check current migration
poetry run alembic current

# Show migration history
poetry run alembic history
```

### Running Scripts

```powershell
# Run any Python script
poetry run python scripts/your_script.py

# Run with arguments
poetry run python scripts/generate_env.py --force

# Run interactive
poetry run python scripts/generate_env.py --interactive
```

### Testing

```powershell
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_auth.py

# Run with verbose output
poetry run pytest -v
```

### Code Quality

```powershell
# Run linter
poetry run flake8 app

# Run type checker
poetry run mypy app

# Run formatter check
poetry run black --check app

# Auto-format code
poetry run black app
```

### Shell Access

```powershell
# Open Python shell with project environment
poetry shell

# Then you can run commands without 'poetry run'
python
>>> from app.core.settings import get_settings
>>> get_settings()
```

---

## 🔧 Common Issues & Solutions

### Issue: "Poetry not found"

**Solution:**
```powershell
# Install Poetry
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Add to PATH (permanent)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:APPDATA\Python\Scripts", [System.EnvironmentVariableTarget]::User)
```

### Issue: "Virtual environment not activating"

**Solution:**
```powershell
# Remove existing venv
poetry env remove python

# Create new venv
poetry env use python

# Install dependencies
poetry install
```

### Issue: "Dependencies conflict"

**Solution:**
```powershell
# Clear cache
poetry cache clear pypi --all

# Update lock file
poetry lock --no-update

# Reinstall
poetry install
```

### Issue: "Module not found"

**Solution:**
```powershell
# Make sure you're in backend directory
cd backend

# Activate poetry shell
poetry shell

# Or use poetry run
poetry run python your_script.py
```

---

## 🚀 Complete Startup Sequence

### Option 1: Using poetry shell (Recommended for Development)

```powershell
# Terminal 1 - Backend
cd backend
poetry shell
python scripts\generate_env.py
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd ..\frontend
npm install --legacy-peer-deps
npm run dev
```

### Option 2: Using poetry run (No shell activation)

```powershell
# Terminal 1 - Backend
cd backend
poetry run python scripts\generate_env.py
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd ..\frontend
npm install --legacy-peer-deps
npm run dev
```

### Option 3: Using setup scripts (Easiest)

```powershell
# Run automated setup
.\setup_auto.ps1

# Then start
cd backend
poetry run uvicorn app.main:app --reload
```

---

## 📊 Project Structure with Poetry

```
backend/
├── pyproject.toml          # Poetry configuration
├── poetry.lock             # Locked dependencies
├── .venv/                  # Virtual environment (created by Poetry)
├── scripts/
│   ├── generate_env.py     # Environment generator
│   └── ...
├── app/
│   ├── main.py             # FastAPI application
│   ├── core/
│   │   └── settings.py     # Settings (Pydantic)
│   └── ...
└── alembic/                # Database migrations
```

---

## 🔍 Useful Poetry Commands

```powershell
# Show project info
poetry show

# Show dependency tree
poetry show --tree

# Check for outdated packages
poetry show --outdated

# Add new package
poetry add package-name

# Add dev dependency
poetry add --group dev package-name

# Remove package
poetry remove package-name

# Run any command in virtual environment
poetry run <command>

# Open shell in virtual environment
poetry shell

# Export requirements.txt (for compatibility)
poetry export -f requirements.txt --output requirements.txt
```

---

## 🎯 Development Workflow

### Daily Development

```powershell
# 1. Activate Poetry shell
cd backend
poetry shell

# 2. Run server with auto-reload
poetry run uvicorn app.main:app --reload

# 3. In another terminal, run tests
poetry run pytest tests/ -v

# 4. Check code quality
poetry run flake8 app
poetry run mypy app
```

### Before Committing

```powershell
# Run all tests
poetry run pytest --cov=app

# Check code quality
poetry run flake8 app
poetry run mypy app
poetry run black --check app

# Update lock file if needed
poetry lock --no-update
```

---

## 📚 Additional Resources

- **Poetry Documentation**: https://python-poetry.org/docs/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Project README**: [../README.md](../README.md)
- **Setup Guide**: [../docs/ZERO_CONFIG_SETUP.md](../docs/ZERO_CONFIG_SETUP.md)

---

## 🆘 Quick Help

```powershell
# Check Poetry installation
poetry --version

# Check Python version
python --version

# Check if in backend directory
pwd
ls

# Activate and run
cd backend
poetry shell
poetry run uvicorn app.main:app --reload
```

---

**That's it! Poetry makes dependency management easy!** 🚀

For more help, see:
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- [docs/NATIVE_SETUP.md](../docs/NATIVE_SETUP.md)
