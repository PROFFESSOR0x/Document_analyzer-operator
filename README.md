# Document-Analyzer-Operator Platform

## 🎯 Project Overview

The **Document-Analyzer-Operator Platform** is a large-scale autonomous agent ecosystem designed for intelligent document analysis, knowledge synthesis, content generation, and complex workflow orchestration through multi-agent collaboration.

### Core Capabilities

- **Multi-Agent Collaboration**: 24+ specialized agents across 6 categories
- **Autonomous Workflow Orchestration**: Temporal.io-powered durable workflows
- **Document Intelligence**: PDF, DOCX, Markdown parsing with OCR support
- **Knowledge Management**: Vector search, graph-based knowledge, semantic search
- **Content Generation**: Academic writing, technical documentation, code generation
- **Research Automation**: Web research, fact verification, citation management
- **Tool Ecosystem**: 20+ tools for web, AI, automation, and data operations

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
│   │   ├── api/                      # REST API
│   │   │   └── v1/
│   │   │       ├── routes/           # API endpoints
│   │   │       └── websockets/       # WebSocket handlers
│   │   │
│   │   ├── models/                   # SQLAlchemy models
│   │   ├── schemas/                  # Pydantic schemas
│   │   ├── services/                 # Business logic
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
│   │   │   │   └── workspace/        # Workspace
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
│   ├── AGENT_FRAMEWORK.md            # Agent documentation
│   ├── WORKFLOW_ENGINE.md            # Workflow documentation
│   ├── TOOLS_AND_KNOWLEDGE.md        # Tools documentation
│   └── API.md                        # API documentation
│
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

# Edit .env and set:
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - DATABASE_URL=postgresql://user:pass@localhost:5432/document_analyzer
# - REDIS_URL=redis://localhost:6379

# Run migrations
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

---

## 📚 Documentation

- **[ARCHITECTURE.md](./backend/ARCHITECTURE.md)**: Complete system architecture
- **[AGENT_FRAMEWORK.md](./backend/AGENT_FRAMEWORK.md)**: Agent framework documentation
- **[WORKFLOW_ENGINE.md](./backend/WORKFLOW_ENGINE.md)**: Workflow engine guide
- **[TOOLS_AND_KNOWLEDGE.md](./backend/TOOLS_AND_KNOWLEDGE.md)**: Tools and knowledge infrastructure
- **[WORKFLOW_EXAMPLES.md](./backend/WORKFLOW_EXAMPLES.md)**: Workflow usage examples
- **[COMPONENT_USAGE.md](./frontend/COMPONENT_USAGE.md)**: Frontend component guide

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

## 📝 License

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

## 📞 Support

For questions and support:
- Open an issue on GitHub
- Check documentation in `/docs`
- Review API docs at http://localhost:8000/docs

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-13  
**Status**: Production Ready
