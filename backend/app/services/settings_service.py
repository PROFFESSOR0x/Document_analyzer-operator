"""Settings service for managing application configuration."""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from cryptography.fernet import Fernet, InvalidToken

from app.models.application_setting import ApplicationSetting
from app.models.setting_audit_log import SettingAuditLog
from app.models.user import User
from app.schemas.application_setting import (
    ApplicationSettingCreate,
    ApplicationSettingUpdate,
    BulkSettingsUpdate,
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class SettingsEncryptionError(Exception):
    """Exception raised for encryption/decryption errors."""

    pass


class SettingsValidationError(Exception):
    """Exception raised for validation errors."""

    pass


class SettingsService:
    """Service for managing application settings with encryption and audit logging."""

    DEFAULT_CATEGORIES = [
        "llm",
        "database",
        "redis",
        "security",
        "application",
        "ui",
    ]

    def __init__(self, db: AsyncSession) -> None:
        """Initialize settings service.

        Args:
            db: Database session.
        """
        self.db = db
        self._fernet: Optional[Fernet] = None

    def _get_encryption_key(self) -> bytes:
        """Get encryption key from environment.

        Returns:
            bytes: Encryption key.

        Raises:
            SettingsEncryptionError: If encryption key is not configured.
        """
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise SettingsEncryptionError(
                "ENCRYPTION_KEY environment variable is not set. "
                "Generate one with: cryptography.fernet.Fernet.generate_key()"
            )
        return key.encode() if isinstance(key, str) else key

    @property
    def fernet(self) -> Fernet:
        """Get Fernet encryption instance.

        Returns:
            Fernet: Fernet encryption instance.

        Raises:
            SettingsEncryptionError: If encryption key is invalid.
        """
        if self._fernet is None:
            try:
                key = self._get_encryption_key()
                self._fernet = Fernet(key)
            except Exception as e:
                raise SettingsEncryptionError(f"Failed to initialize encryption: {e}") from e
        return self._fernet

    def encrypt_value(self, value: str) -> str:
        """Encrypt a secret value using Fernet encryption.

        Args:
            value: Plain text value.

        Returns:
            str: Encrypted value.

        Raises:
            SettingsEncryptionError: If encryption fails.
        """
        try:
            return self.fernet.encrypt(value.encode()).decode()
        except Exception as e:
            raise SettingsEncryptionError(f"Failed to encrypt value: {e}") from e

    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a secret value using Fernet encryption.

        Args:
            encrypted_value: Encrypted value.

        Returns:
            str: Decrypted value.

        Raises:
            SettingsEncryptionError: If decryption fails.
        """
        try:
            return self.fernet.decrypt(encrypted_value.encode()).decode()
        except InvalidToken:
            raise SettingsEncryptionError("Invalid encryption key or corrupted data") from None
        except Exception as e:
            raise SettingsEncryptionError(f"Failed to decrypt value: {e}") from e

    def validate_setting(self, key: str, value: Any) -> bool:
        """Validate a setting value against its schema.

        Args:
            key: Setting key.
            value: Value to validate.

        Returns:
            bool: True if valid.

        Raises:
            SettingsValidationError: If validation fails.
        """
        setting = self.get_setting_sync(key)
        if not setting:
            raise SettingsValidationError(f"Setting '{key}' not found")

        if setting.validation_schema:
            try:
                from pydantic import create_model

                schema = setting.validation_schema
                field_type = schema.get("type", "string")

                type_map = {
                    "string": str,
                    "integer": int,
                    "number": float,
                    "boolean": bool,
                    "object": dict,
                    "array": list,
                }

                pydantic_type = type_map.get(field_type, str)
                validators = {}

                if "minimum" in schema:
                    validators["min_value"] = lambda v: v >= schema["minimum"]
                if "maximum" in schema:
                    validators["max_value"] = lambda v: v <= schema["maximum"]
                if "min_length" in schema and isinstance(value, str):
                    validators["min_len"] = lambda v: len(v) >= schema["min_length"]
                if "max_length" in schema and isinstance(value, str):
                    validators["max_len"] = lambda v: len(v) <= schema["max_length"]
                if "pattern" in schema and isinstance(value, str):
                    import re
                    validators["pattern"] = lambda v: bool(re.match(schema["pattern"], v))
                if "enum" in schema:
                    validators["enum"] = lambda v: v in schema["enum"]

                model = create_model("DynamicValidator", value=(pydantic_type, ...))
                model.model_validate({"value": value})

                for validator_func in validators.values():
                    if not validator_func(value):
                        raise SettingsValidationError(
                            f"Value '{value}' does not meet validation criteria for '{key}'"
                        )

            except SettingsValidationError:
                raise
            except Exception as e:
                raise SettingsValidationError(f"Validation failed for '{key}': {e}") from e

        if setting.value_type == "boolean":
            if value.lower() not in ("true", "false", "1", "0", "yes", "no"):
                raise SettingsValidationError(
                    f"Boolean value must be 'true', 'false', '1', '0', 'yes', or 'no', got '{value}'"
                )
        elif setting.value_type == "integer":
            try:
                int(value)
            except ValueError:
                raise SettingsValidationError(f"Integer value expected for '{key}', got '{value}'")
        elif setting.value_type == "float":
            try:
                float(value)
            except ValueError:
                raise SettingsValidationError(f"Float value expected for '{key}', got '{value}'")
        elif setting.value_type == "json":
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise SettingsValidationError(f"Invalid JSON for '{key}': {value}")

        return True

    def get_setting_sync(self, key: str) -> Optional[ApplicationSetting]:
        """Synchronously get a setting (for validation).

        Args:
            key: Setting key.

        Returns:
            Optional[ApplicationSetting]: Setting if found.
        """
        from sqlalchemy.orm import Session
        from app.db.session import engine

        with Session(engine.sync_engine) as session:
            return session.query(ApplicationSetting).filter(
                ApplicationSetting.key == key
            ).first()

    async def get_setting(self, key: str, decrypt_secrets: bool = False) -> Optional[ApplicationSetting]:
        """Get a single setting by key.

        Args:
            key: Setting key.
            decrypt_secrets: Whether to decrypt secret values.

        Returns:
            Optional[ApplicationSetting]: Setting if found.
        """
        result = await self.db.execute(
            select(ApplicationSetting).where(ApplicationSetting.key == key)
        )
        setting = result.scalar_one_or_none()

        if setting and setting.is_secret and setting.value and decrypt_secrets:
            try:
                setting.value = self.decrypt_value(setting.value)
            except SettingsEncryptionError:
                logger.warning(f"Failed to decrypt secret setting: {key}")

        return setting

    async def get_settings_by_category(self, category: str) -> List[ApplicationSetting]:
        """Get all settings in a category.

        Args:
            category: Category name.

        Returns:
            List[ApplicationSetting]: List of settings.
        """
        result = await self.db.execute(
            select(ApplicationSetting)
            .where(ApplicationSetting.category == category)
            .order_by(ApplicationSetting.key)
        )
        return list(result.scalars().all())

    async def get_all_settings(self, decrypt_secrets: bool = False) -> List[ApplicationSetting]:
        """Get all settings.

        Args:
            decrypt_secrets: Whether to decrypt secret values.

        Returns:
            List[ApplicationSetting]: List of all settings.
        """
        result = await self.db.execute(
            select(ApplicationSetting).order_by(
                ApplicationSetting.category,
                ApplicationSetting.key,
            )
        )
        settings = list(result.scalars().all())

        if decrypt_secrets:
            for setting in settings:
                if setting.is_secret and setting.value:
                    try:
                        setting.value = self.decrypt_value(setting.value)
                    except SettingsEncryptionError:
                        logger.warning(f"Failed to decrypt secret setting: {setting.key}")

        return settings

    async def update_setting(
        self,
        key: str,
        value: Any,
        user_id: str,
        reason: Optional[str] = None,
    ) -> Optional[ApplicationSetting]:
        """Update a setting with audit logging.

        Args:
            key: Setting key.
            value: New value.
            user_id: User ID making the change.
            reason: Optional reason for the change.

        Returns:
            Optional[ApplicationSetting]: Updated setting if found.

        Raises:
            SettingsValidationError: If validation fails.
            SettingsEncryptionError: If encryption fails.
        """
        setting = await self.get_setting(key)
        if not setting:
            return None

        if not setting.is_editable:
            raise SettingsValidationError(f"Setting '{key}' is not editable")

        value_str = str(value)

        self.validate_setting(key, value_str)

        old_value = setting.value

        if setting.is_secret and value_str:
            setting.value = self.encrypt_value(value_str)
        else:
            setting.value = value_str

        setting.updated_by_id = user_id

        self.db.add(setting)

        if old_value != setting.value:
            audit_log = SettingAuditLog(
                id=str(uuid4()),
                setting_id=setting.id,
                old_value=old_value,
                new_value=setting.value,
                changed_by_id=user_id,
                change_reason=reason,
            )
            self.db.add(audit_log)

        await self.db.flush()
        await self.db.refresh(setting)

        logger.info(f"Setting updated: {key} by user {user_id}")

        return setting

    async def bulk_update_settings(
        self,
        settings_dict: Dict[str, Any],
        user_id: str,
        reason: Optional[str] = None,
    ) -> Dict[str, bool]:
        """Bulk update multiple settings.

        Args:
            settings_dict: Dictionary of setting key to value.
            user_id: User ID making the changes.
            reason: Optional reason for the changes.

        Returns:
            Dict[str, bool]: Dictionary of setting key to success status.
        """
        results: Dict[str, bool] = {}

        for key, value in settings_dict.items():
            try:
                await self.update_setting(key, value, user_id, reason)
                results[key] = True
            except Exception as e:
                logger.error(f"Failed to update setting {key}: {e}")
                results[key] = False

        return results

    async def reset_setting_to_default(self, key: str) -> Optional[ApplicationSetting]:
        """Reset a setting to its default value.

        Args:
            key: Setting key.

        Returns:
            Optional[ApplicationSetting]: Reset setting if found.
        """
        setting = await self.get_setting(key)
        if not setting or not setting.default_value:
            return None

        old_value = setting.value

        if setting.is_secret:
            setting.value = self.encrypt_value(setting.default_value)
        else:
            setting.value = setting.default_value

        self.db.add(setting)

        if old_value != setting.value:
            audit_log = SettingAuditLog(
                id=str(uuid4()),
                setting_id=setting.id,
                old_value=old_value,
                new_value=setting.value,
                change_reason="Reset to default",
            )
            self.db.add(audit_log)

        await self.db.flush()
        await self.db.refresh(setting)

        logger.info(f"Setting reset to default: {key}")

        return setting

    async def get_audit_log(
        self,
        setting_id: str,
        limit: int = 50,
    ) -> List[SettingAuditLog]:
        """Get audit log for a setting.

        Args:
            setting_id: Setting ID.
            limit: Maximum number of entries.

        Returns:
            List[SettingAuditLog]: List of audit log entries.
        """
        result = await self.db.execute(
            select(SettingAuditLog)
            .where(SettingAuditLog.setting_id == setting_id)
            .order_by(SettingAuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_all_audit_logs(
        self,
        limit: int = 100,
        setting_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[SettingAuditLog]:
        """Get all audit logs with optional filters.

        Args:
            limit: Maximum number of entries.
            setting_id: Optional setting ID filter.
            user_id: Optional user ID filter.

        Returns:
            List[SettingAuditLog]: List of audit log entries.
        """
        query = select(SettingAuditLog).order_by(SettingAuditLog.created_at.desc()).limit(limit)

        if setting_id:
            query = query.where(SettingAuditLog.setting_id == setting_id)
        if user_id:
            query = query.where(SettingAuditLog.changed_by_id == user_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def export_settings(self, user_id: str) -> Dict[str, Any]:
        """Export all settings as JSON.

        Args:
            user_id: User ID exporting the settings.

        Returns:
            Dict[str, Any]: Exported settings data.
        """
        settings = await self.get_all_settings()

        settings_data = []
        for setting in settings:
            setting_data = {
                "key": setting.key,
                "value": setting.default_value if setting.is_secret else setting.value,
                "value_type": setting.value_type,
                "category": setting.category,
                "description": setting.description,
                "is_secret": setting.is_secret,
                "is_editable": setting.is_editable,
                "validation_schema": setting.validation_schema,
                "default_value": setting.default_value,
            }
            settings_data.append(setting_data)

        return {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "exported_by": user_id,
            "settings": settings_data,
            "total": len(settings_data),
        }

    async def import_settings(
        self,
        settings_data: Dict[str, Any],
        user_id: str,
        overwrite_existing: bool = False,
    ) -> Dict[str, bool]:
        """Import settings from JSON.

        Args:
            settings_data: Settings data to import.
            user_id: User ID importing the settings.
            overwrite_existing: Whether to overwrite existing settings.

        Returns:
            Dict[str, bool]: Dictionary of setting key to success status.
        """
        results: Dict[str, bool] = {}
        settings_list = settings_data.get("settings", [])

        for setting_data in settings_list:
            key = setting_data.get("key")
            if not key:
                continue

            try:
                existing = await self.get_setting(key)

                if existing and not overwrite_existing:
                    results[key] = False
                    continue

                if existing:
                    await self.update_setting(
                        key,
                        setting_data.get("value", setting_data.get("default_value")),
                        user_id,
                        reason="Imported from backup",
                    )
                else:
                    new_setting = ApplicationSetting(
                        id=str(uuid4()),
                        key=key,
                        value=setting_data.get("value") or setting_data.get("default_value"),
                        value_type=setting_data.get("value_type", "string"),
                        category=setting_data.get("category", "general"),
                        description=setting_data.get("description"),
                        is_secret=setting_data.get("is_secret", False),
                        is_editable=setting_data.get("is_editable", True),
                        validation_schema=setting_data.get("validation_schema"),
                        default_value=setting_data.get("default_value"),
                        updated_by_id=user_id,
                    )

                    if new_setting.is_secret and new_setting.value:
                        new_setting.value = self.encrypt_value(new_setting.value)

                    self.db.add(new_setting)
                    await self.db.flush()

                results[key] = True

            except Exception as e:
                logger.error(f"Failed to import setting {key}: {e}")
                results[key] = False

        return results

    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get all setting categories with counts.

        Returns:
            List[Dict[str, Any]]: List of categories with metadata.
        """
        result = await self.db.execute(
            select(
                ApplicationSetting.category,
                func.count(ApplicationSetting.id).label("count"),
            )
            .group_by(ApplicationSetting.category)
            .order_by(ApplicationSetting.category)
        )

        categories = []
        category_icons = {
            "llm": "cpu",
            "database": "database",
            "redis": "server",
            "security": "shield",
            "application": "settings",
            "ui": "monitor",
        }

        for row in result.all():
            categories.append({
                "id": row.category,
                "name": row.category.title(),
                "description": f"{row.category.title()} settings",
                "icon": category_icons.get(row.category, "settings"),
                "setting_count": row.count,
            })

        return categories


def get_settings_service(db: AsyncSession) -> SettingsService:
    """Get settings service instance.

    Args:
        db: Database session.

    Returns:
        SettingsService: Service instance.
    """
    return SettingsService(db)
