# 🚀 Zero-Configuration Setup Guide

## Setup Without Filling Any .env File!

The Document-Analyzer-Operator Platform now features **fully automated environment setup**. Just run one command and everything is configured for you!

---

## ⚡ Quick Start (30 Seconds)

### Windows

```powershell
.\setup_auto.bat
```

### Linux/Mac

```bash
chmod +x setup_auto.sh
./setup_auto.sh
```

**That's it!** The script will:
1. ✅ Check prerequisites (Python, Node.js)
2. ✅ Generate secure `.env` files automatically
3. ✅ Install all dependencies
4. ✅ Run database migrations
5. ✅ Validate the setup

---

## 🎯 What Gets Auto-Configured

### Automatically Generated

| Setting | Value | Notes |
|---------|-------|-------|
| **SECRET_KEY** | Random 32-byte secure key | 🔐 Cryptographically secure |
| **ENCRYPTION_KEY** | Fernet encryption key | 🔐 For encrypting secrets |
| **JWT_SECRET_KEY** | Random secure key | 🔐 For JWT tokens |
| **DATABASE_URL** | postgresql://localhost:5432/document_analyzer | 📦 PostgreSQL |
| **REDIS_URL** | redis://localhost:6379 | 🔴 Redis |
| **CORS_ORIGINS** | ["http://localhost:3000","http://localhost:8000"] | 🌐 Localhost only |
| **APP_DEBUG** | true | 🔧 Development mode |
| **APP_ENV** | development | 🔧 Development environment |
| **LLM Provider Keys** | Empty (ready for you to fill) | ⭐ Optional |

### What You Don't Need to Do

❌ No manual `.env` editing  
❌ No key generation  
❌ No URL configuration  
❌ No path setup  
❌ No complex configuration  

---

## 📋 Setup Options

### Option 1: Fully Automated (Recommended)

```bash
# Windows
.\setup_auto.bat

# Linux/Mac
./setup_auto.sh
```

**What it does:**
- Checks prerequisites
- Generates `.env` files
- Installs dependencies
- Runs migrations
- Validates setup

**Time:** 2-5 minutes

### Option 2: Interactive Setup

```bash
# Windows
.\quick_setup.bat

# Linux/Mac
./quick_setup.sh
```

**What it does:**
- Same as automated, but asks for confirmation at each step
- Shows progress and explanations

**Time:** 3-6 minutes

### Option 3: Manual Setup (Traditional)

```bash
# Backend
cd backend
python scripts/generate_env.py
poetry install
poetry run alembic upgrade head

# Frontend
cd frontend
node scripts/generate_env.js
npm install
```

**Time:** 5-10 minutes

---

## 🎨 Customization (Optional)

### Custom Database Configuration

```bash
# Windows
.\setup_auto.bat --db-host myhost --db-port 5432 --db-name mydb

# Linux/Mac
./setup_auto.sh --db-host myhost --db-port 5432 --db-name mydb
```

### Custom Ports

```bash
# Backend on different port
./setup_auto.sh --api-port 8080

# Frontend on different port
./setup_auto.sh --frontend-port 3001
```

### Production Mode

```bash
./setup_auto.sh --env production
```

This sets:
- `APP_DEBUG=false`
- `APP_ENV=production`
- Stricter security settings

---

## 🔧 Regenerate Environment

If you need to regenerate the `.env` file:

```bash
# Backend
cd backend
python scripts/generate_env.py --force

# Frontend
cd frontend
node scripts/generate_env.js --force
```

**Note:** Your existing `.env` will be backed up automatically!

---

## ✅ Validate Setup

After setup, validate everything is configured correctly:

```bash
python scripts/validate_env.py
```

**Expected output:**
```
✓ .env file exists
✓ SECRET_KEY is properly formatted (32+ bytes)
✓ ENCRYPTION_KEY is valid Fernet key
✓ DATABASE_URL format is valid
✓ REDIS_URL format is valid
✓ All required keys present
✓ Environment configuration is valid

✅ Setup validation passed!
```

---

## 🚀 Start the Application

After setup completes:

### Terminal 1 - Backend

```bash
cd backend
poetry run uvicorn app.main:app --reload
```

**Access:** http://localhost:8000/docs

### Terminal 2 - Frontend

