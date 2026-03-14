"""Settings API routes for managing application configuration."""

import json
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import ActiveUser, get_current_active_user
from app.models.user import User
from app.models.application_setting import ApplicationSetting
from app.schemas.application_setting import (
    ApplicationSettingCreate,
    ApplicationSettingUpdate,
    ApplicationSettingResponse,
    ApplicationSettingList,
    SettingCategoryResponse,
    SettingAuditLogResponse,
    SettingAuditLogList,
    BulkSettingsUpdate,
    SettingsExport,
    SettingsImport,
)
from app.services.settings_service import (
    SettingsService,
    get_settings_service,
    SettingsValidationError,
    SettingsEncryptionError,
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


def require_admin(user: User) -> None:
    """Check if user has admin privileges.

    Args:
        user: Current user.

    Raises:
        HTTPException: If user is not an admin.
    """
    if user.role not in ("admin", "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )


@router.get("", response_model=ApplicationSettingList)
async def list_settings(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db),
    current_user: ActiveUser = Depends(get_current_active_user),
    settings_service: SettingsService = Depends(get_settings_service),
) -> ApplicationSettingList:
    """List all application settings.

    Args:
        category: Optional category filter.
        db: Database session.
        current_user: Current authenticated user.
        settings_service: Settings service.

    Returns:
        ApplicationSettingList: List of settings.

    Raises:
        HTTPException: If user lacks permissions.
    """
    require_admin(current_user)

    if category:
        settings = await settings_service.get_settings_by_category(category)
    else:
        settings = await settings_service.get_all_settings()

    return ApplicationSettingList(
        settings=[
            ApplicationSettingResponse(
                id=s.id,
                key=s.key,
                value=s.value,
                value_type=s.value_type,
                category=s.category,
                description=s.description,
                is_secret=s.is_secret,
                is_editable=s.is_editable,
                validation_schema=s.validation_schema,
                default_value=s.default_value,
                updated_at=s.updated_at,
                updated_by={"id": s.updated_by_id} if s.updated_by_id else None,
            )
            for s in settings
        ],
        total=len(settings),
    )


@router.get("/categories", response_model=List[SettingCategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: ActiveUser = Depends(get_current_active_user),
    settings_service: SettingsService = Depends(get_settings_service),
) -> List[SettingCategoryResponse]:
    """List all setting categories.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        settings_service: Settings service.

    Returns:
        List[SettingCategoryResponse]: List of categories.
    """
    require_admin(current_user)

    categories = await settings_service.get_categories()

    return [
        SettingCategoryResponse(
            id=c["id"],
            name=c["name"],
            description=c["description"],
            icon=c["icon"],
            setting_count=c["setting_count"],
        )
        for c in categories
    ]


@router.get("/category/{category}", response_model=ApplicationSettingList)
async def get_settings_by_category(
    category: str,
    db: AsyncSession = Depends(get_db),
    current_user: ActiveUser = Depends(get_current_active_user),
    settings_service: SettingsService = Depends(get_settings_service),
) -> ApplicationSettingList:
    """Get all settings in a category.

    Args:
        category: Category name.
        db: Database session.
        current_user: Current authenticated user.
        settings_service: Settings service.

    Returns:
        ApplicationSettingList: List of settings in category.
    """
    require_admin(current_user)

    settings = await settings_service.get_settings_by_category(category)

    return ApplicationSettingList(
        settings=[
            ApplicationSettingResponse(
                id=s.id,
                key=s.key,
                value=s.value,
                value_type=s.value_type,
                category=s.category,
                description=s.description,
                is_secret=s.is_secret,
                is_editable=s.is_editable,
                validation_schema=s.validation_schema,
                default_value=s.default_value,
                updated_at=s.updated_at,
                updated_by={"id": s.updated_by_id} if s.updated_by_id else None,
            )
            for s in settings
        ],
        total=len(settings),
    )


@router.get("/{key}", response_model=ApplicationSettingResponse)
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: ActiveUser = Depends(get_current_active_user),
    settings_service: SettingsService = Depends(get_settings_service),
) -> ApplicationSettingResponse:
    """Get a specific setting by key.

    Args:
        key: Setting key.
        db: Database session.
        current_user: Current authenticated user.
        settings_service: Settings service.

    Returns:
        ApplicationSettingResponse: Setting details.

    Raises:
        HTTPException: If setting not found.
    """
    require_admin(current_user)

    setting = await settings_service.get_setting(key)

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found",
        )

    return ApplicationSettingResponse(
        id=setting.id,
        key=setting.key,
        value=setting.value,
        value_type=setting.value_type,
        category=setting.category,
        description=setting.description,
        is_secret=setting.is_secret,
        is_editable=setting.is_editable,
        validation_schema=setting.validation_schema,
        default_value=setting.default_value,
        updated_at=setting.updated_at,
        updated_by={"id": setting.updated_by_id} if setting.updated_by_id else None,
    )


@router.put("/{key}", response_model=ApplicationSettingResponse)
async def update_setting(
    key: str,
    update_data: ApplicationSettingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: ActiveUser = Depends(get_current_active_user),
    settings_service: SettingsService = Depends(get_settings_service),
) -> ApplicationSettingResponse:
    """Update a setting.

    Args:
        key: Setting key.
        update_data: Update data.
        db: Database session.
        current_user: Current authenticated user.
        settings_service: Settings service.

    Returns:
        ApplicationSettingResponse: Updated setting.

    Raises:
        HTTPException: If setting not found or validation fails.
    """
    require_admin(current_user)

    try:
        setting = await settings_service.update_setting(
            key=key,
            value=update_data.value,
            user_id=current_user.id,
            reason=update_data.change_reason,
        )

        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting '{key}' not found",
            )

        return ApplicationSettingResponse(
            id=setting.id,
            key=setting.key,
            value=setting.value,
            value_type=setting.value_type,
            category=setting.category,
            description=setting.description,
            is_secret=setting.is_secret,
            is_editable=setting.is_editable,
            validation_schema=setting.validation_schema,
            default_value=setting.default_value,
            updated_at=setting.updated_at,
            updated_by={"id": setting.updated_by_id} if setting.updated_by_id else None,
        )

    except SettingsValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except SettingsEncryptionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encryption error: {e}",
        )


