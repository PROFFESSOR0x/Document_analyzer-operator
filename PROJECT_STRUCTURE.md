# Project Structure

Document Analyzer Operator Platform - Complete directory structure and organization.

## Root Directory

```
Document_analyzer-operator/
├── README.md                      # Main documentation entry point
├── PROJECT_STRUCTURE.md           # This file - project structure documentation
├── docker-compose.yml             # Docker orchestration for full stack
├── .gitignore                     # Git ignore rules
├── setup.bat / setup.sh           # Main setup scripts (entry points)
├── start.bat / start.sh           # Quick start backend scripts
├── start-frontend.bat / start-frontend.sh  # Quick start frontend scripts
├── clean.bat / clean.sh           # Cleanup scripts
├── SETTINGS_QUICKSTART.md         # Settings quick reference
├── docs/                          # 📚 All documentation (see docs/README.md)
├── scripts/                       # 🔧 Automation scripts
├── backend/                       # 🐍 Python FastAPI Backend
└── frontend/                      # ⚛️ Next.js React Frontend
```

## Directories

### 📚 docs/ - Documentation Hub

All project documentation organized by category.

```
docs/
├── README.md                      # Documentation index
├── getting-started/               # Setup and onboarding guides
│   ├── quickstart.md
│   ├── zero-config-setup.md
│   ├── native-setup.md
│   ├── windows-setup.md
│   └── auto-setup-guide.md
├── user-guides/                   # End-user configuration guides
│   ├── llm-providers.md
│   ├── settings-management.md
│   ├── openai-compatible.md
│   └── running-with-poetry.md
├── architecture/                  # System design documentation
│   ├── architecture.md
│   ├── agent-framework.md
│   └── workflow-engine.md
├── implementation/                # Implementation details
│   ├── implementation-summary.md
│   ├── llm-implementation.md
│   ├── settings-implementation.md
│   ├── auto-setup-summary.md
│   └── openai-compatible-implementation.md
├── technical/                     # Technical reference
│   ├── api.md
│   ├── tools-and-knowledge.md
│   └── validation-report.md
└── troubleshooting/               # Problem-solving guides
    └── troubleshooting.md
```

### 🔧 scripts/ - Automation Scripts

Executable scripts for setup, running, and maintenance.

```
scripts/
├── README.md                      # Scripts usage guide
├── setup/                         # Setup automation
│   ├── setup_auto.bat / setup_auto.sh    # Full automated setup
│   ├── setup_auto.ps1                    # PowerShell setup
│   ├── quick_setup.bat / quick_setup.sh  # Quick setup (minimal)
│   └── quick_setup.ps1                   # PowerShell quick setup
├── run/                           # Run scripts
│   ├── run_backend.bat / run_backend.sh  # Start backend server
│   ├── run_frontend.bat / run_frontend.sh # Start frontend server
│   └── run_backend_poetry.bat             # Start backend with Poetry
├── maintenance/                   # Maintenance scripts
│   ├── cleanup.bat / cleanup.sh           # Clean temporary files
│   ├── fix_env.bat                        # Fix environment issues
│   ├── setup_fallback.bat                 # Fallback setup
│   ├── stop.bat / stop.sh                 # Stop all services
│   └── systemd/                           # Linux systemd services
│       ├── document-analyzer-backend.service
│       └── document-analyzer-frontend.service
└── install_prerequisites.bat / install_prerequisites.sh  # System dependencies
```

### 🐍 backend/ - Python FastAPI Backend

Backend application code and configuration.

```
backend/
├── README.md                      # Backend documentation
├── pyproject.toml                 # Poetry project configuration
├── poetry.lock                    # Poetry lock file (committed)
├── .env.example                   # Environment template
├── .env.native.example            # Native setup environment template
├── alembic.ini                    # Alembic migration config
├── ecosystem.config.js            # PM2 process manager config
├── docker-compose.yml             # Backend Docker config
├── Dockerfile                     # Backend Docker image
├── setup_native.bat / setup_native.sh     # Native setup script
├── run_native.bat / run_native.sh         # Native run script
├── start.bat / start.sh                   # Quick start script
├── app/                           # Application source code
│   ├── main.py                    # FastAPI application entry
│   ├── api/                       # API routes
│   │   ├── v1/                    # API version 1
│   │   │   ├── endpoints/         # Endpoint handlers
│   │   │   └── router.py          # API router
│   ├── models/                    # SQLAlchemy models
│   ├── schemas/                   # Pydantic schemas
│   ├── services/                  # Business logic services
│   ├── agents/                    # Agent implementations
│   ├── workflows/                 # Workflow definitions
│   ├── tools/                     # Tool implementations
│   ├── llm/                       # LLM provider integrations
│   ├── db/                        # Database configuration
│   └── utils/                     # Utility functions
├── config/                        # Configuration modules
├── scripts/                       # Backend utility scripts
│   ├── init_db.py                 # Database initialization
│   └── migrate.py                 # Migration runner
├── tests/                         # Test suite
│   ├── test_agents/               # Agent tests
│   ├── test_workflows/            # Workflow tests
│   ├── test_tools/                # Tool tests
│   ├── test_llm_providers/        # LLM provider tests
│   └── conftest.py                # Pytest configuration
└── alembic/                       # Database migrations
    ├── versions/                  # Migration files
    └── env.py                     # Alembic environment
```

