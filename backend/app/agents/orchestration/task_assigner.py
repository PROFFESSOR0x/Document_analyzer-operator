"""Task assigner for distributing work to agents."""

from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from uuid import uuid4

from app.agents.core.base import BaseAgent
from app.agents.core.states import AgentState
from app.agents.core.messages import RequestMessage, ResponseMessage
from app.agents.registry.agent_registry import AgentRegistry
from app.agents.orchestration.load_balancer import LoadBalancer, LoadBalancingStrategy


class TaskStatus(str, Enum):
    """Task status enumeration.

    Attributes:
        PENDING: Task waiting to be assigned.
        ASSIGNED: Task assigned to an agent.
        IN_PROGRESS: Task being executed.
        COMPLETED: Task completed successfully.
        FAILED: Task failed.
        CANCELLED: Task cancelled.
        TIMEOUT: Task timed out.
    """

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class Task:
    """Task representation.

    Attributes:
        id: Task ID.
        type: Task type.
        payload: Task data.
        status: Task status.
        priority: Task priority.
        assigned_agent_id: ID of assigned agent.
        created_at: Creation timestamp.
        started_at: Start timestamp.
        completed_at: Completion timestamp.
        timeout_seconds: Task timeout.
        retry_count: Number of retries.
        max_retries: Maximum retry attempts.
        metadata: Additional metadata.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    type: str = field(default="")
    payload: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = field(default=TaskStatus.PENDING)
    priority: int = field(default=0)
    assigned_agent_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_seconds: float = field(default=300.0)
    retry_count: int = field(default=0)
    max_retries: int = field(default=3)
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary.

        Returns:
            Dict: Task data.
        """
        return {
            "id": self.id,
            "type": self.type,
            "payload": self.payload,
            "status": self.status.value,
            "priority": self.priority,
            "assigned_agent_id": self.assigned_agent_id,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "metadata": self.metadata,
            "result": self.result,
            "error_message": self.error_message,
        }


