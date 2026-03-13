"""Workflow Engine Core - Main orchestration engine for Temporal.io workflows."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

from temporalio import activity, workflow
from temporalio.client import Client as TemporalClient
from temporalio.worker import Worker

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class WorkflowPriority(str, Enum):
    """Workflow execution priority."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class WorkflowDefinition:
    """Workflow structure and configuration.

    Attributes:
        id: Unique workflow definition ID.
        name: Workflow name.
        description: Workflow description.
        version: Workflow version.
        tasks: List of task definitions.
        edges: Task dependencies and flow.
        config: Workflow configuration.
        retry_policy: Default retry policy.
        timeout: Default timeout in seconds.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: Optional[str] = None
    version: str = "1.0.0"
    tasks: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)
    retry_policy: Optional[dict[str, Any]] = None
    timeout: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "tasks": self.tasks,
            "edges": self.edges,
            "config": self.config,
            "retry_policy": self.retry_policy,
            "timeout": self.timeout,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowDefinition:
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description"),
            version=data.get("version", "1.0.0"),
            tasks=data.get("tasks", []),
            edges=data.get("edges", []),
            config=data.get("config", {}),
            retry_policy=data.get("retry_policy"),
            timeout=data.get("timeout"),
        )


@dataclass
class WorkflowState:
    """State management for workflows.

    Attributes:
        workflow_id: Unique workflow execution ID.
        definition_id: Workflow definition ID.
        status: Current workflow status.
        priority: Workflow priority.
        input_data: Input data for workflow.
        output_data: Output data from workflow.
        current_task: Current executing task ID.
        completed_tasks: List of completed task IDs.
        failed_tasks: List of failed task IDs.
        progress: Progress percentage (0-100).
        error_message: Error message if failed.
        started_at: Workflow start timestamp.
        completed_at: Workflow completion timestamp.
        metadata: Additional metadata.
    """

    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    definition_id: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    priority: WorkflowPriority = WorkflowPriority.MEDIUM
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    current_task: Optional[str] = None
    completed_tasks: list[str] = field(default_factory=list)
    failed_tasks: list[str] = field(default_factory=list)
    progress: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "definition_id": self.definition_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "current_task": self.current_task,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "progress": self.progress,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowState:
        """Create from dictionary."""
        return cls(
            workflow_id=data.get("workflow_id", str(uuid.uuid4())),
            definition_id=data.get("definition_id", ""),
            status=WorkflowStatus(data.get("status", "pending")),
            priority=WorkflowPriority(data.get("priority", "medium")),
            input_data=data.get("input_data", {}),
            output_data=data.get("output_data", {}),
            current_task=data.get("current_task"),
            completed_tasks=data.get("completed_tasks", []),
            failed_tasks=data.get("failed_tasks", []),
            progress=data.get("progress", 0),
            error_message=data.get("error_message"),
            started_at=(
                datetime.fromisoformat(data["started_at"])
                if data.get("started_at")
                else None
            ),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data.get("completed_at")
                else None
            ),
            metadata=data.get("metadata", {}),
        )

    def update_progress(self, progress: int) -> None:
        """Update workflow progress."""
        self.progress = min(100, max(0, progress))

    def mark_task_completed(self, task_id: str) -> None:
        """Mark a task as completed."""
        if task_id not in self.completed_tasks:
            self.completed_tasks.append(task_id)
            self.update_progress(
                int((len(self.completed_tasks) / self._total_tasks()) * 100)
                if self._total_tasks() > 0
                else 0
            )

    def mark_task_failed(self, task_id: str) -> None:
        """Mark a task as failed."""
        if task_id not in self.failed_tasks:
            self.failed_tasks.append(task_id)

    def _total_tasks(self) -> int:
        """Get total number of tasks."""
        return len(self.completed_tasks) + len(self.failed_tasks)


@dataclass
class WorkflowContext:
    """Execution context for workflows.

    Attributes:
        workflow_id: Unique workflow execution ID.
        user_id: User ID who initiated the workflow.
        workspace_id: Workspace ID for context isolation.
        correlation_id: Correlation ID for tracing.
        created_at: Context creation timestamp.
        expires_at: Context expiration timestamp.
    """

    workflow_id: str
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    context_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "context_data": self.context_data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowContext:
        """Create from dictionary."""
        return cls(
            workflow_id=data.get("workflow_id", ""),
            user_id=data.get("user_id"),
            workspace_id=data.get("workspace_id"),
            correlation_id=data.get("correlation_id", str(uuid.uuid4())),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else datetime.now(timezone.utc)
            ),
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at")
                else None
            ),
            context_data=data.get("context_data", {}),
        )

    def is_expired(self) -> bool:
        """Check if context has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at


