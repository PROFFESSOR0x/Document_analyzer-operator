# Workflow Engine Documentation

Comprehensive workflow orchestration system using Temporal.io for durable execution of multi-stage workflows involving multiple agents.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Workflow Core](#workflow-core)
6. [Workflow Activities](#workflow-activities)
7. [Workflow Patterns](#workflow-patterns)
8. [Pre-built Workflows](#pre-built-workflows)
9. [Workflow Management](#workflow-management)
10. [API Reference](#api-reference)
11. [Integration](#integration)
12. [Temporal Setup](#temporal-setup)
13. [Testing](#testing)
14. [Known Limitations](#known-limitations)

## Overview

The Workflow Engine provides:

- **Durable Execution**: Workflows survive process restarts and failures
- **Multi-Agent Orchestration**: Coordinate multiple AI agents in complex workflows
- **Temporal.io Integration**: Production-grade workflow orchestration
- **Lightweight Mode**: In-memory engine for development and testing
- **Pre-built Workflows**: Ready-to-use workflows for common scenarios
- **Real-time Monitoring**: Track workflow progress via WebSocket events

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│                    FastAPI Workflow API                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Workflow Management Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Workflow   │  │  Workflow   │  │     Workflow            │  │
│  │   Manager   │  │  Scheduler  │  │      Monitor            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Workflow Engine Layer                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    WorkflowEngine                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │  │
│  │  │  Temporal   │  │  Lightweight│  │   Integration   │   │  │
│  │  │   Client    │  │   Engine    │  │   Components    │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Workflow Definitions Layer                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Patterns   │  │  Pre-built  │  │    Custom Workflows     │  │
│  │             │  │  Workflows  │  │                         │  │
│  │ - Sequential│  │ - Document  │  │   (User Defined)        │  │
│  │ - Parallel  │  │ - Research  │  │                         │  │
│  │ - Conditional│ │ - Content   │  │                         │  │
│  │ - Pipeline  │  │ - Code      │  │                         │  │
│  │ - Stateful  │  │ - Book      │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Activities Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Agent     │  │   Tool      │  │     Validation          │  │
│  │  Activity   │  │  Activity   │  │      Activity           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Parallel   │  │  Sequential │  │     Conditional         │  │
│  │  Activity   │  │  Activity   │  │      Activity           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Integration Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Agent     │  │  Knowledge  │  │    WebSocket            │  │
│  │ Integration │  │ Integration │  │    Integration          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

### 1. Add Dependencies

Add to `pyproject.toml`:

```toml
[tool.poetry.dependencies]
temporalio = "^1.4.0"
croniter = "^2.0.0"
```

Install:

```bash
cd backend
poetry install
```

### 2. Start Temporal Server

**Development (Docker):**

```bash
docker run --rm --name temporal \
  -p 7233:7233 \
  temporalio/auto-setup:latest
```

**Production:**

See [Temporal Setup Instructions](#temporal-setup)

### 3. Configure Environment

Add to `.env`:

```env
# Temporal Configuration
TEMPORAL_HOST=localhost
TEMPORAL_PORT=7233
TEMPORAL_TASK_QUEUE=workflow-queue
```

## Quick Start

### Basic Workflow Execution

```python
from app.workflow import WorkflowEngine, DocumentAnalysisWorkflow

# Initialize engine
engine = WorkflowEngine(
    temporal_host="localhost",
    temporal_port=7233,
    task_queue="workflow-queue",
)

# Connect to Temporal
await engine.connect()

# Register workflow
engine.register_workflow(DocumentAnalysisWorkflow)

# Start worker (in a separate task)
asyncio.create_task(engine.start_worker())

# Execute workflow
run_id = await engine.execute_workflow(
    workflow_id="doc-analysis-001",
    workflow_type="DocumentAnalysisWorkflow",
    input_data={
        "document_id": "doc-123",
        "document_path": "/path/to/document.pdf",
        "analysis_config": {"extract_entities": True},
    },
)

print(f"Workflow started with run_id: {run_id}")
```

### Using Workflow Manager

```python
from app.workflow import WorkflowEngine, WorkflowManager

# Initialize
engine = WorkflowEngine()
await engine.connect()

manager = WorkflowManager(engine)

# Register workflow definition
from app.workflow import WorkflowDefinition

definition = WorkflowDefinition(
    name="Document Analysis",
    description="Analyze documents",
    tasks=[...],
)
manager.register_definition(definition)

# Create and start workflow
execution = await manager.create_workflow(
    workflow_type="DocumentAnalysisWorkflow",
    input_data={"document_id": "doc-123"},
)

run_id = await manager.start_workflow(execution.execution_id)
```

### Lightweight Mode (Development)

```python
from app.workflow.lightweight import LightweightWorkflowEngine

# Create engine (no Temporal required)
engine = LightweightWorkflowEngine()

# Register workflow function
async def my_workflow(input_data):
    return {"result": "completed"}

engine.register_workflow("my_workflow", my_workflow)

# Execute
execution_id = await engine.execute(
    workflow_type="my_workflow",
    input_data={"key": "value"},
)

# Get status
status = await engine.get_status(execution_id)
print(f"Status: {status.status.value}")
```

## Workflow Core

### WorkflowEngine

Main orchestration engine for Temporal.io workflows.

```python
class WorkflowEngine:
    """Main orchestration engine."""

    def __init__(
        self,
        temporal_host: str = "localhost",
        temporal_port: int = 7233,
        task_queue: str = "workflow-queue",
    ) -> None:
        ...

    async def connect(self) -> None:
        """Connect to Temporal server."""
        ...

    def register_workflow(self, workflow_class: type) -> None:
        """Register a workflow definition."""
        ...

    async def execute_workflow(
        self,
        workflow_id: str,
        workflow_type: str,
        input_data: dict[str, Any],
    ) -> str:
        """Execute a workflow."""
        ...
```

### WorkflowDefinition

Workflow structure and configuration.

```python
@dataclass
class WorkflowDefinition:
    """Workflow structure and configuration."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: Optional[str] = None
    version: str = "1.0.0"
    tasks: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)
    retry_policy: Optional[dict[str, Any]] = None
    timeout: Optional[int] = None
```

### WorkflowState

State management for workflows.

```python
@dataclass
class WorkflowState:
    """State management for workflows."""

    workflow_id: str
    definition_id: str
    status: WorkflowStatus
    priority: WorkflowPriority
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    current_task: Optional[str]
    completed_tasks: list[str]
    failed_tasks: list[str]
    progress: int
    error_message: Optional[str]
```

### WorkflowStatus

```python
class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
```

## Workflow Activities

Activities are the building blocks of workflows.

### Agent Activity

Execute a single agent task.

```python
@activity.defn
async def agent_activity(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a single agent task.

    Input:
        - agent_id: Agent ID to execute
        - task_type: Type of task
        - payload: Task payload

    Output:
        - status: Execution status
        - output_data: Agent result
    """
```

### Parallel Activity

Execute multiple activities in parallel.

```python
@activity.defn
async def parallel_activity(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute multiple activities in parallel.

    Input:
        - activities: List of activity definitions
        - fail_fast: Whether to fail on first error
    """
```

### Validation Activity

Validate activity outputs.

```python
@activity.defn
async def validation_activity(input_data: dict[str, Any]) -> dict[str, Any]:
    """Validate activity outputs.

    Input:
        - data: Data to validate
        - schema: Validation schema
        - rules: Validation rules
    """
```

## Workflow Patterns

### Sequential Workflow

Linear task execution.

```python
from app.workflow import SequentialWorkflow

engine.register_workflow(SequentialWorkflow)

# Execute
await engine.execute_workflow(
    workflow_id="seq-001",
    workflow_type="SequentialWorkflow",
    input_data={
        "tasks": [
            {"id": "task1", "type": "agent_activity", "config": {...}},
            {"id": "task2", "type": "agent_activity", "config": {...}},
        ],
        "initial_data": {...},
    },
)
```

### Parallel Workflow

Fan-out/fan-in pattern.

```python
from app.workflow import ParallelWorkflow

engine.register_workflow(ParallelWorkflow)

# Execute
await engine.execute_workflow(
    workflow_id="parallel-001",
    workflow_type="ParallelWorkflow",
    input_data={
        "tasks": [...],
        "aggregation_strategy": "all",
        "fail_fast": False,
    },
)
```

### Conditional Workflow

Branching based on conditions.

```python
from app.workflow import ConditionalWorkflow

engine.register_workflow(ConditionalWorkflow)

# Execute
await engine.execute_workflow(
    workflow_id="conditional-001",
    workflow_type="ConditionalWorkflow",
    input_data={
        "conditions": [
            {"name": "high_priority", "expression": "priority > 5"},
        ],
        "branches": {
            "high_priority": {"type": "sequential", "tasks": [...]},
        },
        "default_branch": {...},
        "context": {"priority": 8},
    },
)
```

### Pipeline Workflow

Data pipeline pattern.

```python
from app.workflow import PipelineWorkflow

engine.register_workflow(PipelineWorkflow)

# Execute
await engine.execute_workflow(
    workflow_id="pipeline-001",
    workflow_type="PipelineWorkflow",
    input_data={
        "stages": [
            {"id": "extract", "type": "agent_activity", "config": {...}},
            {"id": "transform", "type": "agent_activity", "config": {...}},
            {"id": "load", "type": "agent_activity", "config": {...}},
        ],
        "input_data": {...},
    },
)
```

## Pre-built Workflows

### Document Analysis Workflow

Complete document analysis pipeline.

```python
from app.workflow import DocumentAnalysisWorkflow

engine.register_workflow(DocumentAnalysisWorkflow)

result = await engine.execute_workflow(
    workflow_id="doc-analysis-001",
    workflow_type="DocumentAnalysisWorkflow",
    input_data={
        "document_id": "doc-123",
        "document_path": "/path/to/document.pdf",
        "analysis_config": {"extract_entities": True},
        "extraction_types": ["entities", "relationships", "events"],
    },
)

# Result structure:
# {
#     "document_id": "doc-123",
#     "stages": {
#         "ingestion": {...},
#         "structure": {...},
#         "analysis": {...},
#         "knowledge": {...},
#         "summary": {...},
#         "validation": {...},
#     },
#     "final": {...},
# }
```

### Research Workflow

Comprehensive research workflow.

```python
from app.workflow import ResearchWorkflow

engine.register_workflow(ResearchWorkflow)

result = await engine.execute_workflow(
    workflow_id="research-001",
    workflow_type="ResearchWorkflow",
    input_data={
        "topic": "AI Safety",
        "sources": ["web", "academic", "news"],
        "depth": "deep",
        "research_config": {"citation_style": "apa"},
    },
)
```

### Content Generation Workflow

Generate content with multiple sections.

```python
from app.workflow import ContentGenerationWorkflow

engine.register_workflow(ContentGenerationWorkflow)

result = await engine.execute_workflow(
    workflow_id="content-001",
    workflow_type="ContentGenerationWorkflow",
    input_data={
        "topic": "Introduction to Machine Learning",
        "content_type": "article",
        "target_audience": "beginners",
        "length": "long",
        "tone": "friendly",
    },
)
```

### Code Generation Workflow

Generate code with multiple modules.

```python
from app.workflow import CodeGenerationWorkflow

engine.register_workflow(CodeGenerationWorkflow)

result = await engine.execute_workflow(
    workflow_id="code-001",
    workflow_type="CodeGenerationWorkflow",
    input_data={
        "requirements": {"description": "REST API for user management"},
        "tech_stack": {"language": "python", "framework": "fastapi"},
        "modules": [
            {"name": "models", "description": "Database models"},
            {"name": "routes", "description": "API routes"},
            {"name": "services", "description": "Business logic"},
        ],
        "coding_standards": {"style": "pep8"},
    },
)
```

### Book Generation Workflow

Generate complete books.

```python
from app.workflow import BookGenerationWorkflow

engine.register_workflow(BookGenerationWorkflow)

result = await engine.execute_workflow(
    workflow_id="book-001",
    workflow_type="BookGenerationWorkflow",
    input_data={
        "book_title": "Introduction to Python",
        "genre": "technical",
        "target_audience": "beginners",
        "chapter_count": 12,
        "writing_style": "educational",
    },
)
```

## Workflow Management

### WorkflowManager

Create, start, pause, resume, cancel workflows.

```python
from app.workflow import WorkflowManager, WorkflowEngine

engine = WorkflowEngine()
await engine.connect()
manager = WorkflowManager(engine)

# Create workflow
execution = await manager.create_workflow(
    workflow_type="DocumentAnalysisWorkflow",
    input_data={"document_id": "doc-123"},
)

# Start workflow
run_id = await manager.start_workflow(execution.execution_id)

# Pause workflow
await manager.pause_workflow(execution.execution_id)

# Resume workflow
await manager.resume_workflow(execution.execution_id)

# Cancel workflow
await manager.cancel_workflow(execution.execution_id)

# Get status
state = await manager.get_workflow_status(execution.execution_id)
```

### WorkflowScheduler

Schedule workflows with cron expressions.

```python
from app.workflow import WorkflowScheduler, WorkflowManager

scheduler = WorkflowScheduler(manager)
await scheduler.start()

# Schedule daily workflow
schedule_id = scheduler.schedule_workflow(
    workflow_type="DocumentAnalysisWorkflow",
    cron_expression="0 9 * * *",  # Daily at 9 AM
    input_data={"document_id": "daily-doc"},
)

# Unscheduled
scheduler.unschedule_workflow(schedule_id)
```

### WorkflowMonitor

Monitor workflow health and progress.

```python
from app.workflow import WorkflowMonitor, WorkflowManager

monitor = WorkflowMonitor(manager)
await monitor.start()

# Get progress
progress = await monitor.get_workflow_progress(execution_id)
print(f"Progress: {progress['progress']}%")

# Check health
health = await monitor.check_health()
print(f"System healthy: {health['healthy']}")

# Get metrics
metrics = monitor.metrics
print(f"Total executions: {metrics['total_executions']}")
```

## API Reference

### Workflow Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/workflows` | Create workflow |
| GET | `/api/v1/workflows` | List workflows |
| GET | `/api/v1/workflows/{id}` | Get workflow details |
| POST | `/api/v1/workflows/{id}/execute` | Start execution |
| POST | `/api/v1/workflows/{id}/pause` | Pause execution |
| POST | `/api/v1/workflows/{id}/resume` | Resume execution |
| POST | `/api/v1/workflows/{id}/cancel` | Cancel execution |
| GET | `/api/v1/workflows/{id}/history` | Get execution history |
| GET | `/api/v1/workflows/{id}/progress` | Get real-time progress |
| POST | `/api/v1/workflows/schedule` | Schedule recurring workflow |
| DELETE | `/api/v1/workflows/schedule/{id}` | Remove schedule |
| GET | `/api/v1/workflows/monitor/health` | Get health status |
| GET | `/api/v1/workflows/monitor/metrics` | Get metrics |

### Example API Usage

```bash
# Create workflow
curl -X POST "http://localhost:8000/api/v1/workflows" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "DocumentAnalysisWorkflow",
    "input_data": {"document_id": "doc-123"}
  }'

# Start execution
curl -X POST "http://localhost:8000/api/v1/workflows/{execution_id}/execute" \
  -H "Authorization: Bearer $TOKEN"

# Get progress
curl "http://localhost:8000/api/v1/workflows/{execution_id}/progress" \
  -H "Authorization: Bearer $TOKEN"
```

## Integration

### Agent Integration

```python
from app.workflow.integration import AgentIntegration

agent_integration = AgentIntegration(
    agent_orchestrator=orchestrator,
    agent_service=agent_service,
)

result = await agent_integration.execute_agent_task(
    agent_id="research-agent",
    task_type="research_topic",
    payload={"topic": "AI Safety"},
    timeout=300,
)
```

### Knowledge Integration

```python
from app.workflow.integration import KnowledgeIntegration

knowledge_integration = KnowledgeIntegration(
    knowledge_service=knowledge_service,
)

# Store knowledge
entity_id = await knowledge_integration.store_knowledge(
    entity_type="document",
    entity_data={"title": "AI Safety Report"},
    workspace_id="ws-123",
)

# Retrieve knowledge
entities = await knowledge_integration.retrieve_knowledge(
    entity_type="document",
    query="AI Safety",
    limit=10,
)
```

### WebSocket Integration

```python
from app.workflow.integration import WebSocketIntegration

ws_integration = WebSocketIntegration(
    websocket_manager=websocket_manager,
    event_publisher=event_publisher,
)

# Notify progress
await ws_integration.notify_workflow_progress(
    workflow_id="workflow-123",
    progress=50,
    current_task="analyzing",
    user_id="user-456",
)
```

## Temporal Setup

### Development Setup

1. **Install Docker Desktop** (if not already installed)

2. **Start Temporal:**

```bash
docker run --rm --name temporal \
  -p 7233:7233 \
  temporalio/auto-setup:latest
```

3. **Access Temporal Web UI:**

```bash
docker run --rm --name temporal-ui \
  -p 8080:8080 \
  --env TEMPORAL_ADDRESS=temporal:7233 \
  --link temporal \
  temporalio/ui:latest
```

Visit http://localhost:8080

### Production Setup

1. **Use Temporal Cloud** (recommended) or self-hosted cluster

2. **Configure connection:**

```env
TEMPORAL_HOST=your-temporal-host.temporal-cloud.com
TEMPORAL_PORT=7233
TEMPORAL_NAMESPACE=your-namespace
TEMPORAL_API_KEY=your-api-key
```

3. **Set up TLS:**

```python
from temporalio.client import Client

client = await Client.connect(
    "your-host:7233",
    namespace="your-namespace",
    api_key="your-api-key",
    tls=True,
)
```

### Worker Deployment

1. **Run worker as separate service:**

```python
# worker.py
from app.workflow import init_workflow_engine, DocumentAnalysisWorkflow

async def main():
    engine = await init_workflow_engine(
        temporal_host="temporal",
        temporal_port=7233,
        task_queue="workflow-queue",
    )

    # Register all workflows
    engine.register_workflow(DocumentAnalysisWorkflow)
    # ... register other workflows

    # Start worker
    await engine.start_worker()

if __name__ == "__main__":
    asyncio.run(main())
```

2. **Deploy with Docker:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install poetry && poetry install

CMD ["python", "worker.py"]
```

## Testing

### Unit Tests

```python
import pytest
from app.workflow.lightweight import LightweightWorkflowEngine

@pytest.mark.asyncio
async def test_sequential_workflow():
    engine = LightweightWorkflowEngine()

    async def task1(data):
        return {"step": 1}

    async def task2(data):
        return {"step": 2}

    engine.register_workflow("test", lambda d: {"result": "ok"})

    execution_id = await engine.execute("test", {})
    status = await engine.get_status(execution_id)

    assert status.status.value == "completed"
```

### Integration Tests

```python
import pytest
from app.workflow import WorkflowEngine, SequentialWorkflow

@pytest.mark.asyncio
async def test_temporal_workflow():
    engine = WorkflowEngine()

    try:
        await engine.connect()
        engine.register_workflow(SequentialWorkflow)

        # Start worker in background
        worker_task = asyncio.create_task(engine.start_worker())

        # Give worker time to start
        await asyncio.sleep(1)

        # Execute workflow
        run_id = await engine.execute_workflow(
            workflow_id="test-001",
            workflow_type="SequentialWorkflow",
            input_data={"tasks": []},
        )

        assert run_id is not None

    finally:
        await engine.shutdown()
        worker_task.cancel()
```

## Known Limitations

1. **Temporal Dependency**: Production workflows require Temporal server
2. **Agent Integration**: Placeholder implementations need actual agent framework integration
3. **Message Persistence**: Workflow messages not persisted by default
4. **Distributed Agents**: Assumes single-process deployment
5. **Resource Limits**: No built-in resource quota management

### TODOs

- [ ] Add message persistence layer
- [ ] Implement distributed agent support
- [ ] Add LLM provider integration
- [ ] Implement resource quota management
- [ ] Add workflow versioning and migration
- [ ] Implement workflow templates library
- [ ] Add comprehensive monitoring dashboard
- [ ] Implement workflow collaboration patterns
- [ ] Add retry policies configuration
- [ ] Implement circuit breaker pattern
- [ ] Add workflow analytics and reporting
- [ ] Implement workflow debugging tools
- [ ] Add workflow simulation mode
- [ ] Implement workflow cost tracking

## Support

For issues and questions:
- Check existing issues in the repository
- Review Temporal documentation: https://docs.temporal.io
- Contact the development team
