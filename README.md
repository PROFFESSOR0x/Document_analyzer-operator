# Document-Analyzer-Operator Platform

## 🎯 Project Overview

The **Document-Analyzer-Operator Platform** is a large-scale autonomous agent ecosystem designed for intelligent document analysis, knowledge synthesis, content generation, and complex workflow orchestration through multi-agent collaboration.

### Core Capabilities

- **Multi-Agent Collaboration**: 24+ specialized agents across 6 categories (all LLM-enabled)
- **Multi-LLM Provider Support**: 10+ cloud and local LLM providers
- **OpenAI-Compatible APIs**: Drop-in replacement providers (Groq, Together AI, Anyscale, LocalAI, vLLM)
- **Autonomous Workflow Orchestration**: Temporal.io-powered durable workflows
- **Document Intelligence**: PDF, DOCX, Markdown parsing with OCR support
- **Knowledge Management**: Vector search, graph-based knowledge, semantic search
- **Content Generation**: Academic writing, technical documentation, code generation
- **Research Automation**: Web research, fact verification, citation management
- **Tool Ecosystem**: 20+ tools for web, AI, automation, and data operations
- **Usage Analytics**: Token tracking, cost estimation, provider monitoring
- **Encrypted Credentials**: Secure API key storage with Fernet encryption

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Interaction Layer                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Dashboard  │  │     CLI      │  │  REST/GraphQL │           │
│  │  (Next.js)  │  │   Interface  │  │     API       │           │
│  └─────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestration Layer                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │    Goal     │  │     Task     │  │   Strategy   │           │
│  │ Interpreter │  │  Decomposer  │  │    Planner   │           │
│  └─────────────┘  └──────────────┘  └──────────────┘           │
│  ┌──────────────────────────────────────────────────┐           │
│  │          Workflow Coordinator (Temporal)         │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Agent Intelligence Layers                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Cognitive  │  │    Content   │  │  Engineering │          │
│  │   Agents     │  │    Agents    │  │    Agents    │          │
│  │  - Research  │  │  - Architect │  │  - Analyst   │          │
│  │  - Document  │  │  - Writing   │  │  - Tech Sel  │          │
│  │  - Synthesis │  │  - Editing   │  │  - Debate    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Programming │  │  Operational │  │  Validation  │          │
│  │    Agents    │  │    Agents    │  │    Agents    │          │
│  │  - Generator │  │  - Executor  │  │  - Validator │          │
│  │  - Reviewer  │  │  - File Ops  │  │  - Checker   │          │
│  │  - Debugger  │  │  - Automation│  │  - Verifier  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────────────────────────────────────────┐           │
│  │           LLM Provider Integration Layer          │           │
│  │  (OpenAI, Anthropic, Groq, Ollama, LocalAI...)   │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Tool Capability Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Web    │  └──────────┘  └──────────┘  └──────────┘       │
│  │  Tools   │  └──────────┘  └──────────┘  └──────────┘       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│  ┌──────────────────────────────────────────────────┐           │
│  │              Data Tools & Utilities              │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Infrastructure                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Session   │  │   Long-term  │  │  Embedding   │           │
│  │   Memory    │  │   Storage    │  │    Store     │           │
│  │   (Redis)   │  │  (PostgreSQL)│  │  (Qdrant)    │           │
│  └─────────────┘  └──────────────┘  └──────────────┘           │
│  ┌──────────────────────────────────────────────────┐           │
│  │          Knowledge Graph (Neo4j)                 │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Document_analyzer-operator/
├── README.md                    # Main documentation
├── PROJECT_STRUCTURE.md         # Detailed project structure
├── docker-compose.yml           # Docker orchestration
├── setup.bat/sh                 # Main setup entry point
├── start.bat/sh                 # Start backend
├── start-frontend.bat/sh        # Start frontend
├── clean.bat/sh                 # Cleanup utilities
├── docs/                        # Documentation (22 files)
│   ├── README.md               # Documentation index
│   ├── getting-started/        # Setup guides (5)
│   ├── user-guides/            # User guides (4)
│   ├── architecture/           # Architecture docs (3)
│   ├── implementation/         # Implementation docs (5)
│   ├── technical/              # Technical docs (3)
│   └── troubleshooting/        # Troubleshooting (1)
├── scripts/                     # Automation scripts (18)
│   ├── README.md               # Scripts usage guide
│   ├── setup/                  # Setup scripts (7)
│   ├── run/                    # Run scripts (6)
│   └── maintenance/            # Maintenance scripts (5)
├── backend/                     # Python FastAPI backend
└── frontend/                    # Next.js React frontend
```

For detailed information about the project structure, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md).

### Quick Overview
- **Root** - Entry points and main configuration
- **docs/** - All documentation (22 files in 6 categories)
- **scripts/** - Automation scripts (18 files in 3 categories)
- **backend/** - Python FastAPI application
- **frontend/** - Next.js React application

---

## 🚀 Quick Start

### Choose Your Setup Method

#### Option A: Docker Setup (Recommended for most users)

```bash
# Start all services with Docker
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Option B: Native Setup (No Docker required)

