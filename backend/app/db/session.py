"""Database session management for SQLAlchemy async operations."""

from collections.abc import AsyncGenerator
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.logging_config import get_logger
from app.core.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session.

    Yields:
        AsyncSession: Database session instance.
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# Redis connection
_redis_client: Optional[object] = None


async def get_redis() -> object:
    """Dependency for getting Redis client.

    Returns:
        Redis client instance.
    """
    global _redis_client

    if _redis_client is None:
        try:
            import redis.asyncio as redis

            _redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("Redis connection established")
        except ImportError:
            logger.warning("Redis not installed, caching disabled")
            return None
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return None

    return _redis_client


async def init_db() -> None:
    """Initialize database connection and create tables.

    Note: In production, use Alembic migrations instead of creating tables directly.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()

    global _redis_client
    if _redis_client:
        try:
            import redis.asyncio as redis

            if isinstance(_redis_client, redis.Redis):
                await _redis_client.close()
                logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")

    logger.info("Database connections closed")
