"""Application setting schemas for request/response validation."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SettingValueTypeSchema(str):
    """Schema for setting value type enumeration."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    SECRET = "secret"


class ApplicationSettingBase(BaseModel):
    """Base application setting schema with common fields."""

    key: str = Field(..., min_length=1, max_length=255, description="Setting key name")
    value: Optional[str] = Field(default=None, description="Setting value")
    value_type: str = Field(
        default="string",
        description="Type of value (string, integer, float, boolean, json, secret)",
    )
    category: str = Field(..., min_length=1, max_length=100, description="Category grouping")
    description: Optional[str] = Field(default=None, description="Human-readable description")
    is_secret: bool = Field(default=False, description="Whether value should be encrypted")
    is_editable: bool = Field(default=True, description="Whether UI can modify it")
    validation_schema: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Pydantic schema for validation",
    )
    default_value: Optional[str] = Field(default=None, description="Default value")


class ApplicationSettingCreate(ApplicationSettingBase):
    """Schema for creating a new application setting."""

    pass


class ApplicationSettingUpdate(BaseModel):
    """Schema for updating an application setting."""

    value: Optional[str] = Field(default=None, description="Setting value")
    is_editable: Optional[bool] = Field(default=None, description="Whether UI can modify it")
    validation_schema: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Pydantic schema for validation",
    )
    change_reason: Optional[str] = Field(
        default=None,
        description="Reason for the change",
    )


class ApplicationSettingResponse(ApplicationSettingBase):
    """Schema for application setting response data."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Setting ID")
    updated_at: datetime = Field(..., description="Last update timestamp")
    updated_by: Optional[Dict[str, Any]] = Field(
        default=None,
        description="User who last updated",
    )

    @field_validator("value")
    @classmethod
    def mask_secret_value(cls, v: Optional[str]) -> Optional[str]:
        """Mask secret values for security."""
        if v and len(v) > 8:
            return f"{v[:4]}••••••{v[-4:]}"
        return "••••••••" if v else None


class ApplicationSettingList(BaseModel):
    """Schema for application setting list response."""

    settings: List[ApplicationSettingResponse]
    total: int = Field(..., description="Total number of settings")


class SettingCategoryResponse(BaseModel):
    """Schema for setting category response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(default=None, description="Category description")
    icon: str = Field(default="settings", description="Category icon name")
    setting_count: int = Field(..., description="Number of settings in category")
    settings: List[ApplicationSettingResponse] = Field(
        default_factory=list,
        description="Settings in this category",
    )


class SettingAuditLogResponse(BaseModel):
    """Schema for setting audit log response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Audit log ID")
    setting_id: str = Field(..., description="Setting ID")
    setting_key: str = Field(..., description="Setting key")
    old_value: Optional[str] = Field(default=None, description="Previous value")
    new_value: Optional[str] = Field(default=None, description="New value")
    changed_by: Optional[Dict[str, Any]] = Field(
        default=None,
        description="User who made the change",
    )
    change_reason: Optional[str] = Field(default=None, description="Reason for change")
    created_at: datetime = Field(..., description="Change timestamp")

    @field_validator("old_value", "new_value")
    @classmethod
    def mask_secret_values(cls, v: Optional[str]) -> Optional[str]:
        """Mask secret values for security."""
        if v and len(v) > 8:
            return f"{v[:4]}••••••{v[-4:]}"
        return "••••••••" if v else None


class SettingAuditLogList(BaseModel):
    """Schema for setting audit log list response."""

    logs: List[SettingAuditLogResponse]
    total: int = Field(..., description="Total number of logs")


class BulkSettingsUpdate(BaseModel):
    """Schema for bulk updating settings."""

    settings: Dict[str, str] = Field(
        ...,
        description="Dictionary of setting key to value",
    )
    change_reason: Optional[str] = Field(
        default=None,
        description="Reason for bulk change",
    )


class SettingsExport(BaseModel):
    """Schema for exported settings."""

    exported_at: datetime = Field(..., description="Export timestamp")
    exported_by: str = Field(..., description="User ID who exported")
    settings: List[ApplicationSettingResponse]
    total: int = Field(..., description="Total number of settings")


class SettingsImport(BaseModel):
    """Schema for importing settings."""

    settings: List[ApplicationSettingCreate]
    overwrite_existing: bool = Field(
        default=False,
        description="Whether to overwrite existing settings",
    )
