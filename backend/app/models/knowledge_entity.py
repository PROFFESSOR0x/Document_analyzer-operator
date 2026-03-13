"""KnowledgeEntity model for storing knowledge base content."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, String, Text, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.workspace import Workspace


class KnowledgeEntity(BaseModel):
    """Knowledge entity model for storing knowledge base content.

    Attributes:
        workspace_id: Parent workspace ID (foreign key).
        title: Entity title.
        content: Entity content (text or markdown).
        entity_type: Entity type (document, note, snippet, reference).
        source: Source reference (URL, file path, etc.).
        tags: Tags for categorization.
        metadata: Additional metadata as JSON.
        embedding: Vector embedding for semantic search.
        version: Entity version.
        parent_id: Parent entity ID for hierarchical organization.
        is_indexed: Whether the entity has been indexed for search.
    """

    __tablename__ = "knowledge_entities"

    # Foreign keys
    workspace_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Basic info
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Type
    entity_type: Mapped[str] = mapped_column(
        String(30),
        default="document",
        nullable=False,
        index=True,
    )

    # Source
    source: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Organization
    tags: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
    )

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )

    # Embedding for semantic search
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Vector embedding for semantic search",
    )

    # Versioning
    version: Mapped[str] = mapped_column(
        String(20),
        default="1.0.0",
        nullable=False,
    )

    # Indexing
    is_indexed: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="knowledge_entities",
    )
    parent: Mapped[Optional["KnowledgeEntity"]] = relationship(
        "KnowledgeEntity",
        remote_side="KnowledgeEntity.id",
        backref="children",
    )

    # Indexes
    __table_args__ = (
        Index("ix_knowledge_entities_workspace_type", "workspace_id", "entity_type"),
        Index("ix_knowledge_entities_tags", "tags", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        """Return string representation of the knowledge entity.

        Returns:
            str: Knowledge entity representation.
        """
        return f"<KnowledgeEntity {self.title} (type={self.entity_type})>"
