"""User model for authentication and user management."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.workflow import Workflow
    from app.models.workspace import Workspace


class User(BaseModel):
    """User model for authentication and authorization.

    Attributes:
        email: Unique email address for login.
        username: Unique username.
        hashed_password: Bcrypt hashed password.
        full_name: User's full name.
        is_active: Account active status.
        is_superuser: Superuser privileges flag.
        is_verified: Email verification status.
        role: User role for RBAC (user, admin, superadmin).
        avatar_url: Profile picture URL.
        bio: User biography.
        last_login: Last successful login timestamp.
        failed_login_attempts: Count of consecutive failed login attempts.
        locked_until: Account lock expiration timestamp.
    """

    __tablename__ = "users"

    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Profile
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # RBAC
    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False,
    )

    # Security
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    agents: Mapped[list["Agent"]] = relationship(
        "Agent",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    workflows: Mapped[list["Workflow"]] = relationship(
        "Workflow",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    workspaces: Mapped[list["Workspace"]] = relationship(
        "Workspace",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of the user.

        Returns:
            str: User representation.
        """
        return f"<User {self.username} ({self.email})>"

    @property
    def is_locked(self) -> bool:
        """Check if the account is currently locked.

        Returns:
            bool: True if account is locked, False otherwise.
        """
        if self.locked_until is None:
            return False
        from datetime import timezone

        return datetime.now(timezone.utc) < self.locked_until
