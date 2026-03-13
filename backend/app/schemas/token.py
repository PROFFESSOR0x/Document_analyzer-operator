"""Token schemas for JWT authentication."""

from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token response schema."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")


class TokenPayload(BaseModel):
    """Token payload schema for decoded JWT."""

    sub: str = Field(..., description="Subject (user ID)")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")
    type: str = Field(..., description="Token type (access or refresh)")
    jti: Optional[str] = Field(default=None, description="Token ID for blacklist")