**Windows:**
```powershell
# 1. Setup application (automated)
setup.bat

# 2. Start backend
start.bat

# 3. Start frontend (in new terminal)
start-frontend.bat
```

**macOS/Linux:**
```bash
# 1. Setup application (automated)
chmod +x setup.sh
./setup.sh

# 2. Start backend
chmod +x start.sh
./start.sh

# 3. Start frontend (in new terminal)
chmod +x start-frontend.sh
./start-frontend.sh
```

**Quick Commands:**
```bash
# Setup
setup.bat          # Windows
./setup.sh         # Linux/Mac

# Start backend
start.bat          # Windows
./start.sh         # Linux/Mac

# Start frontend
start-frontend.bat # Windows
./start-frontend.sh # Linux/Mac

# Cleanup
clean.bat          # Windows
./clean.sh         # Linux/Mac
```

📖 **Documentation**: [Documentation Index](docs/README.md) | **Scripts Guide**: [scripts/README.md](scripts/README.md)

---

### Prerequisites

| Method | Requirements |
|--------|-------------|
| **Docker** | Docker 20+, Docker Compose |
| **Native** | Python 3.11+, Node.js 18+, PostgreSQL 16+, Redis 7+ |

---

### 1. Clone and Setup

```bash
cd "D:\Computer-Science\Artificial-Intelligence\AI-programing\Document_analyzer-operator"
```

### 2. Backend Setup

#### Docker Mode
```bash
# Infrastructure is managed by docker-compose
docker-compose up -d postgres redis temporal
```

#### Native Mode
```bash
cd backend

# Run native setup
./setup_native.sh          # Linux/Mac
.\setup_native.bat         # Windows

# This will:
# - Install Poetry and dependencies
# - Create virtual environment
# - Setup .env file with secure keys
# - Run database migrations
# - Verify installation
```

**Manual Backend Setup:**
```bash
cd backend

# Install dependencies
poetry install

# Generate encryption key for LLM API keys
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Copy environment file and edit
cp .env.example .env
# Set SECRET_KEY and ENCRYPTION_KEY in .env

# Run migrations
poetry run alembic upgrade head

# Start backend server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend API Docs**: http://localhost:8000/docs

### 3. Frontend Setup

#### Native Mode
```bash
cd frontend

# Run native setup
./setup_native.sh          # Linux/Mac
.\setup_native.bat         # Windows

# This will:
# - Check Node.js installation
# - Install npm dependencies
# - Setup .env.local file
# - Verify installation
```

**Manual Frontend Setup:**
```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Start development server
npm run dev
```

**Frontend Dashboard**: http://localhost:3000

### 4. Configure LLM Providers

#### Option A: Via Dashboard
1. Go to: http://localhost:3000/dashboard/settings/llm-providers
2. Click "Add Provider"
3. Select provider type (OpenAI, Groq, Ollama, etc.)
4. Enter API key and configuration
5. Test connection and save

#### Option B: Via API
```bash
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Groq",
    "provider_type": "openai_compatible",
    "base_url": "https://api.groq.com/openai/v1",
    "api_key": "your-groq-key",
    "model_name": "mixtral-8x7b-32768"
  }'