### ⚛️ frontend/ - Next.js React Frontend

Frontend application code and configuration.

```
frontend/
├── README.md                      # Frontend documentation
├── package.json                   # npm project configuration
├── package-lock.json              # npm lock file
├── next.config.js                 # Next.js configuration
├── next.config.native.js          # Native setup Next.js config
├── tailwind.config.js             # Tailwind CSS configuration
├── tsconfig.json                  # TypeScript configuration
├── .eslintrc.json                 # ESLint configuration
├── .prettierrc                    # Prettier configuration
├── vitest.config.ts               # Vitest test configuration
├── playwright.config.ts           # Playwright E2E config
├── .env.example                   # Environment template
├── ecosystem.config.js            # PM2 process manager config
├── docker-compose.yml             # Frontend Docker config
├── Dockerfile                     # Frontend Docker image
├── setup.bat / setup.sh           # Frontend setup script
├── setup_native.bat / setup_native.sh     # Native setup script
├── run_native.bat / run_native.sh         # Native run script
├── src/                           # Source code
│   ├── app/                       # Next.js App Router
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Home page
│   │   ├── dashboard/             # Dashboard pages
│   │   └── api/                   # API routes
│   ├── components/                # React components
│   │   ├── ui/                    # Base UI components
│   │   ├── agents/                # Agent-related components
│   │   ├── workflows/             # Workflow components
│   │   └── llm/                   # LLM provider components
│   ├── lib/                       # Utility libraries
│   ├── hooks/                     # Custom React hooks
│   ├── stores/                    # Zustand state stores
│   ├── services/                  # API services
│   └── types/                     # TypeScript types
├── public/                        # Static assets
│   ├── images/                    # Image files
│   ├── fonts/                     # Font files
│   └── icons/                     # Icon files
├── scripts/                       # Frontend utility scripts
└── e2e/                           # End-to-end tests
    └── tests/                     # Playwright tests
```

## File Naming Conventions

### Scripts

- **Shell scripts**: `.sh` extension (Linux/Mac)
- **Batch scripts**: `.bat` extension (Windows CMD)
- **PowerShell scripts**: `.ps1` extension (Windows PowerShell)
- **Paired scripts**: Same base name with different extensions (e.g., `setup.sh`, `setup.bat`)

### Documentation

- **Markdown files**: `.md` extension
- **Lowercase names**: All filenames in lowercase with hyphens
- **Descriptive names**: Clear, descriptive filenames (e.g., `llm-providers.md`)

### Configuration

- **Environment templates**: `.env.example`, `.env.local.example`
- **Lock files**: `package-lock.json`, `poetry.lock` (committed)
- **Config files**: Language-specific (`.toml`, `.json`, `.yaml`, `.js`)

## Path Conventions

- **Relative paths**: Used within documentation and scripts
- **Absolute paths**: Used in configuration files when necessary
- **Cross-platform**: Scripts use platform-appropriate path separators

## Entry Points

### For Users

| Script | Purpose | Platform |
|--------|---------|----------|
| `setup.bat` / `setup.sh` | Full project setup | Windows / Linux/Mac |
| `start.bat` / `start.sh` | Start backend | Windows / Linux/Mac |
| `start-frontend.bat` / `start-frontend.sh` | Start frontend | Windows / Linux/Mac |
| `clean.bat` / `clean.sh` | Clean temporary files | Windows / Linux/Mac |

### For Developers

| Directory | Purpose |
|-----------|---------|
| `scripts/setup/` | Setup automation scripts |
| `scripts/run/` | Run/start scripts |
| `scripts/maintenance/` | Maintenance and cleanup |
| `backend/app/` | Backend source code |
| `frontend/src/` | Frontend source code |

## Build Artifacts (Not Committed)

The following are generated during build/run and excluded from Git:

- `node_modules/` - npm dependencies
- `.venv/` - Python virtual environment
- `__pycache__/` - Python bytecode
- `.next/` - Next.js build output
- `.pytest_cache/` - pytest cache
- `.mypy_cache/` - mypy cache
- `*.log` - Log files
- `dist/`, `build/` - Build outputs

---

**Last Updated**: March 2026
**Version**: 2.0.0
