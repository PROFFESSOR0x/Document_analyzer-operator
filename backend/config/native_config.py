"""
Document Analyzer Operator - Native Configuration Module
Configuration settings specific to native (non-Docker) deployment.
"""

import os
from pathlib import Path
from typing import Optional


class NativeConfig:
    """Configuration for native deployment."""
    
    # Base directories
    BASE_DIR = Path(__file__).parent.parent
    ROOT_DIR = BASE_DIR.parent
    
    # Application directories
    LOGS_DIR = ROOT_DIR / "logs"
    UPLOADS_DIR = ROOT_DIR / "uploads"
    TEMP_DIR = ROOT_DIR / "tmp"
    STORAGE_DIR = ROOT_DIR / "storage"
    
    # Ensure directories exist
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        for directory in [cls.LOGS_DIR, cls.UPLOADS_DIR, cls.TEMP_DIR, cls.STORAGE_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    # Service configuration
    class Services:
        """Native service configuration."""
        
        # PostgreSQL
        POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
        POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
        POSTGRES_USER = os.getenv("POSTGRES_USER", "document_analyzer")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        POSTGRES_DB = os.getenv("POSTGRES_DB", "document_analyzer")
        
        # Redis
        REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
        REDIS_DB = int(os.getenv("REDIS_DB", 0))
        REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None
        
        @classmethod
        def get_database_url(cls) -> str:
            """Get PostgreSQL connection URL."""
            return (
                f"postgresql+asyncpg://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
                f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
            )
        
        @classmethod
        def get_redis_url(cls) -> str:
            """Get Redis connection URL."""
            if cls.REDIS_PASSWORD:
                return f"redis://:{cls.REDIS_PASSWORD}@{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
            return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
        
        @classmethod
        def check_connections(cls) -> dict:
            """Check service connections."""
            results = {
                "postgres": False,
                "redis": False,
            }
            
            # Check PostgreSQL
            try:
                import asyncio
                import asyncpg
                
                async def check_pg():
                    conn = await asyncpg.connect(
                        host=cls.POSTGRES_HOST,
                        port=cls.POSTGRES_PORT,
                        user=cls.POSTGRES_USER,
                        password=cls.POSTGRES_PASSWORD,
                        database=cls.POSTGRES_DB
                    )
                    await conn.close()
                    return True
                
                results["postgres"] = asyncio.run(check_pg())
            except Exception:
                results["postgres"] = False
            
            # Check Redis
            try:
                import redis
                
                r = redis.Redis(
                    host=cls.REDIS_HOST,
                    port=cls.REDIS_PORT,
                    db=cls.REDIS_DB,
                    password=cls.REDIS_PASSWORD,
                    decode_responses=False
                )
                results["redis"] = r.ping()
            except Exception:
                results["redis"] = False
            
            return results
    
    # Server configuration
    class Server:
        """Native server configuration."""
        
        HOST = os.getenv("APP_HOST", "127.0.0.1")
        PORT = int(os.getenv("APP_PORT", 8000))
        WORKERS = int(os.getenv("APP_WORKERS", 1))
        RELOAD = os.getenv("APP_RELOAD", "true").lower() == "true"
        
        @classmethod
        def get_uvicorn_config(cls) -> dict:
            """Get uvicorn server configuration."""
            return {
                "host": cls.HOST,
                "port": cls.PORT,
                "workers": cls.WORKERS,
                "reload": cls.RELOAD,
                "log_level": "info",
            }
    
    # File storage configuration
    class Storage:
        """Native file storage configuration."""
        
        PROVIDER = os.getenv("STORAGE_PROVIDER", "local")
        ROOT = Path(os.getenv("STORAGE_ROOT", str(NativeConfig.STORAGE_DIR)))
        MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 104857600))  # 100MB
        
        @classmethod
        def ensure_storage(cls):
            """Ensure storage directory exists."""
            cls.ROOT.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (cls.ROOT / "documents").mkdir(exist_ok=True)
            (cls.ROOT / "workspaces").mkdir(exist_ok=True)
            (cls.ROOT / "artifacts").mkdir(exist_ok=True)
            (cls.ROOT / "temp").mkdir(exist_ok=True)
    
    # Logging configuration
    class Logging:
        """Native logging configuration."""
        
        LEVEL = os.getenv("LOG_LEVEL", "INFO")
        FORMAT = os.getenv(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        FILE = os.getenv("LOG_FILE", str(NativeConfig.LOGS_DIR / "app.log"))
        
        @classmethod
        def get_config(cls) -> dict:
            """Get logging configuration."""
            return {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": cls.FORMAT,
                    },
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "default",
                        "level": cls.LEVEL,
                    },
                    "file": {
                        "class": "logging.FileHandler",
                        "formatter": "default",
                        "filename": cls.FILE,
                        "level": cls.LEVEL,
                    },
                },
                "root": {
                    "level": cls.LEVEL,
                    "handlers": ["console", "file"],
                },
            }
    
    # Health check configuration
    class HealthCheck:
        """Health check configuration."""
        
        INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))
        TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", 10))
        ENDPOINT = "/api/v1/health"
        
        @classmethod
        def get_config(cls) -> dict:
            """Get health check configuration."""
            return {
                "interval": cls.INTERVAL,
                "timeout": cls.TIMEOUT,
                "endpoint": cls.ENDPOINT,
            }


# Initialize on import
NativeConfig.ensure_directories()
NativeConfig.Storage.ensure_storage()
