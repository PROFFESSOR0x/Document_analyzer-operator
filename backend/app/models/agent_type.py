"""AgentType model for defining agent categories."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.agent import Agent


class AgentType(BaseModel):
    """Agent type model for categorizing agents.

    Attributes:
        name: Unique type name (e.g., 'analyzer', 'summarizer').
        description: Type description.
        icon: Icon identifier for UI display.
        color: Color code for UI display.
        is_active: Whether this type is available for use.
        default_config: Default configuration JSON for this type.
    """

    __tablename__ = "agent_types"

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    icon: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    color: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    default_config: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON configuration template",
    )

    # Relationships
    agents: Mapped[list["Agent"]] = relationship(
        "Agent",
        back_populates="agent_type",
    )

    def __repr__(self) -> str:
        """Return string representation of the agent type.

        Returns:
            str: Agent type representation.
        """
        return f"<AgentType {self.name}>"