```

---

## 🛠️ Available Scripts

### Setup Scripts
- `setup.bat/sh` - Main setup entry point
- `scripts/setup/setup_auto.*` - Automated setup
- `scripts/setup/quick_setup.*` - Interactive setup

### Run Scripts
- `start.bat/sh` - Start backend
- `start-frontend.bat/sh` - Start frontend
- `scripts/run/run_backend_poetry.bat` - Backend with Poetry

### Maintenance Scripts
- `clean.bat/sh` - Clean temporary files
- `scripts/maintenance/fix_env.bat` - Fix .env issues
- `scripts/maintenance/setup_fallback.bat` - Fallback setup

---

## 🎯 Agent Categories

### Cognitive Agents (4 agents)
- **ResearchAgent**: Web research, information gathering
- **DocumentIntelligenceAgent**: Document parsing, structure extraction
- **KnowledgeSynthesisAgent**: Knowledge integration, insight generation

### Content Agents (4 agents)
- **ContentArchitectAgent**: Content structure planning
- **WritingAgent**: Content generation, drafting
- **EditingAgent**: Content refinement, language improvement

### Engineering Agents (4 agents)
- **ArchitectureAnalystAgent**: System architecture analysis
- **TechnologySelectorAgent**: Technology stack selection
- **DebateModeratorAgent**: Technical debate coordination

### Programming Agents (4 agents)
- **CodeGeneratorAgent**: Code creation, implementation
- **CodeReviewerAgent**: Code analysis, quality checks
- **DebuggerAgent**: Bug detection and fixing

### Operational Agents (4 agents)
- **WorkflowExecutorAgent**: Workflow execution
- **FileOperationsAgent**: File management
- **AutomationAgent**: Task automation

### Validation Agents (4 agents)
- **OutputValidatorAgent**: Output validation
- **ConsistencyCheckerAgent**: Consistency verification
- **FactVerifierAgent**: Fact checking

---

## 🧠 LLM Provider Management

The platform now supports 10+ LLM providers including:

**Cloud Providers:**
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3)
- Groq (Ultra-fast inference, FREE)
- Together AI (Open-source models)
- Anyscale Endpoints
- DeepInfra (Low-cost)

**Local Providers:**
- Ollama (Self-hosted)
- LM Studio (Desktop app)
- vLLM (High-throughput)
- LocalAI (OpenAI replacement)
- FastChat (Distributed serving)

**OpenAI-Compatible Providers:**
- Groq, Together AI, Anyscale, DeepInfra, LocalAI, FastChat, vLLM

**Features:**
- 🔐 Encrypted API key storage (Fernet encryption)
- 📊 Usage tracking and analytics
- 💰 Cost estimation and monitoring
- 🔄 Automatic failover between providers
- ⚡ Streaming support
- 🎯 Provider-specific optimizations

---

## 📊 Supported LLM Providers

| Provider | Type | API Key | Cost | Speed | Best For |
|----------|------|---------|------|-------|----------|
| **Groq** | Cloud | Required | **FREE** | ⚡⚡⚡⚡⚡ | Real-time apps |
| **OpenAI** | Cloud | Required | $$$ | ⚡⚡⚡ | Production quality |
| **Anthropic** | Cloud | Required | $$ | ⚡⚡⚡ | Long context |
| **Together AI** | Cloud | Required | $ | ⚡⚡⚡ | Open-source models |
| **Anyscale** | Cloud | Required | $ | ⚡⚡ | Enterprise apps |
| **DeepInfra** | Cloud | Required | ¢ | ⚡⚡ | Cost-sensitive |
| **Ollama** | Local | Optional | Free | ⚡⚡ | Development |
| **LM Studio** | Local | Optional | Free | ⚡⚡ | Desktop testing |
| **vLLM** | Local | Optional | Free | ⚡⚡⚡ | High-throughput |
| **LocalAI** | Local | Optional | Free | ⚡⚡ | Self-hosted |
| **FastChat** | Local | Optional | Free | ⚡⚡ | Research |

---

## 🔧 Tool Ecosystem

### Web Tools (4 tools)
- WebSearchTool, WebScraperTool, APIClientTool, RSSFeedTool

### Document Tools (5 tools)
- PDFParserTool, DOCXParserTool, MarkdownParserTool, TableExtractionTool, ImageOCRTool

### AI Tools (5 tools)
- LLMClientTool, EmbeddingGeneratorTool, TextClassifierTool, SummarizationTool, QuestionAnsweringTool

### Automation Tools (4 tools)
- ShellExecutorTool, GitOperationsTool, FileConverterTool, ScheduledTaskTool

### Data Tools (4 tools)
- DatabaseQueryTool, DataValidationTool, DataTransformationTool, CSVExcelTool

---

## 📊 Pre-built Workflows

### 1. Document Analysis Workflow
```
Document Ingestion → Structure Extraction → Content Analysis
→ Knowledge Extraction → Summary Generation → Validation
```

### 2. Research Workflow
```
Topic Analysis → Web Research → Information Aggregation
→ Fact Verification → Report Generation → Citation Formatting
```

### 3. Content Generation Workflow
```
Content Planning → Outline Creation → Section Drafting (parallel)
→ Content Review → Editing → Final Validation
```

### 4. Code Generation Workflow
```
Requirements Analysis → Architecture Design → Code Generation (parallel)
→ Code Review → Testing → Documentation
```

### 5. Book Generation Workflow
```
Book Planning → Chapter Outlining → Chapter Writing (parallel)
→ Cross-chapter Consistency → Editing → Formatting → Final Review
```

---

## 🎨 Frontend Features

### Dashboard Sections

1. **Agents**
   - Agent list with status indicators
   - Agent detail with metrics and logs
   - Agent creation wizard
   - Real-time status updates

2. **Workflows**
   - Workflow list and execution history
   - Visual workflow builder (React Flow)
   - Real-time progress tracking
   - Workflow controls (start, pause, resume, cancel)

3. **Tasks**
   - Kanban-style task board
   - Task assignment and tracking
   - Priority management
   - Real-time updates

4. **Knowledge**
   - Document browser
   - Knowledge graph visualization
   - Semantic search
   - Document upload

5. **Workspaces**
   - File tree viewer
   - Code editor (Monaco)
   - Terminal emulator
   - Resource monitoring

6. **LLM Providers** ⭐ NEW
   - Provider management dashboard
   - Usage statistics and charts
   - Cost tracking
   - Test connection tool

7. **Settings**
   - User profile
   - API key management
   - Integration configuration
   - Theme preferences

---

## 🔐 Authentication & Authorization

### Roles
- **Admin**: Full system access
- **Workspace Admin**: Manage own workspaces
- **User**: Execute agents and workflows
- **Service**: Service-to-service communication

### Permissions
- Agent creation, execution, management
- Workflow creation, execution, management
- Knowledge base access
- Workspace management
- API key management
- LLM provider configuration (Admin only)

---

## 📡 API Endpoints

### Authentication
```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me
```

### Agents
```
GET    /api/v1/agents                    # List agents
GET    /api/v1/agents/{id}               # Get agent details
POST   /api/v1/agents                    # Create agent
PUT    /api/v1/agents/{id}               # Update agent
DELETE /api/v1/agents/{id}               # Delete agent
POST   /api/v1/agents/{id}/execute       # Execute task
POST   /api/v1/agents/{id}/start         # Start agent
POST   /api/v1/agents/{id}/stop          # Stop agent
POST   /api/v1/agents/{id}/pause         # Pause agent
POST   /api/v1/agents/{id}/resume        # Resume agent
GET    /api/v1/agents/{id}/metrics       # Get metrics
```

### Workflows
```
GET    /api/v1/workflows                 # List workflows
GET    /api/v1/workflows/{id}            # Get workflow
POST   /api/v1/workflows                 # Create workflow
POST   /api/v1/workflows/{id}/execute    # Execute workflow
POST   /api/v1/workflows/{id}/pause      # Pause workflow
POST   /api/v1/workflows/{id}/resume     # Resume workflow
POST   /api/v1/workflows/{id}/cancel     # Cancel workflow
GET    /api/v1/workflows/{id}/history    # Execution history
GET    /api/v1/workflows/{id}/progress   # Real-time progress
```

### LLM Providers ⭐ NEW
```
GET    /api/v1/llm-providers             # List all providers
GET    /api/v1/llm-providers/{id}        # Get provider details
POST   /api/v1/llm-providers             # Create new provider
PUT    /api/v1/llm-providers/{id}        # Update provider
DELETE /api/v1/llm-providers/{id}        # Delete provider
POST   /api/v1/llm-providers/{id}/test   # Test connection
POST   /api/v1/llm-providers/{id}/set-default  # Set as default
GET    /api/v1/llm-providers/usage       # Usage statistics
GET    /api/v1/llm-providers/usage/logs  # Detailed usage logs
```

### Knowledge
```
GET    /api/v1/knowledge/search          # Semantic search
POST   /api/v1/knowledge/documents       # Ingest document
GET    /api/v1/knowledge/graph           # Query graph
DELETE /api/v1/knowledge/{id}            # Delete knowledge
```

### Tools
```
GET    /api/v1/tools                     # List available tools
POST   /api/v1/tools/{name}/execute      # Execute tool
GET    /api/v1/tools/{name}/schema       # Get tool schema
```

### WebSocket
```
WS     /api/v1/ws                        # Real-time events
```

---

## 📚 Documentation

### 📁 Main Documentation Hub
**Complete Documentation Index**: [docs/README.md](docs/README.md) - 22 comprehensive guides!

Documentation is organized into categories:

#### 🚀 Getting Started (5 guides)
- **[Zero-Config Setup](docs/getting-started/zero-config-setup.md)** - ⭐ Automated setup (no .env editing!)
- **[Native Setup](docs/getting-started/native-setup.md)** - Native setup (No Docker)
- **[Windows Setup](docs/getting-started/windows-setup.md)** - Windows PowerShell setup

#### 🧠 LLM Providers
- **[LLM Providers](docs/user-guides/llm-providers.md)** - Complete LLM provider setup
- **[Settings Management](docs/user-guides/settings-management.md)** - UI-based settings management

#### 🏗️ Architecture & Design
- **[Architecture](docs/architecture/architecture.md)** - Complete system architecture

#### 📦 Implementation
- **[Implementation Summary](docs/implementation/implementation-summary.md)** - Complete implementation summary

#### 🔍 Troubleshooting
- **[Troubleshooting](docs/troubleshooting/troubleshooting.md)** - Common issues and solutions

### 📖 Additional Documentation
- **[Project Structure](./PROJECT_STRUCTURE.md)** - Detailed directory structure
- **[Scripts Guide](./scripts/README.md)** - Scripts usage guide
- **Backend Docs**: [backend/README.md](backend/README.md)
- **Frontend Docs**: [frontend/README.md](frontend/README.md)

### 🎮 Interactive Documentation
- **API Docs**: http://localhost:8000/docs (when backend is running)
- **ReDoc**: http://localhost:8000/redoc (when backend is running)
- **Frontend Dashboard**: http://localhost:3000 (when frontend is running)

---

## 💰 Cost Estimation

### Cloud Provider Pricing (approximate)

| Provider | Model | Input (per 1K tokens) | Output (per 1K tokens) |
|----------|-------|----------------------|------------------------|
| **OpenAI** | gpt-4 | $0.03 | $0.06 |
| **OpenAI** | gpt-4-turbo | $0.01 | $0.03 |
| **OpenAI** | gpt-3.5-turbo | $0.0005 | $0.0015 |
| **Anthropic** | claude-3-opus | $0.015 | $0.075 |
| **Anthropic** | claude-3-sonnet | $0.003 | $0.015 |
| **Anthropic** | claude-3-haiku | $0.00025 | $0.00125 |
| **Groq** | mixtral-8x7b | Free (beta) | Free (beta) |
| **Together AI** | mixtral-8x7b | $0.0009 | $0.0009 |
| **DeepInfra** | mixtral-8x7b | $0.00024 | $0.00024 |

### Local Providers
- **Ollama**: Free (uses your hardware)
- **LM Studio**: Free (uses your hardware)
- **vLLM**: Free (uses your hardware)
- **LocalAI**: Free (uses your hardware)

**Note:** Token counting uses ~4 characters per token for English text. Monitor usage via the dashboard at http://localhost:3000/dashboard/settings/llm-providers/usage

---

## 🔒 Security Best Practices

1. **Encrypt all API keys** - Using Fernet encryption (automatic in the platform)
2. **Use environment variables** - Never hardcode secrets in code
3. **Enable HTTPS** - Always use HTTPS in production
4. **Rotate API keys** - Change API keys periodically
5. **Monitor usage** - Watch for unusual API usage patterns
6. **Set usage limits** - Configure spending limits with providers
7. **Use separate keys** - Different keys for development and production
8. **Backup encryption key** - Store ENCRYPTION_KEY securely (losing it = losing all API keys)
9. **Implement rate limiting** - Protect against abuse
10. **Audit access logs** - Regular review of access patterns

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test suite
poetry run pytest tests/test_agents/ -v
poetry run pytest tests/test_workflow/ -v
poetry run pytest tests/test_tools/ -v
poetry run pytest tests/test_llm_providers/ -v
```

