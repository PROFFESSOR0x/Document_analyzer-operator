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
│  │   Web    │  │ Document │  │    AI    │  │Automation│       │
│  │  Tools   │  │  Tools   │  │  Tools   │  │  Tools   │       │
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
├── backend/                          # Python FastAPI Backend
│   ├── app/
│   │   ├── agents/                   # Agent Framework (24 agents)
│   │   │   ├── core/                 # Base agent, states, messages
│   │   │   ├── registry/             # Agent registry & factory
│   │   │   ├── orchestration/        # Orchestrator, load balancer
│   │   │   ├── cognitive/            # Research, Document, Knowledge
│   │   │   ├── content/              # Architect, Writing, Editing
│   │   │   ├── engineering/          # Analyst, Tech Selector, Debate
│   │   │   ├── programming/          # Generator, Reviewer, Debugger
│   │   │   ├── operational/          # Executor, File Ops, Automation
│   │   │   └── validation/           # Validator, Checker, Verifier
│   │   │
│   │   ├── tools/                    # Tool Ecosystem (20+ tools)
│   │   │   ├── base.py               # Base tool & registry
│   │   │   ├── web_tools.py          # Search, Scraper, API Client
│   │   │   ├── document_tools.py     # PDF, DOCX, Markdown, OCR
│   │   │   ├── ai_tools.py           # LLM, Embedding, Summarizer
│   │   │   ├── automation_tools.py   # Shell, Git, Scheduler
│   │   │   └── data_tools.py         # Database, ETL, CSV/Excel
│   │   │
│   │   ├── knowledge/                # Knowledge Infrastructure
│   │   │   ├── session_memory.py     # Short-term memory
│   │   │   ├── knowledge_repository.py # Long-term storage
│   │   │   ├── vector_store.py       # Vector database
│   │   │   ├── knowledge_graph.py    # Graph database
│   │   │   └── services.py           # Knowledge services
│   │   │
│   │   ├── workflow/                 # Workflow Engine
│   │   │   ├── engine.py             # Temporal orchestration
│   │   │   ├── activities.py         # Workflow activities
│   │   │   ├── patterns.py           # Workflow patterns
│   │   │   ├── prebuilt_workflows.py # Ready-to-use workflows
│   │   │   ├── management.py         # Lifecycle management
│   │   │   └── lightweight.py        # In-memory engine
│   │   │
│   │   ├── services/                 # Business Logic
│   │   │   ├── llm_client.py         # Multi-provider LLM client
│   │   │   ├── llm_client_openai_compatible.py  # OpenAI-compatible handler
│   │   │   ├── llm_provider_service.py  # Provider management
│   │   │   ├── agent_service.py      # Agent operations
│   │   │   └── user_service.py       # User operations
│   │   │
│   │   ├── api/                      # REST API
│   │   │   └── v1/
│   │   │       ├── routes/           # API endpoints
│   │   │       │   ├── llm_providers.py  # LLM provider routes
│   │   │       │   ├── agents.py     # Agent management
│   │   │       │   ├── workflows.py  # Workflow management
│   │   │       │   └── ...
│   │   │       └── websockets/       # WebSocket handlers
│   │   │
│   │   ├── models/                   # SQLAlchemy models
│   │   │   ├── llm_provider.py       # LLM provider model
│   │   │   ├── llm_usage.py          # Usage tracking model
│   │   │   ├── user.py, agent.py, workflow.py, ...
│   │   │
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── llm_provider.py       # LLM provider schemas
│   │   │   ├── agent.py, auth.py, ...
│   │   │
│   │   ├── db/                       # Database configuration
│   │   ├── core/                     # Core utilities
│   │   └── utils/                    # Helper functions
│   │
│   ├── tests/                        # Test suites
│   ├── alembic/                      # Database migrations
│   ├── pyproject.toml                # Dependencies
│   └── Dockerfile                    # Container config
│
├── frontend/                         # Next.js 14 Frontend
│   ├── src/
│   │   ├── app/                      # App Router pages
│   │   │   ├── dashboard/            # Dashboard sections
│   │   │   │   ├── agents/           # Agent management
│   │   │   │   ├── workflows/        # Workflow management
│   │   │   │   ├── tasks/            # Task board
│   │   │   │   ├── knowledge/        # Knowledge base
│   │   │   │   ├── workspace/        # Workspace
│   │   │   │   └── settings/         # Settings (incl. LLM providers)
│   │   │   ├── login/                # Authentication
│   │   │   └── layout.tsx            # Root layout
│   │   │
│   │   ├── components/               # UI Components
│   │   │   ├── ui/                   # Base components (Radix)
│   │   │   ├── domain/               # Domain components
│   │   │   └── layout/               # Layout components
│   │   │
│   │   ├── lib/                      # Utilities
│   │   │   ├── api-client.ts         # API integration
│   │   │   └── utils.ts              # Helper functions
│   │   │
│   │   ├── stores/                   # Zustand stores
│   │   ├── hooks/                    # React Query hooks
│   │   ├── providers/                # Context providers
│   │   └── types/                    # TypeScript types
│   │
│   ├── package.json                  # Dependencies
│   ├── tsconfig.json                 # TypeScript config
│   └── Dockerfile                    # Container config
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md               # System architecture
│   ├── AGENT_FRAMEWORK.md            # Agent framework documentation
│   ├── WORKFLOW_ENGINE.md            # Workflow engine guide
│   ├── TOOLS_AND_KNOWLEDGE.md        # Tools documentation
│   ├── API.md                        # API documentation
│   ├── LLM_SETUP_GUIDE.md            # LLM provider setup guide
│   ├── OPENAI_COMPATIBLE_GUIDE.md    # OpenAI-compatible providers guide
│   ├── LLM_IMPLEMENTATION_SUMMARY.md # LLM implementation details
│   ├── OPENAI_COMPATIBLE_IMPLEMENTATION.md  # OpenAI-compatible implementation
│   ├── VALIDATION_REPORT.md          # Code validation report
│   └── IMPLEMENTATION_SUMMARY.md     # Project implementation summary
│
├── README.md                         # Main entry point
└── docker-compose.yml                # Full stack orchestration
```

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.11+
- **Node.js**: 18+
- **Docker**: 20+ with Docker Compose
- **PostgreSQL**: 16+ (or use Docker)
- **Redis**: 7+ (or use Docker)

### 1. Clone and Setup

```bash
cd "D:\Computer-Science\Artificial-Intelligence\AI-programing\Document_analyzer-operator"
```

### 2. Start Infrastructure (Docker)

```bash
# Start PostgreSQL, Redis, and Temporal
docker-compose up -d postgres redis temporal
```

### 3. Backend Setup

```bash
cd backend

# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Generate encryption key for API key storage
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Edit .env and set:
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - ENCRYPTION_KEY (paste the generated Fernet key from above)
# - DATABASE_URL=postgresql://user:pass@localhost:5432/document_analyzer
# - REDIS_URL=redis://localhost:6379
# - DEFAULT_LLM_PROVIDER=openai

# Run migrations (creates llm_providers and llm_usage_logs tables)
poetry run alembic upgrade head

# Start backend server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend API Docs**: http://localhost:8000/docs

### 4. Frontend Setup

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

### 5. Configure LLM Providers

#### Option A: Via Frontend Dashboard

1. Navigate to: http://localhost:3000/dashboard/settings/llm-providers
2. Click **"Add Provider"**
3. Select provider type (OpenAI, Anthropic, Groq, Ollama, etc.)
4. Enter API key (if required) and configuration
5. Click **"Test Connection"** to verify
6. Click **"Save"**

#### Option B: Via API

```bash
# Add OpenAI provider
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "OpenAI GPT-4",
    "provider_type": "openai",
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-your-openai-api-key",
    "model_name": "gpt-4",
    "is_active": true,
    "config": {
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }'

# Add Groq provider (ultra-fast, free during beta)
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Groq",
    "provider_type": "openai_compatible",
    "base_url": "https://api.groq.com/openai/v1",
    "api_key": "your-groq-api-key",
    "model_name": "mixtral-8x7b-32768",
    "is_active": true
  }'

# Add Ollama (local, no API key required)
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Local Ollama",
    "provider_type": "ollama",
    "base_url": "http://localhost:11434/v1",
    "model_name": "llama2",
    "is_active": true
  }'
```

---

## 🧠 Supported LLM Providers

The platform supports 10+ LLM providers including cloud and local options:

