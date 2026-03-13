"""Workflow Management - Workflow lifecycle management."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional

from croniter import croniter
from temporalio.client import Client as TemporalClient, WorkflowHandle

from app.core.logging_config import get_logger
from app.workflow.engine import WorkflowDefinition, WorkflowEngine, WorkflowState, WorkflowStatus

logger = get_logger(__name__)


class WorkflowAction(str, Enum):
    """Workflow management actions."""

    CREATE = "create"
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    TERMINATE = "terminate"


@dataclass
class WorkflowExecution:
    """Workflow execution record.

    Attributes:
        execution_id: Unique execution ID.
        workflow_id: Workflow definition ID.
        workflow_type: Type of workflow.
        state: Workflow state.
        context: Workflow context.
        created_at: Creation timestamp.
        started_at: Start timestamp.
        completed_at: Completion timestamp.
        scheduled_at: Scheduled execution time.
        cron_expression: Cron expression for scheduled workflows.
        metadata: Additional metadata.
    """

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    workflow_type: str = ""
    state: WorkflowState = field(default_factory=WorkflowState)
    context: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    cron_expression: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "state": self.state.to_dict(),
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "cron_expression": self.cron_expression,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowExecution:
        """Create from dictionary."""
        return cls(
            execution_id=data.get("execution_id", str(uuid.uuid4())),
            workflow_id=data.get("workflow_id", ""),
            workflow_type=data.get("workflow_type", ""),
            state=WorkflowState.from_dict(data.get("state", {})),
            context=data.get("context", {}),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else datetime.now(timezone.utc)
            ),
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
            scheduled_at=(
                datetime.fromisoformat(data["scheduled_at"])
                if data.get("scheduled_at")
                else None
            ),
            cron_expression=data.get("cron_expression"),
            metadata=data.get("metadata", {}),
        )


class WorkflowManager:
    """Create, start, pause, resume, cancel workflows.

    This class provides lifecycle management for workflow executions.

    Attributes:
        engine: Workflow engine instance.
        executions: Active workflow executions.
        definitions: Registered workflow definitions.
    """

    def __init__(self, engine: WorkflowEngine) -> None:
        """Initialize the workflow manager.

        Args:
            engine: Workflow engine instance.
        """
        self.engine = engine
        self.executions: dict[str, WorkflowExecution] = {}
        self.definitions: dict[str, WorkflowDefinition] = {}
        self._handles: dict[str, WorkflowHandle] = {}

    def register_definition(self, definition: WorkflowDefinition) -> None:
        """Register a workflow definition.

        Args:
            definition: Workflow definition to register.
        """
        self.definitions[definition.id] = definition
        logger.info(f"Registered workflow definition: {definition.name}")

    async def create_workflow(
        self,
        workflow_type: str,
        input_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
        scheduled_at: Optional[datetime] = None,
        cron_expression: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> WorkflowExecution:
        """Create a new workflow execution.

        Args:
            workflow_type: Type of workflow to create.
            input_data: Input data for the workflow.
            context: Optional workflow context.
            scheduled_at: Optional scheduled execution time.
            cron_expression: Optional cron expression for recurring workflows.
            metadata: Optional additional metadata.

        Returns:
            WorkflowExecution: Created workflow execution.

        Raises:
            ValueError: If workflow type not found.
        """
        if workflow_type not in self.engine.workflows:
            raise ValueError(f"Workflow type not found: {workflow_type}")

        execution = WorkflowExecution(
            workflow_type=workflow_type,
            state=WorkflowState(
                definition_id=workflow_type,
                status=WorkflowStatus.PENDING,
                input_data=input_data,
            ),
            context=context or {},
            scheduled_at=scheduled_at,
            cron_expression=cron_expression,
            metadata=metadata or {},
        )

        # If scheduled, set state to scheduled
        if scheduled_at or cron_expression:
            execution.state.status = WorkflowStatus.PENDING
            logger.info(
                f"Scheduled workflow execution: {execution.execution_id} "
                f"at {scheduled_at or cron_expression}"
            )
        else:
            logger.info(f"Created workflow execution: {execution.execution_id}")

        self.executions[execution.execution_id] = execution
        return execution

    async def start_workflow(self, execution_id: str) -> str:
        """Start a workflow execution.

        Args:
            execution_id: Workflow execution ID.

        Returns:
            str: Temporal workflow run ID.

        Raises:
            ValueError: If execution not found or not in pending state.
        """
        if execution_id not in self.executions:
            raise ValueError(f"Workflow execution not found: {execution_id}")

        execution = self.executions[execution_id]

        if execution.state.status != WorkflowStatus.PENDING:
            raise ValueError(
                f"Workflow not in pending state: {execution.state.status.value}"
            )

        # Update state
        execution.state.status = WorkflowStatus.RUNNING
        execution.started_at = datetime.now(timezone.utc)

        # Start workflow in Temporal
        run_id = await self.engine.execute_workflow(
            workflow_id=execution.execution_id,
            workflow_type=execution.workflow_type,
            input_data=execution.state.input_data,
        )

        logger.info(f"Started workflow execution: {execution_id} (run_id: {run_id})")
        return run_id

    async def pause_workflow(self, execution_id: str) -> None:
        """Pause a running workflow.

        Args:
            execution_id: Workflow execution ID.

        Raises:
            ValueError: If execution not found or not running.
        """
        if execution_id not in self.executions:
            raise ValueError(f"Workflow execution not found: {execution_id}")

        execution = self.executions[execution_id]

        if execution.state.status != WorkflowStatus.RUNNING:
            raise ValueError(
                f"Workflow not in running state: {execution.state.status.value}"
            )

        # Send pause signal
        await self.engine.signal_workflow(execution_id, "pause", {})
        execution.state.status = WorkflowStatus.PAUSED

        logger.info(f"Paused workflow execution: {execution_id}")

    async def resume_workflow(self, execution_id: str) -> None:
        """Resume a paused workflow.

        Args:
            execution_id: Workflow execution ID.

        Raises:
            ValueError: If execution not found or not paused.
        """
        if execution_id not in self.executions:
            raise ValueError(f"Workflow execution not found: {execution_id}")

        execution = self.executions[execution_id]

        if execution.state.status != WorkflowStatus.PAUSED:
            raise ValueError(
                f"Workflow not in paused state: {execution.state.status.value}"
            )

        # Send resume signal
        await self.engine.signal_workflow(execution_id, "resume", {})
        execution.state.status = WorkflowStatus.RUNNING

        logger.info(f"Resumed workflow execution: {execution_id}")

    async def cancel_workflow(self, execution_id: str) -> None:
        """Cancel a workflow execution.

        Args:
            execution_id: Workflow execution ID.

        Raises:
            ValueError: If execution not found.
        """
        if execution_id not in self.executions:
            raise ValueError(f"Workflow execution not found: {execution_id}")

        execution = self.executions[execution_id]

        if execution.state.status in [
            WorkflowStatus.COMPLETED,
            WorkflowStatus.CANCELLED,
        ]:
            logger.warning(f"Workflow already completed or cancelled: {execution_id}")
            return

        # Cancel workflow
        await self.engine.cancel_workflow(execution_id)
        execution.state.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.now(timezone.utc)

        logger.info(f"Cancelled workflow execution: {execution_id}")

    async def get_workflow_status(self, execution_id: str) -> WorkflowState:
        """Get the status of a workflow execution.

        Args:
            execution_id: Workflow execution ID.

        Returns:
            WorkflowState: Current workflow state.

        Raises:
            ValueError: If execution not found.
        """
        if execution_id not in self.executions:
            raise ValueError(f"Workflow execution not found: {execution_id}")

        execution = self.executions[execution_id]

        # Update state from Temporal if running
        if execution.state.status == WorkflowStatus.RUNNING:
            try:
                temporal_status = await self.engine.get_workflow_status(execution_id)
                execution.state.status = temporal_status
            except Exception as e:
                logger.warning(f"Failed to get workflow status: {e}")

        return execution.state

    async def get_execution_history(self, execution_id: str) -> dict[str, Any]:
        """Get the execution history of a workflow.

        Args:
            execution_id: Workflow execution ID.

        Returns:
            dict: Execution history.

        Raises:
            ValueError: If execution not found.
        """
        if execution_id not in self.executions:
            raise ValueError(f"Workflow execution not found: {execution_id}")

        execution = self.executions[execution_id]

        return {
            "execution_id": execution.execution_id,
            "workflow_type": execution.workflow_type,
            "history": [
                {
                    "timestamp": execution.created_at.isoformat(),
                    "event": "created",
                    "details": "Workflow execution created",
                },
                {
                    "timestamp": execution.started_at.isoformat()
                    if execution.started_at
                    else None,
                    "event": "started",
                    "details": "Workflow execution started",
                },
                {
                    "timestamp": execution.completed_at.isoformat()
                    if execution.completed_at
                    else None,
                    "event": "completed",
                    "details": "Workflow execution completed",
                },
            ],
            "state": execution.state.to_dict(),
        }

    def list_executions(
        self,
        status_filter: Optional[WorkflowStatus] = None,
        workflow_type_filter: Optional[str] = None,
    ) -> list[WorkflowExecution]:
        """List workflow executions.

        Args:
            status_filter: Optional status filter.
            workflow_type_filter: Optional workflow type filter.

        Returns:
            list: List of workflow executions.
        """
        executions = list(self.executions.values())

        if status_filter:
            executions = [e for e in executions if e.state.status == status_filter]

        if workflow_type_filter:
            executions = [
                e for e in executions if e.workflow_type == workflow_type_filter
            ]

        return executions


class WorkflowScheduler:
    """Schedule workflows (cron-like).

    This class provides scheduling capabilities for workflows.

    Attributes:
        manager: Workflow manager instance.
        scheduled_jobs: Scheduled workflow jobs.
        running: Whether the scheduler is running.
    """

    def __init__(self, manager: WorkflowManager) -> None:
        """Initialize the workflow scheduler.

        Args:
            manager: Workflow manager instance.
        """
        self.manager = manager
        self.scheduled_jobs: dict[str, dict[str, Any]] = {}
        self.running = False
        self._scheduler_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the scheduler."""
        self.running = True
        self._scheduler_task = asyncio.create_task(self._run_scheduler())
        logger.info("Workflow scheduler started")

    async def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Workflow scheduler stopped")

    def schedule_workflow(
        self,
        workflow_type: str,
        cron_expression: str,
        input_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """Schedule a workflow with a cron expression.

        Args:
            workflow_type: Type of workflow to schedule.
            cron_expression: Cron expression for scheduling.
            input_data: Input data for the workflow.
            context: Optional workflow context.
            metadata: Optional additional metadata.

        Returns:
            str: Schedule ID.

        Raises:
            ValueError: If cron expression is invalid.
        """
        # Validate cron expression
        try:
            croniter(cron_expression)
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {e}")

        schedule_id = str(uuid.uuid4())
        self.scheduled_jobs[schedule_id] = {
            "workflow_type": workflow_type,
            "cron_expression": cron_expression,
            "input_data": input_data,
            "context": context or {},
            "metadata": metadata or {},
            "enabled": True,
            "last_run": None,
            "next_run": self._calculate_next_run(cron_expression),
        }

        logger.info(
            f"Scheduled workflow {workflow_type} with cron: {cron_expression} (id: {schedule_id})"
        )
        return schedule_id

    def unschedule_workflow(self, schedule_id: str) -> None:
        """Remove a scheduled workflow.

        Args:
            schedule_id: Schedule ID.

        Raises:
            ValueError: If schedule not found.
        """
        if schedule_id not in self.scheduled_jobs:
            raise ValueError(f"Schedule not found: {schedule_id}")

        del self.scheduled_jobs[schedule_id]
        logger.info(f"Removed scheduled workflow: {schedule_id}")

    def enable_schedule(self, schedule_id: str) -> None:
        """Enable a scheduled workflow.

        Args:
            schedule_id: Schedule ID.

        Raises:
            ValueError: If schedule not found.
        """
        if schedule_id not in self.scheduled_jobs:
            raise ValueError(f"Schedule not found: {schedule_id}")

        self.scheduled_jobs[schedule_id]["enabled"] = True
        logger.info(f"Enabled scheduled workflow: {schedule_id}")

    def disable_schedule(self, schedule_id: str) -> None:
        """Disable a scheduled workflow.

        Args:
            schedule_id: Schedule ID.

        Raises:
            ValueError: If schedule not found.
        """
        if schedule_id not in self.scheduled_jobs:
            raise ValueError(f"Schedule not found: {schedule_id}")

        self.scheduled_jobs[schedule_id]["enabled"] = False
        logger.info(f"Disabled scheduled workflow: {schedule_id}")

    def _calculate_next_run(self, cron_expression: str) -> datetime:
        """Calculate the next run time for a cron expression.

        Args:
            cron_expression: Cron expression.

        Returns:
            datetime: Next run time.
        """
        cron = croniter(cron_expression, datetime.now(timezone.utc))
        return cron.get_next(datetime)

    async def _run_scheduler(self) -> None:
        """Run the scheduler loop."""
        while self.running:
            try:
                await self._check_schedules()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)
                await asyncio.sleep(60)

    async def _check_schedules(self) -> None:
        """Check and trigger due schedules."""
        now = datetime.now(timezone.utc)

        for schedule_id, schedule in self.scheduled_jobs.items():
            if not schedule["enabled"]:
                continue

            next_run = schedule["next_run"]
            if next_run and now >= next_run:
                # Trigger workflow
                try:
                    await self._trigger_scheduled_workflow(schedule_id, schedule)

                    # Calculate next run
                    schedule["last_run"] = now
                    schedule["next_run"] = self._calculate_next_run(
                        schedule["cron_expression"]
                    )

                    logger.info(
                        f"Triggered scheduled workflow {schedule_id}, next run: {schedule['next_run']}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to trigger scheduled workflow {schedule_id}: {e}",
                        exc_info=True,
                    )

    async def _trigger_scheduled_workflow(
        self, schedule_id: str, schedule: dict[str, Any]
    ) -> None:
        """Trigger a scheduled workflow.

        Args:
            schedule_id: Schedule ID.
            schedule: Schedule configuration.
        """
        execution = await self.manager.create_workflow(
            workflow_type=schedule["workflow_type"],
            input_data=schedule["input_data"],
            context=schedule["context"],
            metadata={
                **schedule["metadata"],
                "scheduled_by": schedule_id,
                "scheduled_run": schedule["last_run"],
            },
        )

        # Start immediately
        await self.manager.start_workflow(execution.execution_id)


