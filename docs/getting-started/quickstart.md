# Quick Start - Automated Environment Setup

## 🚀 One-Command Setup

### Windows
```powershell
# Fully automated (recommended)
.\setup_auto.bat

# Interactive mode
.\quick_setup.bat
```

### Linux/Mac
```bash
# Fully automated (recommended)
./setup_auto.sh

# Interactive mode
./quick_setup.sh
```

## 📋 What Gets Configured Automatically

| Component | Configuration |
|-----------|--------------|
| 🔐 **Security Keys** | SECRET_KEY, ENCRYPTION_KEY, JWT_SECRET (all cryptographically secure) |
| 🗄️ **Database** | PostgreSQL connection (localhost:5432) |
| 💾 **Redis** | Redis connection (localhost:6379) |
| 🌐 **CORS** | Localhost origins (3000, 8000, 8080) |
| 🤖 **LLM Providers** | All providers configured (keys empty - add if needed) |
| 📂 **Storage** | Local filesystem (./storage) |
| ⚙️ **Features** | WebSocket, Analytics enabled |

## ⚠️ What You Need to Configure

### Required for Production
```bash
# In backend/.env
POSTGRES_PASSWORD=<change-this-secure-password>
APP_DEBUG=false
APP_ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com
```

### Optional - LLM API Keys
```bash
# In backend/.env (add if you want to use cloud LLMs)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
```

## 🎯 Next Steps After Setup

### 1. Start Backend
```bash
cd backend
poetry run uvicorn app.main:app --reload
```

### 2. Start Frontend (new terminal)
```bash
cd frontend
npm run dev
```

### 3. Access Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 🛠️ Individual Script Usage

### Generate Environment Files Only

**Backend:**
```bash
cd backend
python scripts/generate_env.py              # Non-interactive
python scripts/generate_env.py -i           # Interactive wizard
python scripts/generate_env.py --force      # Force overwrite
```

**Frontend:**
```bash
cd frontend
node scripts/generate_env.js                # Non-interactive
node scripts/generate_env.js -i             # Interactive wizard
node scripts/generate_env.js --force        # Force overwrite
```

### Validate Environment
```bash
python scripts/validate_env.py              # Standard validation
python scripts/validate_env.py --strict     # Strict mode
python scripts/validate_env.py --quiet      # Quiet mode
```

## 🔍 Troubleshooting

### Python Not Found
```bash
# Install Python 3.11+
# https://www.python.org/downloads/
```

### Node.js Not Found
```bash
# Install Node.js 18+
# https://nodejs.org/
```

### Database Connection Failed
```bash
# Ensure PostgreSQL is running
# Windows: Check Services
# Linux: sudo systemctl status postgresql
# Mac: brew services list
```

### Redis Connection Failed
```bash
# Ensure Redis is running
# Windows: Check Services
# Linux: sudo systemctl status redis
# Mac: brew services list
```

### Validation Failed
```bash
# Get detailed errors
python scripts/validate_env.py --strict

# Fix issues in backend/.env
```

## 📚 Full Documentation

- **Complete Guide**: `docs/AUTO_SETUP_GUIDE.md`
- **Implementation Summary**: `AUTO_SETUP_SUMMARY.md`

## 🆘 Need Help?

1. Check validation output for specific errors
2. Review `docs/AUTO_SETUP_GUIDE.md` troubleshooting section
3. Verify prerequisites are installed
4. Check service status (PostgreSQL, Redis)

---

**Setup Time**: < 5 minutes  
**Manual Steps**: 0 (for local development)  
**Platform**: Windows, Linux, Mac
