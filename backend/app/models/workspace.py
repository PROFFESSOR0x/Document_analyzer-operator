"""Workspace model for organizing projects and resources."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.knowledge_entity import KnowledgeEntity


class Workspace(BaseModel):
    """Workspace model for organizing projects and resources.

    Attributes:
        name: Workspace name.
        description: Workspace description.
        owner_id: Owner user ID (foreign key).
        type: Workspace type (personal, team, organization).
        config: Workspace configuration as JSON.
        is_default: Whether this is the user's default workspace.
        color: Workspace color for UI.
        icon: Workspace icon identifier.
        member_count: Number of workspace members.
        storage_used: Storage used in bytes.
        storage_limit: Storage limit in bytes.
    """

    __tablename__ = "workspaces"

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

    # Type
    type: Mapped[str] = mapped_column(
        String(20),
        default="personal",
        nullable=False,
    )

    # Configuration
    config: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )

    # Settings
    is_default: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    color: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    icon: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    # Metrics
    member_count: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
    )
    storage_used: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="Storage used in bytes",
    )
    storage_limit: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Storage limit in bytes, None for unlimited",
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="workspaces",
    )
    knowledge_entities: Mapped[list["KnowledgeEntity"]] = relationship(
        "KnowledgeEntity",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of the workspace.

        Returns:
            str: Workspace representation.
        """
        return f"<Workspace {self.name} (owner={self.owner_id})>"
