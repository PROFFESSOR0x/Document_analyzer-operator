"""Workflow Engine Package - Temporal.io-based workflow orchestration.

This package provides comprehensive workflow orchestration capabilities using Temporal.io
for durable execution of multi-stage workflows involving multiple agents.

Package Structure:
    - engine: Core workflow engine and Temporal integration
    - activities: Activity definitions for agent operations
    - patterns: Common workflow patterns (sequential, parallel, conditional, etc.)
    - prebuilt_workflows: Ready-to-use workflow definitions
    - management: Workflow lifecycle management
    - integration: Integration with existing systems

Usage:
    from app.workflow import WorkflowEngine, WorkflowManager
    from app.workflow.prebuilt_workflows import DocumentAnalysisWorkflow

    # Initialize engine
    engine = WorkflowEngine()
    await engine.connect()

    # Register workflows
    engine.register_workflow(DocumentAnalysisWorkflow)

    # Start worker
    await engine.start_worker()
"""

from app.workflow.engine import (
    WorkflowEngine,
    WorkflowDefinition,
    WorkflowState,
    WorkflowContext,
    WorkflowStatus,
    WorkflowPriority,
    get_workflow_engine,
    init_workflow_engine,
    shutdown_workflow_engine,
)

from app.workflow.activities import (
    ActivityStatus,
    ActivityInput,
    ActivityOutput,
    agent_activity,
    parallel_activity,
    sequential_activity,
    conditional_activity,
    retry_activity,
    validation_activity,
)

from app.workflow.patterns import (
    SequentialWorkflow,
    ParallelWorkflow,
    ConditionalWorkflow,
    IterativeWorkflow,
    PipelineWorkflow,
    StatefulWorkflow,
)

from app.workflow.prebuilt_workflows import (
    DocumentAnalysisWorkflow,
    ResearchWorkflow,
    ContentGenerationWorkflow,
    CodeGenerationWorkflow,
    BookGenerationWorkflow,
)

from app.workflow.management import (
    WorkflowManager,
    WorkflowScheduler,
    WorkflowMonitor,
    WorkflowHistory,
    WorkflowExecution,
    WorkflowAction,
)

__all__ = [
    # Engine
    "WorkflowEngine",
    "WorkflowDefinition",
    "WorkflowState",
    "WorkflowContext",
    "WorkflowStatus",
    "WorkflowPriority",
    "get_workflow_engine",
    "init_workflow_engine",
    "shutdown_workflow_engine",
    # Activities
    "ActivityStatus",
    "ActivityInput",
    "ActivityOutput",
    "agent_activity",
    "parallel_activity",
    "sequential_activity",
    "conditional_activity",
    "retry_activity",
    "validation_activity",
    # Patterns
    "SequentialWorkflow",
    "ParallelWorkflow",
    "ConditionalWorkflow",
    "IterativeWorkflow",
    "PipelineWorkflow",
    "StatefulWorkflow",
    # Pre-built Workflows
    "DocumentAnalysisWorkflow",
    "ResearchWorkflow",
    "ContentGenerationWorkflow",
    "CodeGenerationWorkflow",
    "BookGenerationWorkflow",
    # Management
    "WorkflowManager",
    "WorkflowScheduler",
    "WorkflowMonitor",
    "WorkflowHistory",
    "WorkflowExecution",
    "WorkflowAction",
]
