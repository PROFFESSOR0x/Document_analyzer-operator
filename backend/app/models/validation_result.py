"""ValidationResult model for storing validation outcomes."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.task import Task


class ValidationResult(BaseModel):
    """Validation result model for storing validation outcomes.

    Attributes:
        task_id: Associated task ID (foreign key).
        validator_name: Name of the validator that produced this result.
        status: Validation status (pending, passed, failed, warning).
        severity: Result severity (info, low, medium, high, critical).
        category: Validation category (format, content, security, compliance).
        message: Validation result message.
        details: Detailed validation results as JSON.
        rule_id: ID of the validation rule that was applied.
        rule_name: Name of the validation rule.
        evidence: Evidence supporting the validation result.
        remediation: Suggested remediation steps.
        validated_at: Validation timestamp.
        is_resolved: Whether the issue has been resolved.
        resolved_at: Resolution timestamp.
        resolved_by: User ID who resolved the issue.
    """

    __tablename__ = "validation_results"

    # Foreign keys
    task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Validator info
    validator_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        default="info",
        nullable=False,
        index=True,
    )

    # Category
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # Results
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Rule info
    rule_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    rule_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # Evidence
    evidence: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Evidence supporting the validation result",
    )

    # Remediation
    remediation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Timing
    validated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Resolution
    is_resolved: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolved_by: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
    )

    # Relationships
    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="validation_results",
    )

    def __repr__(self) -> str:
        """Return string representation of the validation result.

        Returns:
            str: Validation result representation.
        """
        return f"<ValidationResult {self.status} ({self.severity})>"
