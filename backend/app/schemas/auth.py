"""Authentication schemas for login/logout operations."""

from pydantic import BaseModel, EmailStr, Field

from app.schemas.token import Token
from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Schema for login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class LoginResponse(Token):
    """Schema for login response with user data."""

    user: UserResponse = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="Refresh token")


class LogoutRequest(BaseModel):
    """Schema for logout request."""

    refresh_token: str = Field(..., description="Refresh token to blacklist")
