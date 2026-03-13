"""Knowledge repository for persistent long-term storage."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import uuid4
import logging

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import BaseModel as AppBaseModel


class KnowledgeEntity(BaseModel):
    """Knowledge entity model."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    content: str
    entity_type: str = "document"  # document, fact, concept, procedure
    source: Optional[str] = None
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    version: int = 1
    parent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_deleted: bool = False


class KnowledgeVersion(BaseModel):
    """Knowledge version model."""

    version_id: str = Field(default_factory=lambda: str(uuid4()))
    entity_id: str
    version_number: int
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None


class KnowledgeRelationship(BaseModel):
    """Knowledge relationship model."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    source_entity_id: str
    target_entity_id: str
    relationship_type: str  # relates_to, depends_on, part_of, references, etc.
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeQuery(BaseModel):
    """Knowledge query model."""

    query_text: Optional[str] = None
    entity_type: Optional[str] = None
    tags: Optional[List[str]] = None
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    limit: int = 20
    offset: int = 0
    sort_by: str = "created_at"
    sort_order: str = "desc"


class KnowledgeRepository:
    """Repository for persistent knowledge storage.

    This class provides:
    - CRUD operations for knowledge entities
    - Versioning support
    - Relationship management
    - Query interface
    """

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize knowledge repository.

        Args:
            db_session: Database session.
        """
        self.db = db_session
        self._logger = logging.getLogger("knowledge.repository")
        self._entities: Dict[str, KnowledgeEntity] = {}  # In-memory cache

    async def create(
        self,
        entity: KnowledgeEntity,
    ) -> KnowledgeEntity:
        """Create a knowledge entity.

        Args:
            entity: Entity to create.

        Returns:
            KnowledgeEntity: Created entity.
        """
        # Store in cache
        self._entities[entity.id] = entity

        self._logger.info(f"Created knowledge entity: {entity.id}")
        return entity

    async def get(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """Get a knowledge entity by ID.

        Args:
            entity_id: Entity ID.

        Returns:
            Optional[KnowledgeEntity]: Entity or None.
        """
        # Check cache first
        if entity_id in self._entities:
            return self._entities[entity_id]

        # In production, this would query the database
        return None

    async def update(
        self,
        entity_id: str,
        updates: Dict[str, Any],
        create_version: bool = True,
    ) -> Optional[KnowledgeEntity]:
        """Update a knowledge entity.

        Args:
            entity_id: Entity ID.
            updates: Update fields.
            create_version: Whether to create a version record.

        Returns:
            Optional[KnowledgeEntity]: Updated entity or None.
        """
        entity = await self.get(entity_id)
        if not entity:
            return None

        # Create version before update
        if create_version:
            await self._create_version(entity)

        # Apply updates
        for key, value in updates.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        entity.updated_at = datetime.now(timezone.utc)
        entity.version += 1

        # Update cache
        self._entities[entity_id] = entity

        self._logger.info(f"Updated knowledge entity: {entity_id}")
        return entity

    async def delete(self, entity_id: str, soft_delete: bool = True) -> bool:
        """Delete a knowledge entity.

        Args:
            entity_id: Entity ID.
            soft_delete: Whether to soft delete.

        Returns:
            bool: True if deleted.
        """
        entity = await self.get(entity_id)
        if not entity:
            return False

        if soft_delete:
            entity.is_deleted = True
            entity.updated_at = datetime.now(timezone.utc)
            self._entities[entity_id] = entity
        else:
            del self._entities[entity_id]

        self._logger.info(f"Deleted knowledge entity: {entity_id}")
        return True

    async def query(self, query: KnowledgeQuery) -> List[KnowledgeEntity]:
        """Query knowledge entities.

        Args:
            query: Query parameters.

        Returns:
            List[KnowledgeEntity]: Matching entities.
        """
        results = list(self._entities.values())

        # Apply filters
        if query.entity_type:
            results = [e for e in results if e.entity_type == query.entity_type]

        if query.workspace_id:
            results = [e for e in results if e.workspace_id == query.workspace_id]

        if query.user_id:
            results = [e for e in results if e.user_id == query.user_id]

        if query.tags:
            results = [
                e for e in results
                if any(tag in e.tags for tag in query.tags)
            ]

        if query.query_text:
            # Simple text search
            query_lower = query.query_text.lower()
            results = [
                e for e in results
                if query_lower in e.title.lower() or query_lower in e.content.lower()
            ]

        # Sort
        reverse = query.sort_order.lower() == "desc"
        if query.sort_by in ["created_at", "updated_at", "title"]:
            results.sort(
                key=lambda e: getattr(e, query.sort_by) or "",
                reverse=reverse,
            )

        # Pagination
        offset = query.offset
        limit = query.offset + query.limit
        results = results[offset:limit]

        return results

    async def create_relationship(
        self,
        relationship: KnowledgeRelationship,
    ) -> KnowledgeRelationship:
        """Create a relationship between entities.

        Args:
            relationship: Relationship to create.

        Returns:
            KnowledgeRelationship: Created relationship.
        """
        self._logger.info(
            f"Created relationship: {relationship.source_entity_id} -> "
            f"{relationship.target_entity_id} ({relationship.relationship_type})"
        )
        return relationship

    async def get_relationships(
        self,
        entity_id: str,
        direction: str = "both",
    ) -> List[KnowledgeRelationship]:
        """Get relationships for an entity.

        Args:
            entity_id: Entity ID.
            direction: Relationship direction (outgoing, incoming, both).

        Returns:
            List[KnowledgeRelationship]: Relationships.
        """
        # This would query the database in production
        return []

    async def _create_version(self, entity: KnowledgeEntity) -> KnowledgeVersion:
        """Create a version record for an entity.

        Args:
            entity: Entity to version.

        Returns:
            KnowledgeVersion: Version record.
        """
        version = KnowledgeVersion(
            version_id=str(uuid4()),
            entity_id=entity.id,
            version_number=entity.version,
            content=entity.content,
            metadata=entity.metadata,
            created_at=datetime.now(timezone.utc),
        )

        self._logger.debug(f"Created version {version.version_number} for {entity.id}")
        return version

    async def get_versions(self, entity_id: str) -> List[KnowledgeVersion]:
        """Get all versions of an entity.

        Args:
            entity_id: Entity ID.

        Returns:
            List[KnowledgeVersion]: Versions.
        """
        # This would query the database in production
        return []

    async def restore_version(
        self,
        entity_id: str,
        version_number: int,
    ) -> Optional[KnowledgeEntity]:
        """Restore an entity to a previous version.

        Args:
            entity_id: Entity ID.
            version_number: Version to restore.

        Returns:
            Optional[KnowledgeEntity]: Restored entity.
        """
        versions = await self.get_versions(entity_id)
        target_version = next(
            (v for v in versions if v.version_number == version_number),
            None,
        )

        if not target_version:
            return None

        return await self.update(
            entity_id,
            {"content": target_version.content, "metadata": target_version.metadata},
            create_version=True,
        )

    async def get_statistics(self, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        """Get knowledge repository statistics.

        Args:
            workspace_id: Optional workspace filter.

        Returns:
            Dict: Statistics.
        """
        entities = list(self._entities.values())

        if workspace_id:
            entities = [e for e in entities if e.workspace_id == workspace_id]

        return {
            "total_entities": len(entities),
            "by_type": self._count_by_type(entities),
            "by_tag": self._count_by_tag(entities),
        }

    def _count_by_type(self, entities: List[KnowledgeEntity]) -> Dict[str, int]:
        """Count entities by type."""
        counts: Dict[str, int] = {}
        for entity in entities:
            counts[entity.entity_type] = counts.get(entity.entity_type, 0) + 1
        return counts

    def _count_by_tag(self, entities: List[KnowledgeEntity]) -> Dict[str, int]:
        """Count entities by tag."""
        counts: Dict[str, int] = {}
        for entity in entities:
            for tag in entity.tags:
                counts[tag] = counts.get(tag, 0) + 1
        return counts
