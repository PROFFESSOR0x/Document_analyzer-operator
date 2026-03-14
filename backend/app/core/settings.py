"""Application settings management using Pydantic Settings."""

from functools import lru_cache
from typing import Optional

from pydantic import Field, PostgresDsn, RedisDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings.

    All settings can be configured via environment variables.
    Environment variable names are prefixed with APP_ for non-database settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Document Analyzer Operator", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode flag")
    environment: str = Field(default="development", description="Deployment environment")
    api_prefix: str = Field(default="/api/v1", description="API route prefix")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")
    reload: bool = Field(default=False, description="Auto-reload for development")

    # Database - PostgreSQL
    postgres_user: str = Field(default="postgres", description="PostgreSQL username")
    postgres_password: str = Field(default="postgres", description="PostgreSQL password")
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="document_analyzer", description="PostgreSQL database name")
    database_url: Optional[PostgresDsn] = Field(
        default=None, description="Full PostgreSQL connection URL"
    )
    db_echo: bool = Field(default=False, description="Enable SQL query logging")
    db_pool_size: int = Field(default=10, description="Database connection pool size")
    db_max_overflow: int = Field(default=20, description="Maximum overflow connections")
    db_pool_timeout: int = Field(default=30, description="Connection pool timeout in seconds")
    db_pool_recycle: int = Field(default=1800, description="Connection recycle time in seconds")

    # Redis
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_url: Optional[RedisDsn] = Field(default=None, description="Full Redis connection URL")
    redis_ttl: int = Field(default=3600, description="Default Redis TTL in seconds")

    # JWT Authentication
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT secret key for signing tokens",
    )
    algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration time in days"
    )
    token_blacklist_enabled: bool = Field(
        default=True, description="Enable token blacklist with Redis"
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow CORS credentials")
    cors_allow_methods: list[str] = Field(
        default=["*"], description="Allowed CORS methods"
    )
    cors_allow_headers: list[str] = Field(
        default=["*"], description="Allowed CORS headers"
    )

    # Security
    bcrypt_rounds: int = Field(default=12, description="Bcrypt hashing rounds")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")

    # LLM Providers API Keys
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    google_api_key: Optional[str] = Field(default=None, description="Google API key")

    # File Storage - MinIO/S3
    storage_provider: str = Field(
        default="minio", description="Storage provider (minio, s3, local)"
    )
    storage_endpoint: str = Field(default="localhost:9000", description="Storage endpoint URL")
    storage_access_key: str = Field(default="minioadmin", description="Storage access key")
    storage_secret_key: str = Field(default="minioadmin", description="Storage secret key")
    storage_bucket: str = Field(
        default="documents", description="Default storage bucket name"
    )
    storage_use_ssl: bool = Field(default=False, description="Use SSL for storage connection")
    storage_region: str = Field(default="us-east-1", description="Storage region")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )
    log_file: Optional[str] = Field(default=None, description="Log file path")

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_database_url(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Assemble PostgreSQL connection URL from components."""
        if v:
            return v

        values = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("postgres_user", "postgres"),
            password=values.get("postgres_password", "postgres"),
            host=values.get("postgres_host", "localhost"),
            port=values.get("postgres_port", 5432),
            path=values.get("postgres_db", "document_analyzer"),
        )

    @field_validator("redis_url", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Assemble Redis connection URL from components."""
        if v:
            return v

        values = info.data
        password = values.get("redis_password")
        host = values.get("redis_host", "localhost")
        port = values.get("redis_port", 6379)
        db = values.get("redis_db", 0)

        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Application settings instance.
    """
    return Settings()
