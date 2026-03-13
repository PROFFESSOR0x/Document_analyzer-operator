"""LLM Provider API routes."""

import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ActiveUser, SuperUser
from app.db.session import get_db
from app.models.llm_provider import LLMProvider
from app.models.user import User
from app.schemas.llm_provider import (
    LLMProviderCreate,
    LLMProviderList,
    LLMProviderResponse,
    LLMProviderUpdate,
    LLMTestRequest,
    LLMTestResponse,
    LLMUsageLogList,
    LLMUsageLogResponse,
    LLMUsageStats,
    LLMUsageStatsRequest,
)
from app.services.llm_provider_service import (
    LLMProviderService,
    get_llm_provider_service,
    EncryptionError,
)
from app.services.llm_client import (
    LLMClient,
    create_llm_client,
    LLMError,
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    ProviderError,
)

router = APIRouter()


def get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> LLMProviderService:
    """Get LLM provider service instance."""
    return get_llm_provider_service(db)


@router.get("", response_model=LLMProviderList)
async def list_providers(
    current_user: ActiveUser,
    service: Annotated[LLMProviderService, Depends(get_service)],
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    active_only: bool = Query(False, description="Filter to active providers only"),
    provider_type: Optional[str] = Query(None, description="Filter by provider type"),
) -> LLMProviderList:
    """List all LLM providers.

    Args:
        current_user: Current authenticated user.
        service: LLM provider service.
        skip: Number of records to skip.
        limit: Maximum number of records.
        active_only: Filter to active providers only.
        provider_type: Filter by provider type.

    Returns:
        LLMProviderList: List of providers.
    """
    providers = await service.list_providers(
        skip=skip,
        limit=limit,
        active_only=active_only,
        provider_type=provider_type,
    )

    return LLMProviderList(
        providers=[LLMProviderResponse.model_validate(p) for p in providers],
        total=len(providers),
    )


@router.get("/{provider_id}", response_model=LLMProviderResponse)
async def get_provider(
    provider_id: str,
    current_user: ActiveUser,
    service: Annotated[LLMProviderService, Depends(get_service)],
) -> LLMProviderResponse:
    """Get LLM provider by ID.

    Args:
        provider_id: Provider ID.
        current_user: Current authenticated user.
        service: LLM provider service.

    Returns:
        LLMProviderResponse: Provider details.

    Raises:
        HTTPException: If provider not found.
    """
    provider = await service.get_provider(provider_id)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )

    return LLMProviderResponse.model_validate(provider)


@router.post("", response_model=LLMProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    provider_data: LLMProviderCreate,
    current_user: ActiveUser,
    service: Annotated[LLMProviderService, Depends(get_service)],
) -> LLMProviderResponse:
    """Create a new LLM provider.

    Args:
        provider_data: Provider creation data.
        current_user: Current authenticated user.
        service: LLM provider service.

    Returns:
        LLMProviderResponse: Created provider.

    Raises:
        HTTPException: If creation fails.
    """
    try:
        provider = await service.create_provider(
            provider_data=provider_data,
            current_user=current_user,
        )
        return LLMProviderResponse.model_validate(provider)
    except EncryptionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encryption error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put("/{provider_id}", response_model=LLMProviderResponse)
async def update_provider(
    provider_id: str,
    provider_data: LLMProviderUpdate,
    current_user: ActiveUser,
    service: Annotated[LLMProviderService, Depends(get_service)],
) -> LLMProviderResponse:
    """Update an LLM provider.

    Args:
        provider_id: Provider ID.
        provider_data: Provider update data.
        current_user: Current authenticated user.
        service: LLM provider service.

    Returns:
        LLMProviderResponse: Updated provider.

    Raises:
        HTTPException: If provider not found or update fails.
    """
    try:
        provider = await service.update_provider(
            provider_id=provider_id,
            provider_data=provider_data,
            current_user=current_user,
        )

        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found",
            )

        return LLMProviderResponse.model_validate(provider)
    except EncryptionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encryption error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_id: str,
    current_user: ActiveUser,
    service: Annotated[LLMProviderService, Depends(get_service)],
) -> None:
    """Delete an LLM provider.

    Args:
        provider_id: Provider ID.
        current_user: Current authenticated user.
        service: LLM provider service.

    Raises:
        HTTPException: If provider not found.
    """
    deleted = await service.delete_provider(
        provider_id=provider_id,
        current_user=current_user,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )


