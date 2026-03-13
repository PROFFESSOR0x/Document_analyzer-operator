"""AgentSession model for tracking agent execution sessions."""

from typing import TYPE_CHECKING, Optional
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.agent import Agent


class AgentSession(BaseModel):
    """AgentSession model for tracking agent execution sessions.

    Attributes:
        agent_id: Agent ID (foreign key).
        session_type: Type of session (execution, conversation, etc.).
        status: Session status (active, completed, failed).
        started_at: Session start timestamp.
        ended_at: Session end timestamp.
        context: Session context data.
        metadata: Additional session metadata.
    """

    __tablename__ = "agent_sessions"

    # Foreign keys
    agent_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Session info
    session_type: Mapped[str] = mapped_column(
        String(50),
        default="execution",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        index=True,
    )

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Context and metadata
    context: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    agent: Mapped["Agent"] = relationship(
        "Agent",
        back_populates="sessions",
    )

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            str: Session representation.
        """
        return f"<AgentSession {self.id} (agent={self.agent_id})>"