@router.put("/bulk", response_model=Dict[str, bool])
async def bulk_update_settings(
    update_data: BulkSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: ActiveUser = Depends(get_current_active_user),
    settings_service: SettingsService = Depends(get_settings_service),
) -> Dict[str, bool]:
    """Bulk update multiple settings.

    Args:
        update_data: Bulk update data.
        db: Database session.
        current_user: Current authenticated user.
        settings_service: Settings service.

    Returns:
        Dict[str, bool]: Update results per setting.
    """
    require_admin(current_user)

    return await settings_service.bulk_update_settings(
        settings_dict=update_data.settings,
        user_id=current_user.id,
        reason=update_data.change_reason,
    )


@router.post("/{key}/reset", response_model=ApplicationSettingResponse)
async def reset_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: ActiveUser = Depends(get_current_active_user),
    settings_service: SettingsService = Depends(get_settings_service),
) -> ApplicationSettingResponse:
    """Reset a setting to its default value.

    Args:
        key: Setting key.
        db: Database session.
        current_user: Current authenticated user.
        settings_service: Settings service.

    Returns:
        ApplicationSettingResponse: Reset setting.

    Raises:
        HTTPException: If setting not found or has no default.
    """
    require_admin(current_user)

    setting = await settings_service.reset_setting_to_default(key)

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found or has no default value",
        )

    return ApplicationSettingResponse(
        id=setting.id,
        key=setting.key,
        value=setting.value,
        value_type=setting.value_type,
        category=setting.category,
        description=setting.description,
        is_secret=setting.is_secret,
        is_editable=setting.is_editable,
        validation_schema=setting.validation_schema,
        default_value=setting.default_value,
        updated_at=setting.updated_at,
        updated_by={"id": setting.updated_by_id} if setting.updated_by_id else None,
    )


@router.get("/{key}/audit", response_model=SettingAuditLogList)
async def get_setting_audit_log(
    key: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum entries to return"),
    db: AsyncSession = Depends(get_db),
    current_user: ActiveUser = Depends(get_current_active_user),
    settings_service: SettingsService = Depends(get_settings_service),
) -> SettingAuditLogList:
    """Get audit log for a setting.

    Args:
        key: Setting key.
        limit: Maximum entries.
        db: Database session.
        current_user: Current authenticated user.
        settings_service: Settings service.

    Returns:
        SettingAuditLogList: Audit log entries.

    Raises:
        HTTPException: If setting not found.
    """
    require_admin(current_user)

    setting = await settings_service.get_setting(key)

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found",
        )

    logs = await settings_service.get_audit_log(setting.id, limit)

    return SettingAuditLogList(
        logs=[
            SettingAuditLogResponse(
                id=log.id,
                setting_id=log.setting_id,
                setting_key=key,
                old_value=log.old_value,
                new_value=log.new_value,
                changed_by={"id": log.changed_by_id} if log.changed_by_id else None,
                change_reason=log.change_reason,
                created_at=log.created_at,
            )
            for log in logs
        ],
        total=len(logs),
    )


@router.post("/export", response_model=SettingsExport)
async def export_settings(
    db: AsyncSession = Depends(get_db),
    current_user: ActiveUser = Depends(get_current_active_user),
    settings_service: SettingsService = Depends(get_settings_service),
) -> SettingsExport:
    """Export all settings as JSON.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        settings_service: Settings service.

    Returns:
        SettingsExport: Exported settings data.
    """
    require_admin(current_user)

    export_data = await settings_service.export_settings(current_user.id)

    return SettingsExport(**export_data)


@router.post("/import", response_model=Dict[str, bool])
async def import_settings(
    file: UploadFile = File(..., description="JSON file with settings"),
    overwrite: bool = Query(False, description="Overwrite existing settings"),
    db: AsyncSession = Depends(get_db),
    current_user: ActiveUser = Depends(get_current_active_user),
    settings_service: SettingsService = Depends(get_settings_service),
) -> Dict[str, bool]:
    """Import settings from a JSON file.

    Args:
        file: JSON file with settings.
        overwrite: Whether to overwrite existing.
        db: Database session.
        current_user: Current authenticated user.
        settings_service: Settings service.

    Returns:
        Dict[str, bool]: Import results per setting.

    Raises:
        HTTPException: If file is invalid.
    """
    require_admin(current_user)

    try:
        content = await file.read()
        settings_data = json.loads(content.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON file: {e}",
        )

    return await settings_service.import_settings(
        settings_data=settings_data,
        user_id=current_user.id,
        overwrite_existing=overwrite,
    )


@router.get("/schema/{category}")
async def get_validation_schema(
    category: str,
    db: AsyncSession = Depends(get_db),
    current_user: ActiveUser = Depends(get_current_active_user),
    settings_service: SettingsService = Depends(get_settings_service),
) -> Dict[str, Any]:
    """Get validation schemas for a category.

    Args:
        category: Category name.
        db: Database session.
        current_user: Current authenticated user.
        settings_service: Settings service.

    Returns:
        Dict[str, Any]: Validation schemas.
    """
    require_admin(current_user)

    settings = await settings_service.get_settings_by_category(category)

    schemas = {}
    for setting in settings:
        if setting.validation_schema:
            schemas[setting.key] = setting.validation_schema

    return schemas
