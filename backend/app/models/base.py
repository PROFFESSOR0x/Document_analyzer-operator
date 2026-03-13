"""Base model with common fields and utilities."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TimestampMixin:
    """Mixin for adding timestamp fields to models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """Abstract base model with common fields.

    Attributes:
        id: Primary key (UUID).
        created_at: Record creation timestamp.
        updated_at: Record last update timestamp.
        deleted_at: Soft delete timestamp.
        is_deleted: Soft delete flag.
    """

    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    def to_dict(self) -> dict:
        """Convert model to dictionary.

        Returns:
            dict: Model data as dictionary.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