class TaskAssigner:
    """Task assigner for distributing work to agents.

    This class provides:
    - Task queue management
    - Task assignment logic
    - Retry logic with exponential backoff
    - Failure recovery strategies
    - Task prioritization

    Usage:
        assigner = TaskAssigner(registry, load_balancer)
        task = Task(type="analyze", payload={"data": "..."})
        await assigner.submit_task(task)
        result = await assigner.execute_task(task)
    """

    def __init__(
        self,
        registry: AgentRegistry,
        load_balancer: Optional[LoadBalancer] = None,
        max_concurrent_tasks: int = 100,
    ) -> None:
        """Initialize task assigner.

        Args:
            registry: Agent registry.
            load_balancer: Optional load balancer.
            max_concurrent_tasks: Maximum concurrent tasks.
        """
        self._registry = registry
        self._load_balancer = load_balancer or LoadBalancer(registry)
        self._max_concurrent_tasks = max_concurrent_tasks
        self._logger = logging.getLogger("agent.task_assigner")

        # Task queues by priority
        self._task_queues: Dict[int, asyncio.Queue[Task]] = {}
        self._active_tasks: Dict[str, Task] = {}
        self._completed_tasks: Dict[str, Task] = {}

        # Callbacks
        self._on_task_complete: List[Callable[[Task], Awaitable[None]]] = []
        self._on_task_failed: List[Callable[[Task], Awaitable[None]]] = []

        # Worker task
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False

        self._logger.info(f"Task assigner initialized (max_concurrent={max_concurrent_tasks})")

    async def start(self) -> None:
        """Start the task assigner worker."""
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._worker_loop())
            self._logger.info("Task assigner worker started")

    async def stop(self) -> None:
        """Stop the task assigner worker."""
        if self._running:
            self._running = False
            if self._worker_task:
                self._worker_task.cancel()
                try:
                    await self._worker_task
                except asyncio.CancelledError:
                    pass
            self._logger.info("Task assigner worker stopped")

    async def submit_task(self, task: Task) -> str:
        """Submit a task for execution.

        Args:
            task: Task to submit.

        Returns:
            str: Task ID.
        """
        priority = task.priority
        if priority not in self._task_queues:
            self._task_queues[priority] = asyncio.Queue()

        await self._task_queues[priority].put(task)
        self._logger.info(f"Task submitted: {task.id} (type={task.type}, priority={priority})")

        return task.id

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task immediately.

        Args:
            task: Task to execute.

        Returns:
            Dict: Task result.

        Raises:
            ValueError: If no agent available.
            asyncio.TimeoutError: If task times out.
        """
        task.status = TaskStatus.ASSIGNED
        task.started_at = datetime.now(timezone.utc)
        self._active_tasks[task.id] = task

        try:
            # Select agent
            agent = self._load_balancer.select_agent(
                agent_type=task.payload.get("agent_type"),
                task=task.payload,
                required_capabilities=task.payload.get("required_capabilities"),
            )

            if not agent:
                raise ValueError("No available agent")

            task.assigned_agent_id = agent.agent_id

            # Execute with timeout
            result = await asyncio.wait_for(
                agent.execute(task.payload),
                timeout=task.timeout_seconds,
            )

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            task.result = result

            self._logger.info(f"Task completed: {task.id}")

            # Notify callbacks
            for callback in self._on_task_complete:
                await callback(task)

            return result

        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.error_message = f"Task timed out after {task.timeout_seconds}s"
            self._logger.error(f"Task timeout: {task.id}")
            raise

        except Exception as e:
            task.error_message = str(e)
            self._logger.error(f"Task failed: {task.id} - {e}")

            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.assigned_agent_id = None

                # Exponential backoff
                delay = 2 ** task.retry_count
                self._logger.info(f"Retrying task {task.id} in {delay}s (attempt {task.retry_count})")
                await asyncio.sleep(delay)
                return await self.execute_task(task)
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now(timezone.utc)

                # Notify callbacks
                for callback in self._on_task_failed:
                    await callback(task)

                raise

        finally:
            if task.id in self._active_tasks and task.status in [
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.TIMEOUT,
            ]:
                del self._active_tasks[task.id]
                self._completed_tasks[task.id] = task

    async def _worker_loop(self) -> None:
        """Background worker loop for processing task queue."""
        while self._running:
            try:
                # Process tasks by priority (highest first)
                for priority in sorted(self._task_queues.keys(), reverse=True):
                    if len(self._active_tasks) >= self._max_concurrent_tasks:
                        break

                    queue = self._task_queues[priority]
                    if queue.empty():
                        continue

                    task = queue.get_nowait()
                    asyncio.create_task(self.execute_task(task))

                await asyncio.sleep(0.1)  # Prevent busy loop

            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(1.0)

    def on_task_complete(
        self,
        callback: Callable[[Task], Awaitable[None]],
    ) -> None:
        """Register a task completion callback.

        Args:
            callback: Callback function.
        """
        self._on_task_complete.append(callback)

    def on_task_failed(
        self,
        callback: Callable[[Task], Awaitable[None]],
    ) -> None:
        """Register a task failure callback.

        Args:
            callback: Callback function.
        """
        self._on_task_failed.append(callback)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID.

        Args:
            task_id: Task ID.

        Returns:
            Optional[Task]: Task or None.
        """
        if task_id in self._active_tasks:
            return self._active_tasks[task_id]
        if task_id in self._completed_tasks:
            return self._completed_tasks[task_id]
        return None

    def get_queue_size(self) -> int:
        """Get total queue size.

        Returns:
            int: Number of pending tasks.
        """
        return sum(q.qsize() for q in self._task_queues.values())

    def get_active_count(self) -> int:
        """Get number of active tasks.

        Returns:
            int: Active task count.
        """
        return len(self._active_tasks)

    def get_stats(self) -> Dict[str, Any]:
        """Get task assigner statistics.

        Returns:
            Dict: Statistics.
        """
        status_counts = {}
        for task in list(self._active_tasks.values()) + list(self._completed_tasks.values()):
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "queue_size": self.get_queue_size(),
            "active_tasks": self.get_active_count(),
            "completed_tasks": len(self._completed_tasks),
            "status_counts": status_counts,
            "max_concurrent": self._max_concurrent_tasks,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert task assigner to dictionary.

        Returns:
            Dict: Task assigner data.
        """
        return {
            "stats": self.get_stats(),
            "active_tasks": [t.to_dict() for t in list(self._active_tasks.values())[:10]],
            "load_balancer": self._load_balancer.to_dict(),
        }
