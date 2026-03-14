# Troubleshooting Setup Issues

## ✅ Quick Fixes

### Issue: npm install fails with "react-flow-renderer" error

**Solution:** The package was renamed. It's now `@xyflow/react`.

The `package.json` has been updated. Run:

```powershell
cd frontend
npm install --legacy-peer-deps
```

Or use the fallback setup:

```powershell
.\setup_fallback.bat
```

---

### Issue: Python script errors with "AttributeError: 'Namespace' object has no attribute 'reload'"

**Solution:** This was fixed by adding the missing `--reload` argument.

Run again:

```powershell
.\setup_auto.ps1
```

Or manually generate the .env:

```powershell
cd backend
python scripts\generate_env.py
```

---

### Issue: npm install fails with peer dependencies error

**Solution:** Use legacy peer deps mode:

```powershell
cd frontend
npm install --legacy-peer-deps
```

---

### Issue: PostgreSQL not running

**Solution:**

```powershell
# Start PostgreSQL service
net start postgresql

# Or check if it's installed
where psql
```

If not installed, download from: https://www.postgresql.org/download/windows/

---

### Issue: Redis not running

**Solution:**

```powershell
# Start Redis service
net start Redis

# Or check if installed
where redis-cli
```

If not installed, download from: https://github.com/microsoftarchive/redis/releases

---

## 🔧 Manual Setup (If Automated Fails)

### Step 1: Create Backend .env

Create `backend\.env` with:

```bash
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost:8000
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgresql://document_user:document_pass@localhost:5432/document_analyzer
REDIS_URL=redis://localhost:6379
ENCRYPTION_KEY=c2VjcmV0LWtleS1mb3ItZGV2ZWxvcG1lbnQtb25seQ==
JWT_SECRET_KEY=dev-jwt-secret-change-in-production
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=
```

### Step 2: Create Frontend .env.local

Create `frontend\.env.local` with:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_ENABLE_WEBSOCKET=true
```

### Step 3: Install Dependencies

```powershell
# Backend
cd backend
poetry install

# Frontend
cd frontend
npm install --legacy-peer-deps
```

### Step 4: Run Migrations

```powershell
cd backend
poetry run alembic upgrade head
```

---

## 🆘 Use Fallback Setup

If the main setup fails, use the fallback:

```powershell
.\setup_fallback.bat
```

This script:
- Creates .env files manually
- Handles errors gracefully
- Provides clear instructions
- Works even if services are missing

---

## 📋 Verify Setup

After setup, verify:

```powershell
# Check .env exists
test-path backend\.env
test-path frontend\.env.local

# Check dependencies
cd backend
poetry show

cd ..\frontend
npm list --depth=0
```

---

## 🎯 Start the Application

```powershell
# Terminal 1 - Backend
cd backend
poetry run uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## 📚 More Help

- **Setup Guide**: [docs/ZERO_CONFIG_SETUP.md](docs/ZERO_CONFIG_SETUP.md)
- **Windows Guide**: [docs/WINDOWS_SETUP_QUICK.md](docs/WINDOWS_SETUP_QUICK.md)
- **Native Setup**: [docs/NATIVE_SETUP.md](docs/NATIVE_SETUP.md)

---

**Still having issues? Check the logs:**

```powershell
# Backend logs
cd backend
poetry run uvicorn app.main:app --reload --log-level debug

# Frontend logs
cd frontend
npm run dev -- --debug
```
