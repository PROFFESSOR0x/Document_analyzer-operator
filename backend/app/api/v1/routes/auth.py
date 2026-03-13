"""Authentication endpoints."""

from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ActiveUser, get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.core.settings import get_settings
from app.db.session import get_db, get_redis
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshTokenRequest,
)
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse

settings = get_settings()
router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoginResponse:
    """Authenticate user and return JWT tokens.

    Args:
        login_data: Login credentials.
        db: Database session.

    Returns:
        LoginResponse: Access and refresh tokens with user data.

    Raises:
        HTTPException: If credentials are invalid.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is locked
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked. Please try again later.",
        )

    # Update last login and reset failed attempts
    user.last_login = datetime.now(timezone.utc)
    user.failed_login_attempts = 0
    await db.commit()

    # Create tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
async def logout(
    logout_data: LogoutRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    redis: Annotated[object, Depends(get_redis)],
) -> dict:
    """Logout user and blacklist the refresh token.

    Args:
        logout_data: Logout request with refresh token.
        current_user: Current authenticated user.
        redis: Redis client.

    Returns:
        dict: Logout confirmation.
    """
    if redis and settings.token_blacklist_enabled:
        import redis.asyncio as redis_client

        if isinstance(redis, redis_client.Redis):
            # Decode token to get expiration
            payload = decode_token(logout_data.refresh_token)
            if payload:
                exp = payload.get("exp")
                if exp:
                    ttl = exp - int(datetime.now(timezone.utc).timestamp())
                    if ttl > 0:
                        await redis.setex(
                            f"blacklist:{logout_data.refresh_token}",
                            timedelta(seconds=ttl),
                            "blacklisted",
                        )

    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    redis: Annotated[object, Depends(get_redis)],
) -> Token:
    """Refresh access token using refresh token.

    Args:
        refresh_data: Refresh token request.
        redis: Redis client.

    Returns:
        Token: New access and refresh tokens.

    Raises:
        HTTPException: If refresh token is invalid.
    """
    # Check if token is blacklisted
    if redis and settings.token_blacklist_enabled:
        import redis.asyncio as redis_client

        if isinstance(redis, redis_client.Redis):
            is_blacklisted = await redis.exists(f"blacklist:{refresh_data.refresh_token}")
            if is_blacklisted:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                )

    # Decode and validate refresh token
    payload = decode_token(refresh_data.refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # Create new tokens
    user_id = payload.get("sub")
    new_access_token = create_access_token(subject=user_id)
    new_refresh_token = create_refresh_token(subject=user_id)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current authenticated user information.

    Args:
        current_user: Current authenticated user.

    Returns:
        User: User information.
    """
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Register a new user.

    Args:
        user_data: User registration data.
        db: Database session.

    Returns:
        User: Created user information.

    Raises:
        HTTPException: If email or username already exists.
    """
    # Check if email already exists
    email_result = await db.execute(select(User).where(User.email == user_data.email))
    if email_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    username_result = await db.execute(select(User).where(User.username == user_data.username))
    if username_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user
