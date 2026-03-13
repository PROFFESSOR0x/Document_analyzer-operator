"""Task model for individual work items."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.workflow import Workflow
    from app.models.validation_result import ValidationResult


class Task(BaseModel):
    """Task model representing individual work items.

    Attributes:
        title: Task title.
        description: Task description.
        status: Task status (pending, running, completed, failed, cancelled).
        priority: Task priority (low, medium, high, critical).
        agent_id: Assigned agent ID (foreign key).
        workflow_id: Parent workflow ID (foreign key).
        parent_task_id: Parent task ID for subtasks.
        input_data: Task input data as JSON.
        output_data: Task output data as JSON.
        error_message: Error message if task failed.
        started_at: Task start timestamp.
        completed_at: Task completion timestamp.
        progress: Task progress percentage (0-100).
        retry_count: Number of retry attempts.
        max_retries: Maximum retry attempts allowed.
        timeout: Task timeout in seconds.
        metadata: Additional metadata as JSON.
    """

    __tablename__ = "tasks"

    # Basic info
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        default="medium",
        nullable=False,
    )

    # Foreign keys
    agent_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    workflow_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("workflows.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    parent_task_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Data
    input_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    output_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Progress
    progress: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Retry config
    retry_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    max_retries: Mapped[int] = mapped_column(
        default=3,
        nullable=False,
    )
    timeout: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Timeout in seconds",
    )

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Relationships
    agent: Mapped[Optional["Agent"]] = relationship(
        "Agent",
        back_populates="tasks",
    )
    workflow: Mapped[Optional["Workflow"]] = relationship(
        "Workflow",
        back_populates="tasks",
        foreign_keys=[workflow_id],
    )
    parent_task: Mapped[Optional["Task"]] = relationship(
        "Task",
        remote_side="Task.id",
        backref="subtasks",
    )
    validation_results: Mapped[list["ValidationResult"]] = relationship(
        "ValidationResult",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of the task.

        Returns:
            str: Task representation.
        """
        return f"<Task {self.title} (status={self.status})>"
