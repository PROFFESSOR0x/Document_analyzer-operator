"""Workflow Execution model for tracking workflow runs."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workflow import Workflow


class WorkflowExecution(BaseModel):
    """Workflow execution model for tracking workflow runs.

    Attributes:
        workflow_id: Workflow definition ID (foreign key).
        execution_id: Unique execution identifier.
        owner_id: Owner user ID (foreign key).
        status: Execution status (pending, running, completed, failed, cancelled).
        workflow_type: Type of workflow executed.
        input_data: Input data for the execution.
        output_data: Output data from the execution.
        error_message: Error message if execution failed.
        temporal_run_id: Temporal workflow run ID.
        progress: Execution progress percentage (0-100).
        current_task: Current executing task ID.
        started_at: Execution start timestamp.
        completed_at: Execution completion timestamp.
        scheduled_at: Scheduled execution time.
        cron_expression: Cron expression for scheduled workflows.
        metadata: Additional metadata.
    """

    __tablename__ = "workflow_executions"

    # Foreign keys
    workflow_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Execution info
    execution_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique execution identifier",
    )
    workflow_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )

    # Data
    input_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Input data for the execution",
    )
    output_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Output data from the execution",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Temporal info
    temporal_run_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Temporal workflow run ID",
    )

    # Progress
    progress: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    current_task: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Current executing task ID",
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
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Scheduled execution time",
    )

    # Scheduling
    cron_expression: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Cron expression for scheduled workflows",
    )

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional metadata",
    )

    # Relationships
    workflow: Mapped["Workflow"] = relationship(
        "Workflow",
        back_populates="executions",
    )
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="workflow_executions",
    )

    def __repr__(self) -> str:
        """Return string representation of the workflow execution.

        Returns:
            str: Workflow execution representation.
        """
        return f"<WorkflowExecution {self.execution_id} (status={self.status})>"


# Add executions relationship to Workflow model
# This will be added via SQLAlchemy event listener
@event.listens_for(Workflow, "configure")
def configure_workflow_executions_relationship(mapper, cls):
    """Configure the executions relationship on Workflow model."""
    from app.models.workflow import Workflow

    if not hasattr(Workflow, "executions"):
        Workflow.executions = relationship(
            "WorkflowExecution",
            back_populates="workflow",
            cascade="all, delete-orphan",
        )


# Add workflow_executions relationship to User model
@event.listens_for(User, "configure")
def configure_user_workflow_executions_relationship(mapper, cls):
    """Configure the workflow_executions relationship on User model."""
    from app.models.user import User

    if not hasattr(User, "workflow_executions"):
        User.workflow_executions = relationship(
            "WorkflowExecution",
            back_populates="owner",
            cascade="all, delete-orphan",
        )
