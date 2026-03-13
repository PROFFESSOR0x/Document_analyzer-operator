"""Lightweight In-Memory Workflow Engine for Development.

This module provides a lightweight, in-memory workflow engine for development
and testing without requiring a Temporal server.

Usage:
    from app.workflow.lightweight import LightweightWorkflowEngine

    engine = LightweightWorkflowEngine()
    engine.register_workflow("my_workflow", my_workflow_function)
    result = await engine.execute("my_workflow", input_data)
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class LightweightWorkflowStatus(str, Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class LightweightWorkflowExecution:
    """Lightweight workflow execution record.

    Attributes:
        execution_id: Unique execution ID.
        workflow_type: Type of workflow.
        status: Execution status.
        input_data: Input data.
        output_data: Output data.
        error_message: Error message if failed.
        created_at: Creation timestamp.
        started_at: Start timestamp.
        completed_at: Completion timestamp.
        progress: Progress percentage.
    """

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_type: str = ""
    status: LightweightWorkflowStatus = LightweightWorkflowStatus.PENDING
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "workflow_type": self.workflow_type,
            "status": self.status.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "progress": self.progress,
        }


class LightweightWorkflowEngine:
    """Lightweight in-memory workflow engine for development.

    This engine provides basic workflow execution capabilities without
    requiring Temporal or other external dependencies.

    Attributes:
        workflows: Registered workflow functions.
        executions: Active workflow executions.
        max_concurrent: Maximum concurrent executions.
    """

    def __init__(self, max_concurrent: int = 10) -> None:
        """Initialize the lightweight workflow engine.

        Args:
            max_concurrent: Maximum concurrent workflow executions.
        """
        self.workflows: dict[str, Callable] = {}
        self.executions: dict[str, LightweightWorkflowExecution] = {}
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._running = False

    def register_workflow(
        self, workflow_type: str, workflow_func: Callable
    ) -> None:
        """Register a workflow function.

        Args:
            workflow_type: Type name for the workflow.
            workflow_func: Workflow function to register.
        """
        self.workflows[workflow_type] = workflow_func
        logger.info(f"Registered lightweight workflow: {workflow_type}")

    async def execute(
        self,
        workflow_type: str,
        input_data: dict[str, Any],
        background: bool = False,
    ) -> str:
        """Execute a workflow.

        Args:
            workflow_type: Type of workflow to execute.
            input_data: Input data for the workflow.
            background: Whether to run in background.

        Returns:
            str: Execution ID.

        Raises:
            ValueError: If workflow type not found.
        """
        if workflow_type not in self.workflows:
            raise ValueError(f"Workflow type not found: {workflow_type}")

        execution = LightweightWorkflowExecution(
            workflow_type=workflow_type,
            input_data=input_data,
        )

        self.executions[execution.execution_id] = execution

        if background:
            # Run in background
            asyncio.create_task(self._execute_workflow(execution))
        else:
            # Run synchronously
            await self._execute_workflow(execution)

        return execution.execution_id

    async def _execute_workflow(
        self, execution: LightweightWorkflowExecution
    ) -> None:
        """Execute a workflow.

        Args:
            execution: Workflow execution record.
        """
        async with self._semaphore:
            try:
                execution.status = LightweightWorkflowStatus.RUNNING
                execution.started_at = datetime.now(timezone.utc)

                logger.info(
                    f"Executing workflow: {execution.execution_id} ({execution.workflow_type})"
                )

                workflow_func = self.workflows[execution.workflow_type]

                # Execute workflow
                if asyncio.iscoroutinefunction(workflow_func):
                    result = await workflow_func(execution.input_data)
                else:
                    result = workflow_func(execution.input_data)

                execution.output_data = result
                execution.status = LightweightWorkflowStatus.COMPLETED
                execution.progress = 100

                logger.info(
                    f"Workflow completed: {execution.execution_id}"
                )

            except asyncio.CancelledError:
                execution.status = LightweightWorkflowStatus.CANCELLED
                execution.error_message = "Workflow was cancelled"
                logger.info(f"Workflow cancelled: {execution.execution_id}")

            except Exception as e:
                execution.status = LightweightWorkflowStatus.FAILED
                execution.error_message = str(e)
                logger.error(
                    f"Workflow failed: {execution.execution_id} - {e}",
                    exc_info=True,
                )

            finally:
                execution.completed_at = datetime.now(timezone.utc)

    async def get_status(self, execution_id: str) -> LightweightWorkflowExecution:
        """Get workflow execution status.

        Args:
            execution_id: Execution ID.

        Returns:
            LightweightWorkflowExecution: Execution record.

        Raises:
            ValueError: If execution not found.
        """
        if execution_id not in self.executions:
            raise ValueError(f"Execution not found: {execution_id}")

        return self.executions[execution_id]

    async def cancel(self, execution_id: str) -> None:
        """Cancel a workflow execution.

        Args:
            execution_id: Execution ID.

        Raises:
            ValueError: If execution not found.
        """
        if execution_id not in self.executions:
            raise ValueError(f"Execution not found: {execution_id}")

        execution = self.executions[execution_id]

        if execution.status in [
            LightweightWorkflowStatus.COMPLETED,
            LightweightWorkflowStatus.FAILED,
            LightweightWorkflowStatus.CANCELLED,
        ]:
            logger.warning(f"Cannot cancel workflow in state: {execution.status.value}")
            return

        execution.status = LightweightWorkflowStatus.CANCELLED
        execution.completed_at = datetime.now(timezone.utc)
        execution.error_message = "Cancelled by user"

        logger.info(f"Workflow cancelled: {execution_id}")

    def list_executions(
        self,
        status_filter: Optional[LightweightWorkflowStatus] = None,
    ) -> list[LightweightWorkflowExecution]:
        """List workflow executions.

        Args:
            status_filter: Optional status filter.

        Returns:
            list: List of executions.
        """
        executions = list(self.executions.values())

        if status_filter:
            executions = [e for e in executions if e.status == status_filter]

        return executions


# Lightweight workflow helpers for common patterns

async def sequential_workflow(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute tasks sequentially.

    Input:
        tasks: List of task functions to execute
        initial_data: Initial data to pass to first task

    Output:
        result: Final result after all tasks
        task_results: Results from each task
    """
    tasks = input_data.get("tasks", [])
    current_data = input_data.get("initial_data", {})
    task_results = []

    for idx, task in enumerate(tasks):
        if asyncio.iscoroutinefunction(task):
            result = await task(current_data)
        else:
            result = task(current_data)

        task_results.append(result)

        if isinstance(result, dict):
            current_data = {**current_data, **result}

    return {
        "result": current_data,
        "task_results": task_results,
    }