class WorkflowMonitor:
    """Monitor workflow health and progress.

    This class provides monitoring capabilities for workflows.

    Attributes:
        manager: Workflow manager instance.
        health_checks: Registered health checks.
        metrics: Workflow metrics.
    """

    def __init__(self, manager: WorkflowManager) -> None:
        """Initialize the workflow monitor.

        Args:
            manager: Workflow manager instance.
        """
        self.manager = manager
        self.health_checks: list[Callable] = []
        self.metrics: dict[str, Any] = {
            "total_executions": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "running": 0,
            "average_duration": 0,
        }
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start the monitor."""
        self._running = True
        self._monitoring_task = asyncio.create_task(self._run_monitor())
        logger.info("Workflow monitor started")

    async def stop(self) -> None:
        """Stop the monitor."""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Workflow monitor stopped")

    def register_health_check(self, check: Callable) -> None:
        """Register a health check function.

        Args:
            check: Health check function.
        """
        self.health_checks.append(check)
        logger.info(f"Registered health check: {check.__name__}")

    async def check_health(self) -> dict[str, Any]:
        """Run all health checks.

        Returns:
            dict: Health check results.
        """
        results = {
            "healthy": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        for check in self.health_checks:
            try:
                if asyncio.iscoroutinefunction(check):
                    result = await check()
                else:
                    result = check()

                results["checks"][check.__name__] = {
                    "status": "healthy" if result else "unhealthy",
                    "healthy": result,
                }

                if not result:
                    results["healthy"] = False
            except Exception as e:
                results["checks"][check.__name__] = {
                    "status": "error",
                    "healthy": False,
                    "error": str(e),
                }
                results["healthy"] = False

        return results

    async def get_workflow_progress(self, execution_id: str) -> dict[str, Any]:
        """Get real-time progress of a workflow.

        Args:
            execution_id: Workflow execution ID.

        Returns:
            dict: Workflow progress.

        Raises:
            ValueError: If execution not found.
        """
        if execution_id not in self.manager.executions:
            raise ValueError(f"Workflow execution not found: {execution_id}")

        execution = self.manager.executions[execution_id]

        return {
            "execution_id": execution_id,
            "workflow_type": execution.workflow_type,
            "status": execution.state.status.value,
            "progress": execution.state.progress,
            "current_task": execution.state.current_task,
            "completed_tasks": execution.state.completed_tasks,
            "failed_tasks": execution.state.failed_tasks,
            "started_at": execution.started_at.isoformat()
            if execution.started_at
            else None,
            "elapsed_seconds": (
                (datetime.now(timezone.utc) - execution.started_at).total_seconds()
                if execution.started_at
                else 0
            ),
        }

    async def _run_monitor(self) -> None:
        """Run the monitor loop."""
        while self._running:
            try:
                await self._update_metrics()
                await asyncio.sleep(30)  # Update every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}", exc_info=True)
                await asyncio.sleep(30)

    async def _update_metrics(self) -> None:
        """Update workflow metrics."""
        executions = list(self.manager.executions.values())

        self.metrics["total_executions"] = len(executions)
        self.metrics["completed"] = sum(
            1 for e in executions if e.state.status == WorkflowStatus.COMPLETED
        )
        self.metrics["failed"] = sum(
            1 for e in executions if e.state.status == WorkflowStatus.FAILED
        )
        self.metrics["cancelled"] = sum(
            1 for e in executions if e.state.status == WorkflowStatus.CANCELLED
        )
        self.metrics["running"] = sum(
            1 for e in executions if e.state.status == WorkflowStatus.RUNNING
        )

        # Calculate average duration
        completed_executions = [
            e
            for e in executions
            if e.state.status == WorkflowStatus.COMPLETED and e.completed_at
        ]
        if completed_executions:
            total_duration = sum(
                (e.completed_at - e.started_at).total_seconds()
                for e in completed_executions
                if e.started_at
            )
            self.metrics["average_duration"] = (
                total_duration / len(completed_executions)
                if completed_executions
                else 0
            )


class WorkflowHistory:
    """Track workflow execution history.

    This class provides history tracking for workflow executions.

    Attributes:
        history_records: History records.
        max_records: Maximum number of records to keep.
    """

    def __init__(self, max_records: int = 1000) -> None:
        """Initialize the workflow history.

        Args:
            max_records: Maximum number of records to keep.
        """
        self.history_records: list[dict[str, Any]] = []
        self.max_records = max_records

    def record_event(
        self,
        execution_id: str,
        event_type: str,
        event_data: dict[str, Any],
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Record a workflow event.

        Args:
            execution_id: Workflow execution ID.
            event_type: Type of event.
            event_data: Event data.
            timestamp: Event timestamp.
        """
        record = {
            "execution_id": execution_id,
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat(),
        }

        self.history_records.append(record)

        # Trim old records
        if len(self.history_records) > self.max_records:
            self.history_records = self.history_records[-self.max_records :]

    def get_history(
        self,
        execution_id: Optional[str] = None,
        event_type_filter: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get workflow history.

        Args:
            execution_id: Optional execution ID filter.
            event_type_filter: Optional event type filter.
            limit: Maximum number of records to return.

        Returns:
            list: History records.
        """
        records = self.history_records

        if execution_id:
            records = [r for r in records if r["execution_id"] == execution_id]

        if event_type_filter:
            records = [r for r in records if r["event_type"] == event_type_filter]

        return records[-limit:]

    def clear_history(self, execution_id: Optional[str] = None) -> None:
        """Clear workflow history.

        Args:
            execution_id: Optional execution ID to clear.
        """
        if execution_id:
            self.history_records = [
                r for r in self.history_records if r["execution_id"] != execution_id
            ]
        else:
            self.history_records.clear()
