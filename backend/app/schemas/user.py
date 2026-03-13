"""User schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(
        default=None, max_length=100, description="Full name"
    )


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 characters)",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for user profile updates."""

    email: Optional[EmailStr] = Field(default=None, description="Email address")
    username: Optional[str] = Field(
        default=None, min_length=3, max_length=50, description="Username"
    )
    full_name: Optional[str] = Field(
        default=None, max_length=100, description="Full name"
    )
    avatar_url: Optional[str] = Field(default=None, description="Avatar URL")
    bio: Optional[str] = Field(default=None, description="User biography")
    password: Optional[str] = Field(
        default=None, min_length=8, max_length=100, description="New password"
    )


class UserResponse(UserBase):
    """Schema for user response data."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="User ID")
    is_active: bool = Field(default=True, description="Account active status")
    is_verified: bool = Field(default=False, description="Email verification status")
    role: str = Field(default="user", description="User role")
    avatar_url: Optional[str] = Field(default=None, description="Avatar URL")
    bio: Optional[str] = Field(default=None, description="User biography")
    created_at: datetime = Field(..., description="Account creation timestamp")


class UserInDB(UserResponse):
    """Schema for user data stored in database."""

    hashed_password: str = Field(..., description="Hashed password")
    is_superuser: bool = Field(default=False, description="Superuser status")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    failed_login_attempts: int = Field(
        default=0, description="Failed login attempts count"
    )
    locked_until: Optional[datetime] = Field(
        default=None, description="Account lock expiration"
    )
