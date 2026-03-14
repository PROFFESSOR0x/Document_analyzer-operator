"""Runtime settings management for dynamic configuration."""

import json
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application_setting import ApplicationSetting
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class RuntimeSettings:
    """Runtime settings manager for dynamic configuration.

    This class provides:
    - In-memory caching of settings
    - Automatic refresh on changes
    - Fallback to environment variables
    - Type conversion helpers
    """

    _instance: Optional["RuntimeSettings"] = None
    _initialized: bool = False

    def __new__(cls) -> "RuntimeSettings":
        """Singleton pattern for runtime settings."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize runtime settings."""
        if not self._initialized:
            self._cache: Dict[str, Any] = {}
            self._last_refresh: Optional[datetime] = None
            self._db_session: Optional[AsyncSession] = None
            self._initialized = True

    async def initialize(self, db: AsyncSession) -> None:
        """Initialize runtime settings from database.

        Args:
            db: Database session.
        """
        self._db_session = db
        await self.refresh()
        logger.info("Runtime settings initialized from database")

    async def refresh(self) -> None:
        """Refresh settings cache from database."""
        if self._db_session is None:
            logger.warning("Cannot refresh settings: database session not initialized")
            return

        from sqlalchemy import select

        result = await self._db_session.execute(
            select(ApplicationSetting)
        )
        settings = result.scalars().all()

        for setting in settings:
            key = setting.key
            value = setting.value

            if setting.is_secret and value:
                from app.services.settings_service import SettingsService
                service = SettingsService(self._db_session)
                try:
                    value = service.decrypt_value(value)
                except Exception as e:
                    logger.error(f"Failed to decrypt setting {key}: {e}")
                    continue

            self._cache[key] = self._convert_value(value, setting.value_type)

        self._last_refresh = datetime.now(timezone.utc)
        logger.info(f"Settings cache refreshed: {len(self._cache)} settings")

    def _convert_value(self, value: Optional[str], value_type: str) -> Any:
        """Convert string value to appropriate type.

        Args:
            value: String value.
            value_type: Expected type.

        Returns:
            Any: Converted value.
        """
        if value is None:
            return None

        try:
            if value_type == "boolean":
                return value.lower() in ("true", "1", "yes")
            elif value_type == "integer":
                return int(value)
            elif value_type == "float":
                return float(value)
            elif value_type == "json":
                return json.loads(value)
            else:
                return value
        except (ValueError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to convert value for {value_type}: {e}")
            return value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value.

        Args:
            key: Setting key.
            default: Default value if not found.

        Returns:
            Any: Setting value or default.
        """
        if key in self._cache:
            return self._cache[key]

        logger.debug(f"Setting '{key}' not found in cache, using default")
        return default

    def get_string(self, key: str, default: str = "") -> str:
        """Get a string setting.

        Args:
            key: Setting key.
            default: Default value.

        Returns:
            str: String value.
        """
        value = self.get(key, default)
        return str(value) if value is not None else default

    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer setting.

        Args:
            key: Setting key.
            default: Default value.

        Returns:
            int: Integer value.
        """
        value = self.get(key, default)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get a float setting.

        Args:
            key: Setting key.
            default: Default value.

        Returns:
            float: Float value.
        """
        value = self.get(key, default)
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean setting.

        Args:
            key: Setting key.
            default: Default value.

        Returns:
            bool: Boolean value.
        """
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        return bool(value) if value is not None else default

    def get_json(self, key: str, default: Optional[Dict] = None) -> Optional[Dict]:
        """Get a JSON setting.

        Args:
            key: Setting key.
            default: Default value.

        Returns:
            Optional[Dict]: JSON value as dict.
        """
        value = self.get(key, default)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return default
        return default

    @property
    def last_refresh(self) -> Optional[datetime]:
        """Get the last refresh timestamp.

        Returns:
            Optional[datetime]: Last refresh time.
        """
        return self._last_refresh

    def invalidate(self, key: Optional[str] = None) -> None:
        """Invalidate cache entry or entire cache.

        Args:
            key: Optional specific key to invalidate.
        """
        if key:
            self._cache.pop(key, None)
            logger.debug(f"Cache invalidated for: {key}")
        else:
            self._cache.clear()
            logger.info("Cache invalidated")


_runtime_settings: Optional[RuntimeSettings] = None


def get_runtime_settings() -> RuntimeSettings:
    """Get the runtime settings singleton.

    Returns:
        RuntimeSettings: Runtime settings instance.
    """
    global _runtime_settings
    if _runtime_settings is None:
        _runtime_settings = RuntimeSettings()
    return _runtime_settings


async def init_runtime_settings(db: AsyncSession) -> RuntimeSettings:
    """Initialize runtime settings from database.

    Args:
        db: Database session.

    Returns:
        RuntimeSettings: Initialized runtime settings.
    """
    global _runtime_settings
    _runtime_settings = RuntimeSettings()
    await _runtime_settings.initialize(db)
    return _runtime_settings
