"""AgentMetric model for storing agent performance metrics."""

from typing import TYPE_CHECKING, Optional
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Float, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.agent import Agent


class AgentMetric(BaseModel):
    """AgentMetric model for storing agent performance metrics.

    Attributes:
        agent_id: Agent ID (foreign key).
        metric_type: Type of metric (execution, error, performance).
        metric_name: Name of the metric.
        metric_value: Numeric value of the metric.
        timestamp: Metric timestamp.
        metadata: Additional metric metadata.
    """

    __tablename__ = "agent_metrics"

    # Foreign keys
    agent_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Metric info
    metric_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    metric_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Additional data
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )
    task_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    # Relationships
    agent: Mapped["Agent"] = relationship(
        "Agent",
        back_populates="metrics",
    )

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            str: Metric representation.
        """
        return f"<AgentMetric {self.metric_name}={self.metric_value} (agent={self.agent_id})>"
