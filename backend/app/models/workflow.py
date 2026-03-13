"""Workflow model for orchestrating multi-agent processes."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task
    from app.models.workflow_execution import WorkflowExecution


class Workflow(BaseModel):
    """Workflow model for multi-agent orchestration.

    Attributes:
        name: Workflow name.
        description: Workflow description.
        owner_id: Owner user ID (foreign key).
        status: Workflow status (draft, active, paused, archived).
        definition: Workflow definition as JSON (nodes, edges, config).
        trigger_type: Trigger type (manual, scheduled, event).
        trigger_config: Trigger configuration as JSON.
        is_public: Whether workflow is publicly accessible.
        version: Workflow version.
        execution_count: Number of times workflow has been executed.
    """

    __tablename__ = "workflows"

    # Basic info
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Foreign keys
    owner_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        nullable=False,
    )

    # Definition
    definition: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Workflow graph definition with nodes and edges",
    )

    # Trigger
    trigger_type: Mapped[str] = mapped_column(
        String(20),
        default="manual",
        nullable=False,
    )
    trigger_config: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Trigger configuration (schedule, event filters)",
    )

    # Visibility
    is_public: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    # Versioning
    version: Mapped[str] = mapped_column(
        String(20),
        default="1.0.0",
        nullable=False,
    )

    # Metrics
    execution_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="workflows",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="workflow",
        cascade="all, delete-orphan",
        foreign_keys="Task.workflow_id",
    )
    executions: Mapped[list["WorkflowExecution"]] = relationship(
        "WorkflowExecution",
        back_populates="workflow",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of the workflow.

        Returns:
            str: Workflow representation.
        """
        return f"<Workflow {self.name} (owner={self.owner_id})>"
