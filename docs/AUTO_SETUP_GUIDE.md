# Automated Environment Setup Guide

This directory contains automated scripts for setting up the Document Analyzer Operator environment with zero manual configuration.

## Quick Start

### Windows (One-Command Setup)

```bash
# Fully automated (no prompts)
.\setup_auto.bat

# Interactive mode (asks before overwriting)
.\quick_setup.bat

# Traditional setup (with env generation)
.\setup.bat
```

### Linux/Mac (One-Command Setup)

```bash
# Fully automated (no prompts)
./setup_auto.sh

# Interactive mode (asks before overwriting)
./quick_setup.sh

# Traditional setup (with env generation)
./setup.sh
```

## Scripts Overview

### Root Level Scripts

| Script | Platform | Description |
|--------|----------|-------------|
| `setup_auto.bat/sh` | Win/Linux | Fully automated setup, no prompts |
| `quick_setup.bat/sh` | Win/Linux | Quick setup with optional prompts |
| `setup.bat/sh` | Win/Linux | Traditional setup with env generation |

### Backend Scripts

| Script | Location | Description |
|--------|----------|-------------|
| `generate_env.py` | `backend/scripts/` | Generate backend `.env` with secure keys |
| `validate_env.py` | `scripts/` | Validate environment configuration |

### Frontend Scripts

| Script | Location | Description |
|--------|----------|-------------|
| `generate_env.js` | `frontend/scripts/` | Generate frontend `.env.local` |

## Features

### Backend Environment Generator (`generate_env.py`)

**Auto-Generated Configuration:**
- ✅ Secure random `SECRET_KEY` (32 bytes)
- ✅ Secure random `ENCRYPTION_KEY` (Fernet key)
- ✅ Secure random `JWT_SECRET_KEY`
- ✅ Default `DATABASE_URL` (PostgreSQL localhost)
- ✅ Default `REDIS_URL` (Redis localhost)
- ✅ All LLM provider configurations (empty by default)
- ✅ Sensible defaults for all settings

**Features:**
- Automatic backup of existing `.env` files
- Interactive mode with wizard (`--interactive`)
- Non-interactive mode for automation (`--force`)
- Service detection (PostgreSQL, Redis)
- Clear guidance on what needs manual configuration

**Usage:**
```bash
# Non-interactive with defaults
python backend/scripts/generate_env.py

# Interactive wizard
python backend/scripts/generate_env.py --interactive

# Force overwrite existing
python backend/scripts/generate_env.py --force

# Custom configuration
python backend/scripts/generate_env.py \
  --env production \
  --port 8080 \
  --workers 8 \
  --log-level DEBUG
```

### Frontend Environment Generator (`generate_env.js`)

