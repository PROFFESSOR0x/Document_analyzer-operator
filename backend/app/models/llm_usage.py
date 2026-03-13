"""LLM Usage Log model for tracking API usage."""

from typing import TYPE_CHECKING, Optional
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Integer, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.llm_provider import LLMProvider
    from app.models.user import User
    from app.models.agent import Agent


class LLMUsageLog(BaseModel):
    """LLM Usage Log model for tracking API usage statistics.

    Attributes:
        provider_id: LLM provider ID (foreign key).
        user_id: User ID who made the request (foreign key).
        agent_id: Agent ID that made the request (nullable foreign key).
        model_used: Model name used for the request.
        tokens_input: Number of input tokens.
        tokens_output: Number of output tokens.
        cost_usd: Cost in USD (nullable for free providers).
        request_type: Type of request (completion, embedding, chat).
        status: Request status (success, failed).
        error_message: Error message if failed.
        response_time_ms: Response time in milliseconds.
        created_at: Request timestamp.
    """

    __tablename__ = "llm_usage_logs"

    # Foreign keys
    provider_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("llm_providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    agent_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Usage details
    model_used: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    tokens_input: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    tokens_output: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    cost_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 6),
        nullable=True,
    )

    # Request info
    request_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    response_time_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Timestamp (created_at from BaseModel)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Relationships
    provider: Mapped["LLMProvider"] = relationship(
        "LLMProvider",
        back_populates="usage_logs",
    )

    def __repr__(self) -> str:
        """Return string representation of the usage log.

        Returns:
            str: Usage log representation.
        """
        return f"<LLMUsageLog {self.id} ({self.model_used})>"