@router.post("/{provider_id}/test", response_model=LLMTestResponse)
async def test_provider(
    provider_id: str,
    test_request: LLMTestRequest,
    current_user: ActiveUser,
    service: Annotated[LLMProviderService, Depends(get_service)],
) -> LLMTestResponse:
    """Test LLM provider connection.

    Args:
        provider_id: Provider ID.
        test_request: Test request data.
        current_user: Current authenticated user.
        service: LLM provider service.

    Returns:
        LLMTestResponse: Test result.

    Raises:
        HTTPException: If provider not found or test fails.
    """
    provider = await service.get_provider(provider_id)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )

    # Decrypt API key if present
    api_key = None
    if provider.api_key:
        try:
            api_key = service.decrypt_api_key(provider.api_key)
        except EncryptionError:
            pass  # Test without API key

    # Create LLM client and test
    client = create_llm_client(timeout=30.0, max_retries=1)
    client.register_provider(provider, api_key=api_key)

    start_time = time.time()
    model_to_test = test_request.model_name or provider.model_name

    try:
        provider_instance = client.get_provider(provider_id)
        if not provider_instance:
            raise LLMError("Provider not registered")

        # Test with a simple completion
        await provider_instance.chat_completion(
            messages=[{"role": "user", "content": test_request.test_prompt}],
            model=model_to_test,
            max_tokens=10,
        )

        response_time_ms = int((time.time() - start_time) * 1000)

        return LLMTestResponse(
            success=True,
            message="Connection successful",
            model_tested=model_to_test,
            response_time_ms=response_time_ms,
        )

    except AuthenticationError as e:
        return LLMTestResponse(
            success=False,
            message="Authentication failed. Check API key.",
            model_tested=model_to_test,
            response_time_ms=int((time.time() - start_time) * 1000),
            error=str(e),
        )
    except RateLimitError as e:
        return LLMTestResponse(
            success=False,
            message="Rate limit exceeded. Try again later.",
            model_tested=model_to_test,
            response_time_ms=int((time.time() - start_time) * 1000),
            error=str(e),
        )
    except TimeoutError as e:
        return LLMTestResponse(
            success=False,
            message="Request timed out. Check connection.",
            model_tested=model_to_test,
            response_time_ms=int((time.time() - start_time) * 1000),
            error=str(e),
        )
    except ProviderError as e:
        return LLMTestResponse(
            success=False,
            message=f"Provider error: {str(e)}",
            model_tested=model_to_test,
            response_time_ms=int((time.time() - start_time) * 1000),
            error=str(e),
        )
    except LLMError as e:
        return LLMTestResponse(
            success=False,
            message=f"Test failed: {str(e)}",
            model_tested=model_to_test,
            response_time_ms=int((time.time() - start_time) * 1000),
            error=str(e),
        )
    except Exception as e:
        return LLMTestResponse(
            success=False,
            message=f"Unexpected error: {str(e)}",
            model_tested=model_to_test,
            response_time_ms=int((time.time() - start_time) * 1000),
            error=str(e),
        )


@router.post("/{provider_id}/set-default", response_model=LLMProviderResponse)
async def set_default_provider(
    provider_id: str,
    current_user: ActiveUser,
    service: Annotated[LLMProviderService, Depends(get_service)],
) -> LLMProviderResponse:
    """Set a provider as the default.

    Args:
        provider_id: Provider ID.
        current_user: Current authenticated user.
        service: LLM provider service.

    Returns:
        LLMProviderResponse: Updated provider.

    Raises:
        HTTPException: If provider not found.
    """
    provider = await service.set_default_provider(provider_id)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )

    return LLMProviderResponse.model_validate(provider)


@router.get("/usage/stats", response_model=LLMUsageStats)
async def get_usage_stats(
    current_user: ActiveUser,
    service: Annotated[LLMProviderService, Depends(get_service)],
    request: Annotated[LLMUsageStatsRequest, Depends()],
) -> LLMUsageStats:
    """Get LLM usage statistics.

    Args:
        current_user: Current authenticated user.
        service: LLM provider service.
        request: Statistics request with filters.

    Returns:
        LLMUsageStats: Usage statistics.
    """
    return await service.get_usage_stats(request)


@router.get("/usage/logs", response_model=LLMUsageLogList)
async def get_usage_logs(
    current_user: ActiveUser,
    service: Annotated[LLMProviderService, Depends(get_service)],
    provider_id: Optional[str] = Query(None, description="Filter by provider ID"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
) -> LLMUsageLogList:
    """Get detailed usage logs.

    Args:
        current_user: Current authenticated user.
        service: LLM provider service.
        provider_id: Filter by provider ID.
        agent_id: Filter by agent ID.
        start_date: Start date filter.
        end_date: End date filter.
        status: Status filter.
        skip: Number of records to skip.
        limit: Maximum number of records.

    Returns:
        LLMUsageLogList: List of usage logs.
    """
    logs = await service.get_usage_logs(
        provider_id=provider_id,
        user_id=current_user.id,
        agent_id=agent_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        skip=skip,
        limit=limit,
    )

    total = len(logs)

    return LLMUsageLogList(
        logs=[LLMUsageLogResponse.model_validate(log) for log in logs],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
    )
