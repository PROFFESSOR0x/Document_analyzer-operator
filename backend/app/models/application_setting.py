"""Application settings model for managing environment variables and configuration."""

from typing import TYPE_CHECKING, Optional
from enum import Enum

from sqlalchemy import String, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.setting_audit_log import SettingAuditLog


class SettingValueType(str, Enum):
    """Enumeration of setting value types."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    SECRET = "secret"


class ApplicationSetting(BaseModel):
    """Application setting model for storing configuration in database.

    Attributes:
        key: Unique setting key name (e.g., "llm.default_provider").
        value: Setting value (stored as text).
        value_type: Type of value (string, integer, float, boolean, json, secret).
        category: Category grouping (e.g., "llm", "database", "security").
        description: Human-readable description of the setting.
        is_secret: Whether the value should be encrypted.
        is_editable: Whether the UI can modify this setting.
        validation_schema: Pydantic schema for validation (JSONB).
        default_value: Default value if not set.
        updated_by: User who last updated the setting.
    """

    __tablename__ = "application_settings"

    # Setting identification
    key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Type and category
    value_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="string",
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Metadata
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    is_secret: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_editable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Validation
    validation_schema: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
    )
    default_value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Audit
    updated_by_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    updated_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[updated_by_id],
    )
    audit_logs: Mapped[list["SettingAuditLog"]] = relationship(
        "SettingAuditLog",
        back_populates="setting",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of the setting.

        Returns:
            str: Setting representation.
        """
        return f"<ApplicationSetting {self.key}={self.value}>"