**Auto-Generated Configuration:**
- ✅ `NEXT_PUBLIC_API_URL` (http://localhost:8000)
- ✅ `NEXT_PUBLIC_WS_URL` (ws://localhost:8000)
- ✅ `NEXT_PUBLIC_ENABLE_WEBSOCKET` (true)
- ✅ Feature flags and development settings

**Features:**
- Automatic backup of existing `.env.local` files
- Interactive mode with wizard (`--interactive`)
- Non-interactive mode for automation (`--force`)
- Port availability detection

**Usage:**
```bash
# Non-interactive with defaults
node frontend/scripts/generate_env.js

# Interactive wizard
node frontend/scripts/generate_env.js --interactive

# Force overwrite existing
node frontend/scripts/generate_env.js --force

# Custom configuration
node frontend/scripts/generate_env.js \
  --api-url http://localhost:8080 \
  --ws-url ws://localhost:8080
```

### Environment Validator (`validate_env.py`)

**Validations:**
- ✅ File existence check
- ✅ Required keys presence
- ✅ `SECRET_KEY` length (min 32 characters)
- ✅ `ENCRYPTION_KEY` format (Fernet key)
- ✅ `DATABASE_URL` format (PostgreSQL URL)
- ✅ `REDIS_URL` format (Redis URL)
- ✅ Boolean value validation
- ✅ Port number validation (1-65535)

**Exit Codes:**
- `0` - All validations passed
- `1` - Validation failed

**Usage:**
```bash
# Validate backend .env
python scripts/validate_env.py

# Strict mode (fail on recommended keys)
python scripts/validate_env.py --strict

# Custom path
python scripts/validate_env.py --env /path/to/.env

# Quiet mode
python scripts/validate_env.py --quiet
```

## What's Auto-Configured

### Backend (`.env`)

| Category | Settings |
|----------|----------|
| **Application** | `APP_ENV`, `APP_DEBUG`, `APP_URL` |
| **Security** | `SECRET_KEY`, `ENCRYPTION_KEY`, `JWT_SECRET_KEY`, `JWT_ALGORITHM` |
| **Database** | `DATABASE_URL` (PostgreSQL localhost:5432) |
| **Redis** | `REDIS_URL` (Redis localhost:6379) |
| **CORS** | `CORS_ORIGINS` (localhost:3000, localhost:8000) |
| **LLM Providers** | All providers configured (keys empty by default) |
| **Storage** | Local filesystem storage |
| **Features** | WebSocket, Analytics enabled |

### Frontend (`.env.local`)

| Category | Settings |
|----------|----------|
| **API** | `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_WS_URL` |
| **Features** | WebSocket, Real-time updates |
| **Development** | Dev mode, Debug enabled |

## What Needs Manual Configuration

### Required for Production

| Setting | File | Description |
|---------|------|-------------|
| `POSTGRES_PASSWORD` | `backend/.env` | Change from default |
| `DATABASE_URL` | `backend/.env` | Update password |
| `CORS_ORIGINS` | `backend/.env` | Add production domains |
| `APP_DEBUG` | `backend/.env` | Set to `false` |
| `APP_ENVIRONMENT` | `backend/.env` | Set to `production` |

### Optional (LLM API Keys)

Add these to `backend/.env` if you want to use cloud LLM providers:

| Provider | Key | Get From |
|----------|-----|----------|
| OpenAI | `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| Anthropic | `ANTHROPIC_API_KEY` | https://console.anthropic.com/settings/keys |
| Groq | `GROQ_API_KEY` | https://console.groq.com/keys |
| Together AI | `TOGETHER_API_KEY` | https://api.together.ai/settings/api-keys |
| Anyscale | `ANYSCALE_API_KEY` | https://app.endpoints.anyscale.com/credentials |

### Local LLM (No API Keys Needed)

For local LLM inference, install one of:
- **Ollama**: https://ollama.ai/
- **LM Studio**: https://lmstudio.ai/
- **vLLM**: https://docs.vllm.ai/

## Setup Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Automated Setup Flow                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Validate Prerequisites                              │
│  - Python 3.11+                                              │
│  - Node.js 18+                                               │
│  - Git                                                       │
│  - Poetry (auto-install if missing)                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Generate Backend .env                               │
│  - Generate secure random keys                               │
│  - Configure database connection                             │
│  - Configure Redis connection                                │
│  - Backup existing .env                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Generate Frontend .env.local                        │
│  - Configure API URL                                         │
│  - Configure WebSocket URL                                   │
│  - Backup existing .env.local                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Install Dependencies                                │
│  - Backend: poetry install                                   │
│  - Frontend: npm install                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Run Database Migrations                             │
│  - alembic upgrade head                                      │
│  - Creates all database tables                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 6: Validate Setup                                      │
│  - Check .env file validity                                  │
│  - Verify all required keys present                          │
│  - Validate key formats                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 7: Show Next Steps                                     │
│  - How to start backend                                      │
│  - How to start frontend                                     │
│  - Access URLs                                               │
│  - Configuration guidance                                    │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Python Version Error

```bash
# Check Python version
python --version

# Should be 3.11 or higher
# If not, install from: https://www.python.org/downloads/
```

### Node.js Version Error

```bash
# Check Node.js version
node --version

# Should be 18 or higher
# If not, install from: https://nodejs.org/
```

### Poetry Installation Failed

```bash
# Manual installation
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Database Connection Failed

```bash
# Check if PostgreSQL is running
# Windows: Check Services
# Linux: sudo systemctl status postgresql
# Mac: brew services list

# Test connection
psql -h localhost -U document_user -d document_analyzer
```

### Redis Connection Failed

```bash
# Check if Redis is running
# Windows: Check Services
# Linux: sudo systemctl status redis
# Mac: brew services list

# Test connection
redis-cli ping
# Should return: PONG
```

### Environment Validation Failed

```bash
# Run validation with details
python scripts/validate_env.py --strict

# Review error messages and fix in backend/.env
```

## Advanced Usage

### Custom Database Configuration

```bash
python backend/scripts/generate_env.py \
  --db-host db.example.com \
  --db-port 5432 \
  --db-name myapp \
  --db-user myuser \
  --db-password mypassword
```

### Custom Server Configuration

```bash
python backend/scripts/generate_env.py \
  --host 0.0.0.0 \
  --port 8080 \
  --workers 8 \
  --log-level DEBUG \
  --env production
```

### CI/CD Integration

```bash
# In your CI/CD pipeline
export CI=true

# Run fully automated setup
./setup_auto.sh

# Validate
python scripts/validate_env.py --strict
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit `.env` files** - They are in `.gitignore` for a reason
2. **Change default passwords** - Before deploying to production
3. **Use strong secrets** - Auto-generated keys are cryptographically secure
4. **Restrict CORS** - Update `CORS_ORIGINS` for production
5. **Disable debug mode** - Set `APP_DEBUG=false` in production
6. **Use HTTPS** - In production, always use HTTPS

## Support

For issues or questions:
1. Check the validation output for specific errors
2. Review the troubleshooting section above
3. Check the main README.md
4. Open an issue on the repository
