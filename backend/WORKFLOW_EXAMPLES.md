# Workflow Engine Usage Examples

This document provides comprehensive usage examples for the Workflow Engine.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Workflow Patterns](#workflow-patterns)
3. [Pre-built Workflows](#pre-built-workflows)
4. [Management Examples](#management-examples)
5. [API Examples](#api-examples)
6. [Integration Examples](#integration-examples)
7. [Advanced Examples](#advanced-examples)

## Basic Examples

### Example 1: Simple Workflow Execution

```python
import asyncio
from app.workflow import WorkflowEngine, DocumentAnalysisWorkflow

async def main():
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

    # Start worker in background
    worker_task = asyncio.create_task(engine.start_worker())

    # Give worker time to start
    await asyncio.sleep(1)

    # Execute workflow
    run_id = await engine.execute_workflow(
        workflow_id="doc-analysis-001",
        workflow_type="DocumentAnalysisWorkflow",
        input_data={
            "document_id": "doc-123",
            "document_path": "/path/to/document.pdf",
            "analysis_config": {"extract_entities": True},
            "extraction_types": ["entities", "relationships"],
        },
    )

    print(f"Workflow started with run_id: {run_id}")

    # Wait for worker (in real app, you'd poll for status)
    # await worker_task

asyncio.run(main())
```

### Example 2: Lightweight Mode (Development)

```python
import asyncio
from app.workflow.lightweight import LightweightWorkflowEngine

async def main():
    # Create engine (no Temporal required)
    engine = LightweightWorkflowEngine(max_concurrent=5)

    # Define a simple workflow
    async def simple_workflow(input_data):
        print(f"Processing: {input_data}")
        await asyncio.sleep(1)  # Simulate work
        return {
            "result": "completed",
            "processed_data": input_data,
        }

    # Register workflow
    engine.register_workflow("simple_workflow", simple_workflow)

    # Execute workflow
    execution_id = await engine.execute(
        workflow_type="simple_workflow",
        input_data={"key": "value", "number": 42},
    )

    print(f"Execution ID: {execution_id}")

    # Get status
    status = await engine.get_status(execution_id)
    print(f"Status: {status.status.value}")
    print(f"Output: {status.output_data}")

asyncio.run(main())
```

### Example 3: Workflow with Error Handling

```python
import asyncio
from app.workflow import WorkflowEngine

async def main():
    engine = WorkflowEngine()

    try:
        await engine.connect()
        engine.register_workflow(DocumentAnalysisWorkflow)

        # Start worker
        worker_task = asyncio.create_task(engine.start_worker())
        await asyncio.sleep(1)

        # Execute with error handling
        try:
            run_id = await engine.execute_workflow(
                workflow_id="doc-analysis-002",
                workflow_type="DocumentAnalysisWorkflow",
                input_data={
                    "document_id": "doc-456",
                    "document_path": "/path/to/missing.pdf",
                },
            )
        except Exception as e:
            print(f"Failed to start workflow: {e}")

    except Exception as e:
        print(f"Engine error: {e}")
    finally:
        await engine.shutdown()

asyncio.run(main())
```

## Workflow Patterns

### Example 4: Sequential Workflow

```python
from app.workflow import WorkflowEngine, SequentialWorkflow

async def run_sequential():
    engine = WorkflowEngine()
    await engine.connect()
    engine.register_workflow(SequentialWorkflow)

    asyncio.create_task(engine.start_worker())
    await asyncio.sleep(1)

    # Define sequential tasks
    tasks = [
        {
            "id": "task-1",
            "type": "agent_activity",
            "config": {
                "agent_id": "research-agent",
                "task_type": "gather_info",
                "payload": {"topic": "AI"},
            },
        },
        {
            "id": "task-2",
            "type": "agent_activity",
            "config": {
                "agent_id": "analysis-agent",
                "task_type": "analyze",
                "payload": {},
            },
        },
        {
            "id": "task-3",
            "type": "validation_activity",
            "config": {
                "rules": [{"type": "required_field", "field": "result"}],
            },
        },
    ]

    run_id = await engine.execute_workflow(
        workflow_id="sequential-001",
        workflow_type="SequentialWorkflow",
        input_data={
            "tasks": tasks,
            "initial_data": {"start_time": "now"},
            "pass_output": True,
        },
    )

    print(f"Sequential workflow started: {run_id}")

asyncio.run(run_sequential())
```

### Example 5: Parallel Workflow

```python
from app.workflow import WorkflowEngine, ParallelWorkflow

async def run_parallel():
    engine = WorkflowEngine()
    await engine.connect()
    engine.register_workflow(ParallelWorkflow)

    asyncio.create_task(engine.start_worker())
    await asyncio.sleep(1)

    # Define parallel tasks
    tasks = [
        {
            "id": "research-web",
            "type": "agent_activity",
            "config": {
                "agent_id": "web-research-agent",
                "task_type": "research",
                "payload": {"source": "web", "topic": "AI"},
            },
        },
        {
            "id": "research-academic",
            "type": "agent_activity",
            "config": {
                "agent_id": "academic-research-agent",
                "task_type": "research",
                "payload": {"source": "academic", "topic": "AI"},
            },
        },
        {
            "id": "research-news",
            "type": "agent_activity",
            "config": {
                "agent_id": "news-research-agent",
                "task_type": "research",
                "payload": {"source": "news", "topic": "AI"},
            },
        },
    ]

    run_id = await engine.execute_workflow(
        workflow_id="parallel-001",
        workflow_type="ParallelWorkflow",
        input_data={
            "tasks": tasks,
            "aggregation_strategy": "merge",
            "fail_fast": False,
        },
    )

    print(f"Parallel workflow started: {run_id}")

asyncio.run(run_parallel())
```

### Example 6: Conditional Workflow

```python
from app.workflow import WorkflowEngine, ConditionalWorkflow

async def run_conditional():
    engine = WorkflowEngine()
    await engine.connect()
    engine.register_workflow(ConditionalWorkflow)

    asyncio.create_task(engine.start_worker())
    await asyncio.sleep(1)

    run_id = await engine.execute_workflow(
        workflow_id="conditional-001",
        workflow_type="ConditionalWorkflow",
        input_data={
            "conditions": [
                {
                    "name": "high_priority",
                    "expression": "priority > 5",
                },
                {
                    "name": "urgent",
                    "expression": "urgent == True",
                },
            ],
            "branches": {
                "high_priority": {
                    "type": "sequential",
                    "tasks": [
                        {
                            "id": "urgent-task",
                            "type": "agent_activity",
                            "config": {"agent_id": "priority-agent"},
                        }
                    ],
                },
                "urgent": {
                    "type": "sequential",
                    "tasks": [
                        {
                            "id": "urgent-task",
                            "type": "agent_activity",
                            "config": {"agent_id": "urgent-agent"},
                        }
                    ],
                },
            },
            "default_branch": {
                "type": "sequential",
                "tasks": [
                    {
                        "id": "normal-task",
                        "type": "agent_activity",
                        "config": {"agent_id": "normal-agent"},
                    }
                ],
            },
            "context": {
                "priority": 8,
                "urgent": False,
            },
        },
    )

    print(f"Conditional workflow started: {run_id}")

asyncio.run(run_conditional())
```

## Pre-built Workflows

### Example 7: Document Analysis Workflow

```python
from app.workflow import WorkflowEngine, DocumentAnalysisWorkflow

async def analyze_document():
    engine = WorkflowEngine()
    await engine.connect()
    engine.register_workflow(DocumentAnalysisWorkflow)

    asyncio.create_task(engine.start_worker())
    await asyncio.sleep(1)

    result = await engine.execute_workflow(
        workflow_id="doc-analysis-003",
        workflow_type="DocumentAnalysisWorkflow",
        input_data={
            "document_id": "research-paper-001",
            "document_path": "/documents/ai-research.pdf",
            "analysis_config": {
                "extract_entities": True,
                "extract_relationships": True,
                "summarize": True,
            },
            "extraction_types": [
                "entities",
                "relationships",
                "events",
                "concepts",
            ],
        },
    )

    print(f"Document analysis started: {result}")

asyncio.run(analyze_document())
```

### Example 8: Research Workflow

```python
from app.workflow import WorkflowEngine, ResearchWorkflow

async def conduct_research():
    engine = WorkflowEngine()
    await engine.connect()
    engine.register_workflow(ResearchWorkflow)

    asyncio.create_task(engine.start_worker())
    await asyncio.sleep(1)

    result = await engine.execute_workflow(
        workflow_id="research-001",
        workflow_type="ResearchWorkflow",
        input_data={
            "topic": "Machine Learning Safety",
            "research_config": {
                "citation_style": "apa",
                "min_sources": 10,
                "include_recent": True,
            },
            "sources": ["web", "academic", "news", "arxiv"],
            "depth": "deep",  # shallow, medium, deep
        },
    )

    print(f"Research workflow started: {result}")

asyncio.run(conduct_research())
```

### Example 9: Content Generation Workflow

```python
from app.workflow import WorkflowEngine, ContentGenerationWorkflow

async def generate_content():
    engine = WorkflowEngine()
    await engine.connect()
    engine.register_workflow(ContentGenerationWorkflow)

    asyncio.create_task(engine.start_worker())
    await asyncio.sleep(1)

    result = await engine.execute_workflow(
        workflow_id="content-001",
        workflow_type="ContentGenerationWorkflow",
        input_data={
            "topic": "Introduction to Neural Networks",
            "content_type": "article",
            "target_audience": "beginners",
            "length": "long",
            "tone": "friendly",
        },
    )

    print(f"Content generation started: {result}")

asyncio.run(generate_content())
```

### Example 10: Code Generation Workflow

```python
from app.workflow import WorkflowEngine, CodeGenerationWorkflow

async def generate_code():
    engine = WorkflowEngine()
    await engine.connect()
    engine.register_workflow(CodeGenerationWorkflow)

    asyncio.create_task(engine.start_worker())
    await asyncio.sleep(1)

    result = await engine.execute_workflow(
        workflow_id="code-gen-001",
        workflow_type="CodeGenerationWorkflow",
        input_data={
            "requirements": {
                "description": "REST API for user management",
                "features": [
                    "user registration",
                    "authentication",
                    "profile management",
                ],
            },
            "tech_stack": {
                "language": "python",
                "framework": "fastapi",
                "database": "postgresql",
                "orm": "sqlalchemy",
            },
            "modules": [
                {"name": "models", "description": "Database models"},
                {"name": "schemas", "description": "Pydantic schemas"},
                {"name": "routes", "description": "API routes"},
                {"name": "services", "description": "Business logic"},
            ],
            "coding_standards": {
                "style": "pep8",
                "type_hints": True,
                "docstrings": "google",
            },
        },
    )

    print(f"Code generation started: {result}")

asyncio.run(generate_code())
```

## Management Examples

### Example 11: Workflow Manager

```python
from app.workflow import WorkflowEngine, WorkflowManager

async def use_workflow_manager():
    engine = WorkflowEngine()
    await engine.connect()
    manager = WorkflowManager(engine)

    # Create workflow
    execution = await manager.create_workflow(
        workflow_type="DocumentAnalysisWorkflow",
        input_data={
            "document_id": "doc-789",
            "document_path": "/docs/report.pdf",
        },
        context={"user_id": "user-123"},
        metadata={"priority": "high"},
    )

    print(f"Created execution: {execution.execution_id}")

    # Start workflow
    run_id = await manager.start_workflow(execution.execution_id)
    print(f"Started workflow: {run_id}")

    # Check status
    state = await manager.get_workflow_status(execution.execution_id)
    print(f"Status: {state.status.value}, Progress: {state.progress}%")

    # Pause workflow
    await manager.pause_workflow(execution.execution_id)
    print("Workflow paused")

    # Resume workflow
    await manager.resume_workflow(execution.execution_id)
    print("Workflow resumed")

    # Cancel workflow (if needed)
    # await manager.cancel_workflow(execution.execution_id)

asyncio.run(use_workflow_manager())
```

### Example 12: Workflow Scheduler

```python
from app.workflow import WorkflowEngine, WorkflowManager, WorkflowScheduler

async def use_workflow_scheduler():
    engine = WorkflowEngine()
    await engine.connect()
    manager = WorkflowManager(engine)
    scheduler = WorkflowScheduler(manager)

    # Start scheduler
    await scheduler.start()

    # Schedule daily workflow
    daily_schedule_id = scheduler.schedule_workflow(
        workflow_type="DocumentAnalysisWorkflow",
        cron_expression="0 9 * * *",  # Daily at 9 AM
        input_data={
            "document_id": "daily-report",
            "document_path": "/docs/daily.pdf",
        },
        metadata={"schedule_type": "daily"},
    )

    print(f"Scheduled daily workflow: {daily_schedule_id}")

    # Schedule weekly workflow
    weekly_schedule_id = scheduler.schedule_workflow(
        workflow_type="ResearchWorkflow",
        cron_expression="0 10 * * 1",  # Every Monday at 10 AM
        input_data={
            "topic": "Weekly Research Summary",
            "depth": "medium",
        },
        metadata={"schedule_type": "weekly"},
    )

    print(f"Scheduled weekly workflow: {weekly_schedule_id}")

    # Disable a schedule
    scheduler.disable_schedule(daily_schedule_id)
    print(f"Disabled schedule: {daily_schedule_id}")

    # Enable a schedule
    scheduler.enable_schedule(daily_schedule_id)
    print(f"Enabled schedule: {daily_schedule_id}")

    # Remove a schedule
    scheduler.unschedule_workflow(weekly_schedule_id)
    print(f"Removed schedule: {weekly_schedule_id}")

    # Stop scheduler (when shutting down)
    # await scheduler.stop()

asyncio.run(use_workflow_scheduler())
```

### Example 13: Workflow Monitor

```python
from app.workflow import WorkflowEngine, WorkflowManager, WorkflowMonitor

async def use_workflow_monitor():
    engine = WorkflowEngine()
    await engine.connect()
    manager = WorkflowManager(engine)
    monitor = WorkflowMonitor(manager)

    # Start monitor
    await monitor.start()

    # Register health checks
    def check_temporal_connection():
        return engine.client is not None

    def check_worker_running():
        return len(engine.workers) > 0

    monitor.register_health_check(check_temporal_connection)
    monitor.register_health_check(check_worker_running)

    # Check health
    health = await monitor.check_health()
    print(f"System healthy: {health['healthy']}")
    print(f"Health checks: {health['checks']}")

    # Get metrics
    metrics = monitor.metrics
    print(f"Total executions: {metrics['total_executions']}")
    print(f"Completed: {metrics['completed']}")
    print(f"Failed: {metrics['failed']}")
    print(f"Average duration: {metrics['average_duration']}s")

    # Get workflow progress
    # progress = await monitor.get_workflow_progress(execution_id)
    # print(f"Progress: {progress['progress']}%")

    # Stop monitor
    # await monitor.stop()

asyncio.run(use_workflow_monitor())
```

## API Examples

### Example 14: Using the REST API

```python
import httpx

async def use_workflow_api():
    base_url = "http://localhost:8000/api/v1"
    token = "your-jwt-token"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        # Create workflow
        response = await client.post(
            f"{base_url}/workflows",
            headers=headers,
            json={
                "workflow_type": "DocumentAnalysisWorkflow",
                "input_data": {
                    "document_id": "doc-api-001",
                    "document_path": "/docs/api.pdf",
                },
            },
        )
        result = response.json()
        execution_id = result["execution_id"]
        print(f"Created workflow: {execution_id}")

        # Start execution
        response = await client.post(
            f"{base_url}/workflows/{execution_id}/execute",
            headers=headers,
        )
        print(f"Started execution: {response.json()}")

        # Get status
        response = await client.get(
            f"{base_url}/workflows/{execution_id}",
            headers=headers,
        )
        print(f"Status: {response.json()}")

        # Get progress
        response = await client.get(
            f"{base_url}/workflows/{execution_id}/progress",
            headers=headers,
        )
        print(f"Progress: {response.json()}")

        # Get history
        response = await client.get(
            f"{base_url}/workflows/{execution_id}/history",
            headers=headers,
        )
        print(f"History: {response.json()}")

        # Pause workflow
        response = await client.post(
            f"{base_url}/workflows/{execution_id}/pause",
            headers=headers,
        )
        print(f"Paused: {response.json()}")

        # Resume workflow
        response = await client.post(
            f"{base_url}/workflows/{execution_id}/resume",
            headers=headers,
        )
        print(f"Resumed: {response.json()}")

        # Cancel workflow
        response = await client.post(
            f"{base_url}/workflows/{execution_id}/cancel",
            headers=headers,
        )
        print(f"Cancelled: {response.json()}")

asyncio.run(use_workflow_api())
```

### Example 15: Schedule Workflow via API

```python
import httpx

async def schedule_workflow_api():
    base_url = "http://localhost:8000/api/v1"
    token = "your-jwt-token"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        # Schedule workflow
        response = await client.post(
            f"{base_url}/workflows/schedule",
            headers=headers,
            json={
                "workflow_type": "DocumentAnalysisWorkflow",
                "cron_expression": "0 9 * * *",
                "input_data": {
                    "document_id": "scheduled-doc",
                    "document_path": "/docs/scheduled.pdf",
                },
            },
        )
        result = response.json()
        schedule_id = result["schedule_id"]
        print(f"Scheduled workflow: {schedule_id}")

        # Remove schedule
        response = await client.delete(
            f"{base_url}/workflows/schedule/{schedule_id}",
            headers=headers,
        )
        print(f"Removed schedule: {response.json()}")

asyncio.run(schedule_workflow_api())
```

## Integration Examples

### Example 16: Agent Integration

```python
from app.workflow.integration import AgentIntegration

async def use_agent_integration():
    # Initialize integration
    agent_integration = AgentIntegration(
        agent_orchestrator=orchestrator,
        agent_service=agent_service,
    )

    # Execute agent task
    result = await agent_integration.execute_agent_task(
        agent_id="research-agent",
        task_type="research_topic",
        payload={
            "topic": "AI Safety",
            "depth": "deep",
        },
        timeout=300,
    )

    print(f"Agent result: {result}")

asyncio.run(use_agent_integration())
```

### Example 17: Knowledge Integration

```python
from app.workflow.integration import KnowledgeIntegration

async def use_knowledge_integration():
    # Initialize integration
    knowledge_integration = KnowledgeIntegration(
        knowledge_service=knowledge_service,
    )

    # Store knowledge
    entity_id = await knowledge_integration.store_knowledge(
        entity_type="document",
        entity_data={
            "title": "AI Safety Report",
            "content": "...",
            "tags": ["ai", "safety"],
        },
        workspace_id="ws-123",
        metadata={"source": "workflow"},
    )
    print(f"Stored knowledge: {entity_id}")

    # Retrieve knowledge
    entities = await knowledge_integration.retrieve_knowledge(
        entity_type="document",
        query="AI Safety",
        workspace_id="ws-123",
        limit=10,
    )
    print(f"Retrieved {len(entities)} entities")

    # Link knowledge
    await knowledge_integration.link_knowledge(
        source_entity_id=entity_id,
        target_entity_id="entity-456",
        relationship_type="references",
        metadata={"confidence": 0.9},
    )
    print("Linked knowledge entities")

asyncio.run(use_knowledge_integration())
```

### Example 18: WebSocket Integration

```python
from app.workflow.integration import WebSocketIntegration

async def use_websocket_integration():
    # Initialize integration
    ws_integration = WebSocketIntegration(
        websocket_manager=websocket_manager,
        event_publisher=event_publisher,
    )

    workflow_id = "workflow-123"
    user_id = "user-456"

    # Notify started
    await ws_integration.notify_workflow_started(
        workflow_id=workflow_id,
        workflow_type="DocumentAnalysisWorkflow",
        user_id=user_id,
    )

    # Notify progress
    await ws_integration.notify_workflow_progress(
        workflow_id=workflow_id,
        progress=50,
        current_task="analyzing_content",
        user_id=user_id,
    )

    # Notify completed
    await ws_integration.notify_workflow_completed(
        workflow_id=workflow_id,
        result={"summary": "Analysis complete"},
        user_id=user_id,
    )

asyncio.run(use_websocket_integration())
```

## Advanced Examples

### Example 19: Custom Workflow Pattern

```python
from temporalio import workflow
from datetime import timedelta

@workflow.defn
class CustomWorkflow:
    """Custom workflow with specific business logic."""

    @workflow.run
    async def run(self, input_data: dict) -> dict:
        """Execute custom workflow."""
        workflow.logger.info(f"Starting custom workflow: {workflow.info().workflow_id}")

        # Custom logic
        step1_result = await workflow.execute_activity(
            "agent_activity",
            {"agent_id": "agent-1", "task_type": "step1"},
            start_to_close_timeout=timedelta(minutes=10),
        )

        # Conditional branching
        if step1_result.get("output_data", {}).get("success"):
            step2_result = await workflow.execute_activity(
                "agent_activity",
                {"agent_id": "agent-2", "task_type": "step2"},
                start_to_close_timeout=timedelta(minutes=10),
            )
        else:
            # Handle failure
            step2_result = {"error": "Step 1 failed"}

        return {
            "step1": step1_result,
            "step2": step2_result,
            "final_status": "completed",
        }

# Register and use
engine = WorkflowEngine()
await engine.connect()
engine.register_workflow(CustomWorkflow)
```

### Example 20: Workflow with Retry Policy

```python
from temporalio.common import RetryPolicy
from datetime import timedelta

async def execute_with_retry():
    engine = WorkflowEngine()
    await engine.connect()

    handle = await engine.client.start_workflow(
        DocumentAnalysisWorkflow,
        {"document_id": "doc-001"},
        id="retry-workflow-001",
        task_queue="workflow-queue",
        retry_policy=RetryPolicy(
            initial_interval=timedelta(seconds=1),
            backoff_coefficient=2.0,
            maximum_interval=timedelta(minutes=1),
            maximum_attempts=5,
            non_retryable_error_types=["ValueError"],
        ),
    )

    result = await handle.result()
    print(f"Workflow completed: {result}")

asyncio.run(execute_with_retry())
```

### Example 21: Workflow with Signals and Queries

```python
from temporalio import workflow

@workflow.defn
class SignalableWorkflow:
    """Workflow that accepts signals and queries."""

    def __init__(self):
        self.counter = 0
        self.paused = False

    @workflow.run
    async def run(self, input_data: dict) -> dict:
        """Execute workflow."""
        for i in range(input_data.get("iterations", 10)):
            # Check if paused
            while self.paused:
                await workflow.sleep(1)

            self.counter += 1
            workflow.logger.info(f"Iteration {self.counter}")
            await workflow.sleep(1)

        return {"counter": self.counter}

    @workflow.signal
    async def pause(self):
        """Pause the workflow."""
        self.paused = True
        workflow.logger.info("Workflow paused")

    @workflow.signal
    async def resume(self):
        """Resume the workflow."""
        self.paused = False
        workflow.logger.info("Workflow resumed")

    @workflow.query
    async def get_counter(self) -> int:
        """Get current counter."""
        return self.counter

# Usage
engine = WorkflowEngine()
await engine.connect()
engine.register_workflow(SignalableWorkflow)

# Start workflow
run_id = await engine.execute_workflow(
    workflow_id="signalable-001",
    workflow_type="SignalableWorkflow",
    input_data={"iterations": 100},
)

# Send signals
await engine.signal_workflow("signalable-001", "pause", {})
await asyncio.sleep(5)
await engine.signal_workflow("signalable-001", "resume", {})

# Query state
counter = await engine.query_workflow("signalable-001", "get_counter")
print(f"Counter: {counter}")
```

These examples demonstrate the flexibility and power of the Workflow Engine. For more information, see the [Workflow Engine Documentation](WORKFLOW_ENGINE.md).