### Frontend Tests

```bash
cd frontend

# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Test with coverage
npm run test:coverage
```

---

## 📦 Deployment

### Docker Deployment

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Native Deployment

#### Development
```bash
# Start all services
./start.sh          # Linux/Mac
start.bat           # Windows

# Start frontend (separate terminal)
./start-frontend.sh # Linux/Mac
start-frontend.bat  # Windows

# Stop all services
scripts/maintenance/stop.sh     # Linux/Mac
scripts\maintenance\stop.bat    # Windows

# Cleanup temporary files
./clean.sh          # Linux/Mac
clean.bat           # Windows
```

#### Production (Linux with systemd)
```bash
# Install systemd services
sudo cp scripts/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable document-analyzer-backend
sudo systemctl enable document-analyzer-frontend
sudo systemctl start document-analyzer-backend
sudo systemctl start document-analyzer-frontend
```

#### Production (PM2)
```bash
# Install PM2
npm install -g pm2

# Start services
cd backend
pm2 start ecosystem.config.js

cd ../frontend
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save
pm2 startup
```

### Production Considerations

1. **Environment Variables**: Set production values for all secrets
2. **Database**: Use managed PostgreSQL (RDS, Cloud SQL)
3. **Redis**: Use Redis cluster or managed service
4. **Temporal**: Deploy Temporal cluster or use Temporal Cloud
5. **Vector DB**: Deploy Qdrant/Pinecone cluster
6. **Load Balancer**: Configure NGINX/HAProxy
7. **SSL/TLS**: Enable HTTPS for all endpoints
8. **Monitoring**: Set up Prometheus + Grafana
9. **Logging**: Configure ELK stack or similar
10. **Backup**: Implement automated backups

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL 16+
- **Cache**: Redis 7+
- **Workflow**: Temporal.io
- **Vector DB**: Qdrant/Pinecone
- **Graph DB**: Neo4j
- **Auth**: JWT + bcrypt
- **Encryption**: Cryptography (Fernet)
- **LLM SDKs**: OpenAI, Anthropic, httpx

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS
- **Components**: Radix UI
- **State**: Zustand + TanStack Query
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Native Deployment**: systemd, PM2
- **Orchestration**: Kubernetes (production)
- **Load Balancer**: NGINX/HAProxy
- **Monitoring**: Prometheus + Grafana
- **Logging**: Loki + Promtail
- **Tracing**: Jaeger/Tempo

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

### Development Guidelines

- Follow existing code style
- Write tests for new features
- Update documentation
- Use meaningful commit messages
- Keep PRs focused and small

---

## 📞 Support

### Documentation
- **Complete Index**: [docs/README.md](docs/README.md) - 22 guides!
- **Quick Start**: [docs/getting-started/zero-config-setup.md](docs/getting-started/zero-config-setup.md)
- **Windows Users**: [docs/getting-started/windows-setup.md](docs/getting-started/windows-setup.md)
- **Troubleshooting**: [docs/troubleshooting/troubleshooting.md](docs/troubleshooting/troubleshooting.md)

### Help & Community
- **Issues**: Open an issue on GitHub
- **Discussions**: GitHub Discussions
- **Setup Help**: See [docs/getting-started/native-setup.md](docs/getting-started/native-setup.md)

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [Temporal](https://temporal.io/)
- [Radix UI](https://www.radix-ui.com/)
- And many other amazing open-source projects!

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-14  
**Status**: ✅ Production Ready  
**Project Structure**: Clean and organized  
**Documentation**: 22 comprehensive guides  
**Scripts**: 18 automation scripts  
**Setup Time**: 2-5 minutes (automated)
