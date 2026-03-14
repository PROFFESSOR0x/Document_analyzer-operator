# Quick Setup Guide for Windows

## ✅ Recommended: Use PowerShell Script

The PowerShell script is more robust and handles errors better than batch files.

### Run the Setup

1. **Open PowerShell** (as regular user, no admin needed)

2. **Navigate to the project folder:**
   ```powershell
   cd "D:\Computer-Science\Artificial-Intelligence\AI-programing\Document_analyzer-operator"
   ```

3. **Run the setup:**
   ```powershell
   .\setup_auto.ps1
   ```

   If you get an execution policy error, run:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\setup_auto.ps1
   ```

---

## 🔄 Alternative: Use Batch File

If PowerShell doesn't work, use the batch file:

```batch
.\setup_auto.bat
```

---

## 📋 What the Setup Does

1. ✅ Checks Python (3.11+)
2. ✅ Checks Node.js (18+)
3. ✅ Generates backend `.env` automatically
4. ✅ Generates frontend `.env.local` automatically
5. ✅ Installs all dependencies
6. ✅ Runs database migrations

**Time:** 3-5 minutes

---

## 🚀 After Setup

### Start Backend (Terminal 1)
```powershell
cd backend
poetry run uvicorn app.main:app --reload
```

### Start Frontend (Terminal 2)
```powershell
cd frontend
npm run dev
```

### Access
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs

---

## ⚠️ If You See Errors

### "Python not found"
Install Python 3.11+ from: https://www.python.org/downloads/

### "Node.js not found"
Install Node.js 18+ from: https://nodejs.org/

### "PostgreSQL not running"
Start PostgreSQL:
```powershell
net start postgresql
```

Or install it from: https://www.postgresql.org/download/windows/

### "Redis not running"
Start Redis:
```powershell
net start Redis
```

Or install it from: https://github.com/microsoftarchive/redis/releases

---

## 📚 More Help

- **Full Guide:** [ZERO_CONFIG_SETUP.md](ZERO_CONFIG_SETUP.md)
- **Detailed Docs:** [docs/AUTO_SETUP_GUIDE.md](docs/AUTO_SETUP_GUIDE.md)
- **Quick Reference:** [QUICKSTART.md](QUICKSTART.md)

---

**That's it! Run `.\setup_auto.ps1` and you're good to go!** 🚀
