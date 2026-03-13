"""Agent model for AI agent instances."""

from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.agent_type import AgentType
    from app.models.task import Task
    from app.models.agent_session import AgentSession
    from app.models.agent_metric import AgentMetric


class Agent(BaseModel):
    """Agent model representing AI agent instances.

    Attributes:
        name: Agent name.
        description: Agent description.
        owner_id: Owner user ID (foreign key).
        agent_type_id: Agent type ID (foreign key).
        status: Agent status (idle, running, paused, error).
        config: Agent configuration as JSON.
        system_prompt: Custom system prompt for the agent.
        model: LLM model identifier.
        temperature: Model temperature setting.
        max_tokens: Maximum tokens for responses.
        is_public: Whether agent is publicly accessible.
        version: Agent version for tracking changes.
    """

    __tablename__ = "agents"

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
    agent_type_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("agent_types.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="idle",
        nullable=False,
    )

    # Configuration
    config: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )
    system_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # LLM settings
    model: Mapped[str] = mapped_column(
        String(50),
        default="gpt-4",
        nullable=False,
    )
    temperature: Mapped[float] = mapped_column(
        default=0.7,
        nullable=False,
    )
    max_tokens: Mapped[Optional[int]] = mapped_column(
        nullable=True,
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

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="agents",
    )
    agent_type: Mapped[Optional["AgentType"]] = relationship(
        "AgentType",
        back_populates="agents",
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[List["AgentSession"]] = relationship(
        "AgentSession",
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    metrics: Mapped[List["AgentMetric"]] = relationship(
        "AgentMetric",
        back_populates="agent",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of the agent.

        Returns:
            str: Agent representation.
        """
        return f"<Agent {self.name} (owner={self.owner_id})>"
