"""Pytest fixtures and configuration for testing."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any, Optional

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.security import get_password_hash
from app.core.settings import Settings, get_settings
from app.db.session import Base, get_db
from app.main import create_application
from app.models.user import User


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests.

    Yields:
        asyncio.AbstractEventLoop: Event loop instance.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create test settings.

    Returns:
        Settings: Test settings instance.
    """
    return Settings(
        app_name="Test App",
        app_version="0.1.0",
        debug=True,
        environment="testing",
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379/1",
        secret_key="test-secret-key-for-testing-only-32chars",
        cors_origins=["http://test"],
    )


@pytest_asyncio.fixture(scope="function")
async def test_engine(test_settings: Settings):
    """Create test database engine.

    Args:
        test_settings: Test settings.

    Yields:
        Async engine instance.
    """
    engine = create_async_engine(
        test_settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(
    test_engine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session.

    Args:
        test_engine: Test database engine.

    Yields:
        AsyncSession: Test database session.
    """
    async_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        yield session


@pytest.fixture(scope="function")
def test_app(test_settings: Settings) -> FastAPI:
    """Create test FastAPI application.

    Args:
        test_settings: Test settings.

    Returns:
        FastAPI: Test application instance.
    """
    app = create_application()
    app.state.settings = test_settings
    return app


@pytest_asyncio.fixture(scope="function")
async def client(
    test_app: FastAPI,
    test_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client.

    Args:
        test_app: Test application.
        test_session: Test database session.

    Yields:
        AsyncClient: Test HTTP client.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    test_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as ac:
        yield ac

    test_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sync_client(test_app: FastAPI) -> Generator[TestClient, None, None]:
    """Create synchronous test client.

    Args:
        test_app: Test application.

    Yields:
        TestClient: Synchronous test client.
    """
    with TestClient(test_app) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def test_user(test_session: AsyncSession) -> User:
    """Create a test user.

    Args:
        test_session: Test database session.

    Returns:
        User: Test user instance.
    """
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPassword123"),
        full_name="Test User",
        is_active=True,
        is_verified=True,
    )

    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    return user


@pytest_asyncio.fixture(scope="function")
async def test_superuser(test_session: AsyncSession) -> User:
    """Create a test superuser.

    Args:
        test_session: Test database session.

    Returns:
        User: Test superuser instance.
    """
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("AdminPassword123"),
        full_name="Admin User",
        is_active=True,
        is_verified=True,
        is_superuser=True,
        role="superadmin",
    )

    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    """Create authentication headers for test client.

    Note: This requires a valid token which should be obtained
    through the login endpoint in actual tests.

    Returns:
        dict: Headers dictionary with Authorization.
    """
    return {"Authorization": "Bearer test-token"}
