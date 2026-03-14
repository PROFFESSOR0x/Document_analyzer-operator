"""
Document Analyzer Operator - Database Configuration Module
Database connection configuration for native deployment.
"""

import os
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class DatabaseConfig:
    """Database configuration for native deployment."""
    
    # Database URL from environment
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://document_analyzer:password@localhost:5432/document_analyzer"
    )
    
    # Pool configuration
    POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))
    MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 10))
    POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", 30))
    POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", 1800))
    
    # Echo SQL queries (for debugging)
    ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
    
    # Engine configuration
    engine = None
    async_session_maker = None
    
    @classmethod
    def get_engine(cls):
        """Get or create the database engine."""
        if cls.engine is None:
            cls.engine = create_async_engine(
                cls.DATABASE_URL,
                pool_size=cls.POOL_SIZE,
                max_overflow=cls.MAX_OVERFLOW,
                pool_timeout=cls.POOL_TIMEOUT,
                pool_recycle=cls.POOL_RECYCLE,
                echo=cls.ECHO,
                pool_pre_ping=True,  # Enable connection health checks
            )
        return cls.engine
    
    @classmethod
    def get_session_maker(cls):
        """Get or create the session maker."""
        if cls.async_session_maker is None:
            cls.async_session_maker = async_sessionmaker(
                cls.get_engine(),
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return cls.async_session_maker
    
    @classmethod
    async def get_db(cls):
        """Get database session (dependency for FastAPI)."""
        async with cls.get_session_maker()() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @classmethod
    async def check_connection(cls) -> bool:
        """Check database connection."""
        try:
            engine = cls.get_engine()
            async with engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    @classmethod
    async def close(cls):
        """Close database connections."""
        if cls.engine:
            await cls.engine.dispose()


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


# Convenience function for getting database URL
def get_database_url(
    user: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: Optional[str] = None,
) -> str:
    """
    Build database URL from components.
    
    Args:
        user: Database username
        password: Database password
        host: Database host
        port: Database port
        database: Database name
    
    Returns:
        PostgreSQL connection URL
    """
    user = user or os.getenv("POSTGRES_USER", "document_analyzer")
    password = password or os.getenv("POSTGRES_PASSWORD")
    host = host or os.getenv("POSTGRES_HOST", "localhost")
    port = port or int(os.getenv("POSTGRES_PORT", 5432))
    database = database or os.getenv("POSTGRES_DB", "document_analyzer")
    
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