async def parallel_workflow(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute tasks in parallel.

    Input:
        tasks: List of task functions to execute
        input_data: Data to pass to all tasks

    Output:
        results: Results from all tasks
    """
    tasks = input_data.get("tasks", [])
    task_input = input_data.get("input_data", {})

    async def execute_task(task: Callable) -> Any:
        if asyncio.iscoroutinefunction(task):
            return await task(task_input)
        else:
            return task(task_input)

    results = await asyncio.gather(*[execute_task(task) for task in tasks])

    return {
        "results": results,
        "count": len(results),
    }


async def conditional_workflow(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute based on conditions.

    Input:
        conditions: List of (condition_func, task_func) tuples
        default_task: Default task if no conditions match
        context: Context data for condition evaluation

    Output:
        result: Result from executed task
        matched_condition: Which condition matched (if any)
    """
    conditions = input_data.get("conditions", [])
    default_task = input_data.get("default_task")
    context = input_data.get("context", {})

    for condition_func, task_func in conditions:
        if asyncio.iscoroutinefunction(condition_func):
            matches = await condition_func(context)
        else:
            matches = condition_func(context)

        if matches:
            if asyncio.iscoroutinefunction(task_func):
                result = await task_func(context)
            else:
                result = task_func(context)

            return {
                "result": result,
                "matched_condition": True,
            }

    if default_task:
        if asyncio.iscoroutinefunction(default_task):
            result = await default_task(context)
        else:
            result = default_task(context)

        return {
            "result": result,
            "matched_condition": False,
        }

    return {
        "result": None,
        "matched_condition": False,
    }


async def retry_workflow(
    task: Callable,
    input_data: dict[str, Any],
    max_retries: int = 3,
    delay: float = 1.0,
) -> dict[str, Any]:
    """Execute a task with retry logic.

    Args:
        task: Task function to execute.
        input_data: Input data for the task.
        max_retries: Maximum number of retries.
        delay: Delay between retries in seconds.

    Returns:
        dict: Task result with retry metadata.
    """
    last_error: Optional[str] = None

    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(task):
                result = await task(input_data)
            else:
                result = task(input_data)

            return {
                "result": result,
                "attempts": attempt + 1,
                "success": True,
            }

        except Exception as e:
            last_error = str(e)
            logger.warning(f"Retry attempt {attempt + 1} failed: {e}")

            if attempt < max_retries:
                await asyncio.sleep(delay)

    return {
        "result": None,
        "attempts": max_retries + 1,
        "success": False,
        "error": last_error,
    }
