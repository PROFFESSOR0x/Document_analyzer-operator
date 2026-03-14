"""Setting audit log model for tracking configuration changes."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.application_setting import ApplicationSetting


class SettingAuditLog(BaseModel):
    """Audit log for tracking changes to application settings.

    Attributes:
        setting_id: Foreign key to the setting that was changed.
        old_value: Previous value before change.
        new_value: New value after change.
        changed_by: User who made the change.
        change_reason: Optional reason for the change.
    """

    __tablename__ = "setting_audit_logs"

    # Foreign keys
    setting_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("application_settings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    changed_by_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Change details
    old_value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    new_value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    change_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    setting: Mapped["ApplicationSetting"] = relationship(
        "ApplicationSetting",
        back_populates="audit_logs",
    )
    changed_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[changed_by_id],
    )

    def __repr__(self) -> str:
        """Return string representation of the audit log.

        Returns:
            str: Audit log representation.
        """
        return f"<SettingAuditLog {self.setting_id}: {self.changed_by_id}>"