```bash
cd frontend
npm run dev
```

**Access:** http://localhost:3000

---

## ⭐ Optional: Configure LLM API Keys

If you want to use cloud LLM providers, add your API keys to `backend/.env`:

```bash
# Open .env file
# Add your keys:

OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GROQ_API_KEY=your-groq-key
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys
- Groq: https://console.groq.com/keys

**Note:** The platform works without these keys using local LLMs (Ollama, LM Studio, etc.)

---

## 🐛 Troubleshooting

### Issue: "PostgreSQL not found"

**Solution:**
```bash
# Install PostgreSQL
# Windows: choco install postgresql16
# macOS: brew install postgresql@16
# Linux: sudo apt install postgresql

# Start PostgreSQL service
# Windows: net start postgresql
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

### Issue: "Redis not found"

**Solution:**
```bash
# Install Redis
# Windows: choco install redis-64
# macOS: brew install redis
# Linux: sudo apt install redis-server

# Start Redis service
# Windows: net start Redis
# macOS: brew services start redis
# Linux: sudo systemctl start redis
```

### Issue: "Python not found"

**Solution:**
```bash
# Install Python 3.11+
# Windows: choco install python --version=3.11
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11
```

### Issue: "Node.js not found"

**Solution:**
```bash
# Install Node.js 18+
# Windows: choco install nodejs-lts
# macOS: brew install node@18
# Linux: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
```

---

## 📊 What's in the Generated .env

### Backend .env

```bash
# Auto-generated environment file
# Generated by scripts/generate_env.py

# Application
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost:8000
SECRET_KEY=<randomly_generated_secure_key>

# Database
DATABASE_URL=postgresql://document_user:document_pass@localhost:5432/document_analyzer

# Redis
REDIS_URL=redis://localhost:6379

# Security
ENCRYPTION_KEY=<randomly_generated_fernet_key>
JWT_SECRET_KEY=<randomly_generated_secure_key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# LLM Providers (configure as needed)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=
TOGETHER_API_KEY=
ANYSCALE_API_KEY=

# Default LLM Settings
DEFAULT_LLM_PROVIDER=local
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# Application Settings
LOG_LEVEL=INFO
UVICORN_WORKERS=4
MAX_UPLOAD_SIZE_MB=10

# Feature Flags
ENABLE_WEBSOCKET=true
ENABLE_ANALYTICS=true

# File Storage (local by default)
STORAGE_TYPE=local
STORAGE_PATH=./storage
```

### Frontend .env.local

```bash
# Auto-generated frontend environment
# Generated by scripts/generate_env.js

NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_ENABLE_WEBSOCKET=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

---

## 🔐 Security Notes

### For Development
✅ All auto-generated settings are secure for local development

### For Production
⚠️ **You MUST change these before deploying:**

```bash
# 1. Change database password
DATABASE_URL=postgresql://user:STRONG_PASSWORD@host:5432/dbname

# 2. Disable debug mode
APP_DEBUG=false

# 3. Set production environment
APP_ENV=production

# 4. Update CORS origins
CORS_ORIGINS=["https://yourdomain.com"]

# 5. Use production-grade secrets
# (Regenerate with: python scripts/generate_env.py --env production)
```

---

## 📚 Additional Resources

- **Complete Setup Guide**: [docs/AUTO_SETUP_GUIDE.md](docs/AUTO_SETUP_GUIDE.md)
- **Quick Reference**: [QUICKSTART.md](QUICKSTART.md)
- **Implementation Details**: [AUTO_SETUP_SUMMARY.md](AUTO_SETUP_SUMMARY.md)
- **Environment Validation**: [scripts/validate_env.py](scripts/validate_env.py)

---

## 🎉 Success Checklist

After running setup:

- [ ] `.env` file created in `backend/`
- [ ] `.env.local` file created in `frontend/`
- [ ] Dependencies installed
- [ ] Database migrations run
- [ ] Validation passed
- [ ] Backend starts successfully
- [ ] Frontend starts successfully
- [ ] Can access http://localhost:3000
- [ ] Can access http://localhost:8000/docs

---

**Setup Time:** 2-5 minutes  
**Complexity:** Zero (fully automated)  
**Manual Configuration:** None required  

**You're ready to go! 🚀**