| Provider | Type | API Key | Cost | Speed | Best For |
|----------|------|---------|------|-------|----------|
| **OpenAI** | Cloud | Required | $$$ | Fast | Production, best quality |
| **Anthropic** | Cloud | Required | $$ | Fast | Long context, safety |
| **Groq** | Cloud | Required | Free (beta) | ⚡ Ultra-Fast | Real-time apps |
| **Together AI** | Cloud | Required | $ | Fast | Open-source models |
| **Anyscale** | Cloud | Required | $ | Fast | Enterprise apps |
| **DeepInfra** | Cloud | Required | ¢ | Medium | Cost-sensitive apps |
| **Ollama** | Local | Optional | Free | Medium | Development/testing |
| **LM Studio** | Local | Optional | Free | Medium | Desktop deployment |
| **vLLM** | Local | Optional | Free | Fast | High-throughput |
| **LocalAI** | Local | Optional | Free | Medium | Self-hosted OpenAI replacement |
| **FastChat** | Local | Optional | Free | Medium | Distributed serving |

### Cloud Providers

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude 3 (Opus, Sonnet, Haiku)
- **Groq**: Mixtral, Llama 2 (ultra-fast LPU inference)
- **Together AI**: Mixtral, Mistral, RedPajama
- **Anyscale**: Mistral, Llama 2
- **DeepInfra**: Low-cost open-source models

### Local Providers

- **Ollama**: Self-hosted, easy setup
- **LM Studio**: Desktop app with GUI
- **vLLM**: High-throughput serving
- **LocalAI**: Drop-in OpenAI replacement
- **FastChat**: Distributed model serving

---

## 🎯 Features

### 🧠 LLM Provider Management

The platform now supports 10+ LLM providers with comprehensive management features:

**Features:**
- 🔐 **Encrypted API key storage** using Fernet encryption
- 📊 **Usage tracking and analytics** - monitor tokens, requests, costs
- 💰 **Cost estimation and monitoring** - real-time cost calculation
- 🔄 **Automatic failover** between providers
- ⚡ **Streaming support** for real-time responses
- 🎯 **Provider-specific optimizations** for each provider
- 📈 **Response time monitoring** and performance metrics
- 🛑 **Rate limit handling** with exponential backoff

### 🤖 Multi-Agent System

- **24 Specialized Agents** across 6 categories (all LLM-enabled):
  - **Cognitive Agents** (4): Research, Document Intelligence, Knowledge Synthesis
  - **Content Agents** (4): Architect, Writing, Editing
  - **Engineering Agents** (4): Architecture Analyst, Tech Selector, Debate Moderator
  - **Programming Agents** (4): Code Generator, Reviewer, Debugger
  - **Operational Agents** (4): Workflow Executor, File Ops, Automation
  - **Validation Agents** (4): Output Validator, Consistency Checker, Fact Verifier

### 🔧 Tool Ecosystem

- **20+ Tools** in 5 categories:
  - **Web Tools**: Search, Scraper, API Client, RSS
  - **Document Tools**: PDF, DOCX, Markdown, Table Extraction, OCR
  - **AI Tools**: LLM, Embedding, Classifier, Summarizer, QA
  - **Automation Tools**: Shell, Git, Converter, Scheduler
  - **Data Tools**: Database, Validation, Transformation, CSV/Excel

### 📊 Workflow Orchestration

- **Temporal.io-powered** durable workflows
- **5 Pre-built Workflows**:
  - Document Analysis Workflow
  - Research Workflow
  - Content Generation Workflow
  - Code Generation Workflow
  - Book Generation Workflow
- **Visual workflow builder** (React Flow)
- **Real-time progress tracking**

### 📚 Knowledge Infrastructure

- **Multi-modal storage**: Relational (PostgreSQL) + Vector (Qdrant) + Graph (Neo4j)
- **Semantic search** with embeddings
- **Knowledge graph** visualization
- **Document ingestion** pipeline
- **Version control** for knowledge entities

### 🔐 Security

- **JWT authentication** with token refresh
- **RBAC** (4 roles: Admin, Workspace Admin, User, Service)
- **Encrypted credential storage** (Fernet)
- **Password hashing** (bcrypt)
- **CORS and security headers**
- **Input validation** (Pydantic)

---

## 📊 Technology Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL 16+
- **Cache**: Redis 7+
- **Workflow**: Temporal.io
- **Vector DB**: Qdrant/Pinecone
- **Graph DB**: Neo4j
- **Auth**: JWT + bcrypt
- **Encryption**: cryptography (Fernet)
- **LLM SDKs**: openai, anthropic, httpx

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
- **Orchestration**: Kubernetes (production)
- **Load Balancer**: NGINX/HAProxy
- **Monitoring**: Prometheus + Grafana
- **Logging**: Loki + Promtail
- **Tracing**: Jaeger/Tempo

