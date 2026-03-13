"""User service for business logic operations."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service class for user-related operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize user service.

        Args:
            db: Database session.
        """
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User ID.

        Returns:
            Optional[User]: User if found, None otherwise.
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            email: User email.

        Returns:
            Optional[User]: User if found, None otherwise.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: User username.

        Returns:
            Optional[User]: User if found, None otherwise.
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user.

        Args:
            user_data: User creation data.

        Returns:
            User: Created user.
        """
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update(self, user: User, user_data: UserUpdate) -> User:
        """Update user information.

        Args:
            user: User to update.
            user_data: Update data.

        Returns:
            User: Updated user.
        """
        update_data = user_data.model_dump(exclude_unset=True)

        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password.

        Args:
            email: User email.
            password: User password.

        Returns:
            Optional[User]: Authenticated user if successful, None otherwise.
        """
        user = await self.get_by_email(email)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    async def record_login(self, user: User) -> User:
        """Record successful login.

        Args:
            user: User who logged in.

        Returns:
            User: Updated user.
        """
        user.last_login = datetime.now(timezone.utc)
        user.failed_login_attempts = 0
        user.locked_until = None

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def record_failed_login(self, user: User, max_attempts: int = 5, lockout_minutes: int = 30) -> User:
        """Record failed login attempt.

        Args:
            user: User who failed to log in.
            max_attempts: Maximum failed attempts before lockout.
            lockout_minutes: Minutes to lock account after max attempts.

        Returns:
            User: Updated user.
        """
        from datetime import timedelta

        user.failed_login_attempts += 1

        if user.failed_login_attempts >= max_attempts:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=lockout_minutes)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def deactivate(self, user: User) -> User:
        """Deactivate user account.

        Args:
            user: User to deactivate.

        Returns:
            User: Updated user.
        """
        user.is_active = False

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def verify_email(self, user: User) -> User:
        """Mark user email as verified.

        Args:
            user: User to verify.

        Returns:
            User: Updated user.
        """
        user.is_verified = True

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user