class WorkflowEngine:
    """Main orchestration engine for workflow execution.

    This class provides the core functionality for managing Temporal.io workers,
    registering workflows and activities, and coordinating execution.

    Attributes:
        client: Temporal client instance.
        task_queue: Task queue name for workers.
        workflows: Registered workflow definitions.
        activities: Registered activity functions.
        workers: Active worker instances.
    """

    def __init__(
        self,
        temporal_host: str = "localhost",
        temporal_port: int = 7233,
        task_queue: str = "workflow-queue",
    ) -> None:
        """Initialize the workflow engine.

        Args:
            temporal_host: Temporal server host.
            temporal_port: Temporal server port.
            task_queue: Default task queue name.
        """
        self.temporal_host = temporal_host
        self.temporal_port = temporal_port
        self.task_queue = task_queue
        self.client: Optional[TemporalClient] = None
        self.workflows: dict[str, type] = {}
        self.activities: dict[str, Callable] = {}
        self.workers: list[Worker] = []
        self._running = False

    async def connect(self) -> None:
        """Connect to Temporal server."""
        try:
            self.client = await TemporalClient.connect(
                target=f"{self.temporal_host}:{self.temporal_port}"
            )
            logger.info(
                f"Connected to Temporal server at {self.temporal_host}:{self.temporal_port}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Temporal server: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Temporal server."""
        await self.shutdown()
        self.client = None
        logger.info("Disconnected from Temporal server")

    def register_workflow(self, workflow_class: type) -> None:
        """Register a workflow definition.

        Args:
            workflow_class: Workflow class to register.
        """
        workflow_name = workflow_class.__name__
        self.workflows[workflow_name] = workflow_class
        logger.info(f"Registered workflow: {workflow_name}")

    def register_activity(self, activity_func: Callable) -> None:
        """Register an activity function.

        Args:
            activity_func: Activity function to register.
        """
        activity_name = activity_func.__name__
        self.activities[activity_name] = activity_func
        logger.info(f"Registered activity: {activity_name}")

    async def start_worker(self) -> None:
        """Start the workflow worker."""
        if not self.client:
            raise RuntimeError("Not connected to Temporal server")

        if not self.workflows:
            raise RuntimeError("No workflows registered")

        worker = Worker(
            self.client,
            task_queue=self.task_queue,
            workflows=list(self.workflows.values()),
            activities=list(self.activities.values()),
        )

        self.workers.append(worker)
        self._running = True

        logger.info(f"Starting worker on task queue: {self.task_queue}")
        await worker.run()

    async def shutdown(self) -> None:
        """Shutdown all workers."""
        self._running = False
        for worker in self.workers:
            await worker.shutdown()
        self.workers.clear()
        logger.info("All workers shutdown")

    async def execute_workflow(
        self,
        workflow_id: str,
        workflow_type: str,
        input_data: dict[str, Any],
        context: Optional[WorkflowContext] = None,
    ) -> str:
        """Execute a workflow.

        Args:
            workflow_id: Unique workflow execution ID.
            workflow_type: Type of workflow to execute.
            input_data: Input data for the workflow.
            context: Optional workflow context.

        Returns:
            str: Workflow execution run ID.

        Raises:
            RuntimeError: If not connected or workflow not found.
        """
        if not self.client:
            raise RuntimeError("Not connected to Temporal server")

        if workflow_type not in self.workflows:
            raise RuntimeError(f"Workflow type not found: {workflow_type}")

        workflow_class = self.workflows[workflow_type]

        handle = await self.client.start_workflow(
            workflow_class,
            input_data,
            id=workflow_id,
            task_queue=self.task_queue,
        )

        logger.info(f"Started workflow {workflow_type} with ID {workflow_id}")
        return handle.result_run_id

    async def get_workflow_status(self, workflow_id: str) -> WorkflowStatus:
        """Get the status of a workflow execution.

        Args:
            workflow_id: Workflow execution ID.

        Returns:
            WorkflowStatus: Current workflow status.
        """
        if not self.client:
            raise RuntimeError("Not connected to Temporal server")

        handle = self.client.get_workflow_handle(workflow_id)
        description = await handle.describe()

        status_map = {
            1: WorkflowStatus.PENDING,
            2: WorkflowStatus.RUNNING,
            3: WorkflowStatus.COMPLETED,
            4: WorkflowStatus.FAILED,
            5: WorkflowStatus.CANCELLED,
        }

        return status_map.get(description.status, WorkflowStatus.PENDING)

    async def cancel_workflow(self, workflow_id: str) -> None:
        """Cancel a running workflow.

        Args:
            workflow_id: Workflow execution ID.
        """
        if not self.client:
            raise RuntimeError("Not connected to Temporal server")

        handle = self.client.get_workflow_handle(workflow_id)
        await handle.cancel()
        logger.info(f"Cancelled workflow: {workflow_id}")

    async def signal_workflow(
        self, workflow_id: str, signal_name: str, signal_data: Any
    ) -> None:
        """Send a signal to a running workflow.

        Args:
            workflow_id: Workflow execution ID.
            signal_name: Name of the signal.
            signal_data: Signal data.
        """
        if not self.client:
            raise RuntimeError("Not connected to Temporal server")

        handle = self.client.get_workflow_handle(workflow_id)
        await handle.signal(signal_name, signal_data)
        logger.info(f"Sent signal {signal_name} to workflow {workflow_id}")


# Global workflow engine instance
_workflow_engine: Optional[WorkflowEngine] = None


def get_workflow_engine() -> WorkflowEngine:
    """Get the global workflow engine instance.

    Returns:
        WorkflowEngine: Workflow engine instance.
    """
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine


async def init_workflow_engine(
    temporal_host: str = "localhost",
    temporal_port: int = 7233,
    task_queue: str = "workflow-queue",
) -> WorkflowEngine:
    """Initialize the global workflow engine.

    Args:
        temporal_host: Temporal server host.
        temporal_port: Temporal server port.
        task_queue: Task queue name.

    Returns:
        WorkflowEngine: Initialized workflow engine.
    """
    global _workflow_engine
    _workflow_engine = WorkflowEngine(
        temporal_host=temporal_host,
        temporal_port=temporal_port,
        task_queue=task_queue,
    )
    await _workflow_engine.connect()
    return _workflow_engine


async def shutdown_workflow_engine() -> None:
    """Shutdown the global workflow engine."""
    global _workflow_engine
    if _workflow_engine:
        await _workflow_engine.disconnect()
        _workflow_engine = None