---

## 📡 API Endpoints

### Authentication
```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me
```

### LLM Providers
```
GET    /api/v1/llm-providers                 # List all providers
GET    /api/v1/llm-providers/{id}            # Get provider details
POST   /api/v1/llm-providers                 # Create provider
PUT    /api/v1/llm-providers/{id}            # Update provider
DELETE /api/v1/llm-providers/{id}            # Delete provider
POST   /api/v1/llm-providers/{id}/test       # Test connection
GET    /api/v1/llm-providers/usage           # Get usage statistics
GET    /api/v1/llm-providers/models          # List available models
```

### Usage Statistics
```
GET    /api/v1/llm-providers/usage?start_date=2026-03-01&end_date=2026-03-31
# Returns: total_requests, total_tokens, total_cost, success_rate, by_provider, by_model
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

**All 24 agents are now LLM-enabled** and can use any configured provider.

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

6. **Settings**
   - User profile
   - **LLM Provider Management** ⭐ NEW
   - **Usage Statistics Dashboard** ⭐ NEW
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
- **LLM provider configuration** ⭐ NEW
- API key management

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
11. **LLM Providers**: Configure production API keys
12. **Encryption Key**: Securely store ENCRYPTION_KEY

---

## 📚 Documentation

### Core Documentation
- **[ARCHITECTURE.md](./backend/ARCHITECTURE.md)**: Complete system architecture
- **[AGENT_FRAMEWORK.md](./backend/AGENT_FRAMEWORK.md)**: Agent framework documentation
- **[WORKFLOW_ENGINE.md](./backend/WORKFLOW_ENGINE.md)**: Workflow engine guide
- **[TOOLS_AND_KNOWLEDGE.md](./backend/TOOLS_AND_KNOWLEDGE.md)**: Tools and knowledge infrastructure
- **[WORKFLOW_EXAMPLES.md](./backend/WORKFLOW_EXAMPLES.md)**: Workflow usage examples
- **[COMPONENT_USAGE.md](./frontend/COMPONENT_USAGE.md)**: Frontend component guide

### LLM Documentation ⭐ NEW
- **[LLM_SETUP_GUIDE.md](./LLM_SETUP_GUIDE.md)**: Complete LLM provider setup guide
- **[OPENAI_COMPATIBLE_GUIDE.md](./OPENAI_COMPATIBLE_GUIDE.md)**: OpenAI-compatible providers guide
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)**: Implementation summary

### API Documentation
- **Interactive API Docs**: http://localhost:8000/docs
- **API Reference**: See [API Endpoints](#-api-endpoints) section

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

1. **Never commit API keys to version control**
2. **Use environment variables** for encryption key and secrets
3. **Enable HTTPS** in production
4. **Rotate API keys** periodically
5. **Monitor usage** for anomalies via the usage dashboard
6. **Set usage limits** with your provider
7. **Use separate keys** for development and production
8. **Backup encryption key** securely (losing it = losing all API keys)
9. **Use encrypted storage** for all sensitive credentials
10. **Implement rate limiting** to prevent abuse

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
- Test LLM integrations with multiple providers

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [Temporal](https://temporal.io/)
- [Radix UI](https://www.radix-ui.com/)
- [OpenAI](https://openai.com/)
- [Anthropic](https://anthropic.com/)
- [Groq](https://groq.com/)
- [Ollama](https://ollama.ai/)
- And many other amazing open-source projects!

---

## 📞 Support

For questions and support:
- Open an issue on GitHub
- Check documentation in `/docs` and root directory
- Review API docs at http://localhost:8000/docs
- See LLM guides: [LLM_SETUP_GUIDE.md](./LLM_SETUP_GUIDE.md), [OPENAI_COMPATIBLE_GUIDE.md](./OPENAI_COMPATIBLE_GUIDE.md)

---

**Version**: 1.0.0
**Last Updated**: 2026-03-13
**Status**: Production Ready
**LLM Providers**: 10+ supported (OpenAI, Anthropic, Groq, Ollama, LocalAI, vLLM, Together AI, Anyscale, DeepInfra, LM Studio, FastChat)
