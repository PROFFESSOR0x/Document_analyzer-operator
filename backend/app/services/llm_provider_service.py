"""LLM Provider service for managing AI model providers."""

import os
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import uuid4

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.llm_provider import LLMProvider
from app.models.llm_usage import LLMUsageLog
from app.models.user import User
from app.models.agent import Agent
from app.schemas.llm_provider import (
    LLMProviderCreate,
    LLMProviderUpdate,
    LLMUsageStats,
    LLMUsageStatsRequest,
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class EncryptionError(Exception):
    """Exception raised for encryption/decryption errors."""

    pass


class LLMProviderService:
    """Service for managing LLM providers and usage tracking."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize LLM provider service.

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
            EncryptionError: If encryption key is not configured.
        """
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise EncryptionError(
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
            EncryptionError: If encryption key is invalid.
        """
        if self._fernet is None:
            try:
                key = self._get_encryption_key()
                self._fernet = Fernet(key)
            except Exception as e:
                raise EncryptionError(f"Failed to initialize encryption: {e}") from e
        return self._fernet

    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key using Fernet encryption.

        Args:
            api_key: Plain text API key.

        Returns:
            str: Encrypted API key.

        Raises:
            EncryptionError: If encryption fails.
        """
        try:
            return self.fernet.encrypt(api_key.encode()).decode()
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt API key: {e}") from e

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key using Fernet encryption.

        Args:
            encrypted_key: Encrypted API key.

        Returns:
            str: Decrypted API key.

        Raises:
            EncryptionError: If decryption fails.
        """
        try:
            return self.fernet.decrypt(encrypted_key.encode()).decode()
        except InvalidToken:
            raise EncryptionError("Invalid encryption key or corrupted data") from None
        except Exception as e:
            raise EncryptionError(f"Failed to decrypt API key: {e}") from e

    async def create_provider(
        self,
        provider_data: LLMProviderCreate,
        current_user: User,
    ) -> LLMProvider:
        """Create a new LLM provider.

        Args:
            provider_data: Provider creation data.
            current_user: Current authenticated user.

        Returns:
            LLMProvider: Created provider.

        Raises:
            EncryptionError: If API key encryption fails.
        """
        # Encrypt API key if provided
        encrypted_key = None
        if provider_data.api_key:
            encrypted_key = self.encrypt_api_key(provider_data.api_key)

        # If this is set as default, unset other defaults
        if provider_data.is_default:
            await self._unset_all_defaults()

        provider = LLMProvider(
            id=str(uuid4()),
            name=provider_data.name,
            provider_type=provider_data.provider_type,
            base_url=provider_data.base_url,
            api_key=encrypted_key,
            model_name=provider_data.model_name,
            is_active=provider_data.is_active,
            is_default=provider_data.is_default,
            config=provider_data.config,
        )

        self.db.add(provider)
        await self.db.flush()
        await self.db.refresh(provider)

        logger.info(
            f"LLM provider created: {provider.name} ({provider.provider_type}) by user {current_user.id}"
        )

        return provider

    async def get_provider(self, provider_id: str) -> Optional[LLMProvider]:
        """Get LLM provider by ID.

        Args:
            provider_id: Provider ID.

        Returns:
            Optional[LLMProvider]: Provider if found.
        """
        result = await self.db.execute(
            select(LLMProvider).where(LLMProvider.id == provider_id)
        )
        return result.scalar_one_or_none()

    async def list_providers(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        provider_type: Optional[str] = None,
    ) -> List[LLMProvider]:
        """List all LLM providers.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records.
            active_only: Filter to active providers only.
            provider_type: Filter by provider type.

        Returns:
            List[LLMProvider]: List of providers.
        """
        query = select(LLMProvider)

        if active_only:
            query = query.where(LLMProvider.is_active == True)

        if provider_type:
            query = query.where(LLMProvider.provider_type == provider_type)

        query = query.order_by(LLMProvider.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_provider(
        self,
        provider_id: str,
        provider_data: LLMProviderUpdate,
        current_user: User,
    ) -> Optional[LLMProvider]:
        """Update an LLM provider.

        Args:
            provider_id: Provider ID.
            provider_data: Provider update data.
            current_user: Current authenticated user.

        Returns:
            Optional[LLMProvider]: Updated provider if found.

        Raises:
            EncryptionError: If API key encryption fails.
        """
        result = await self.db.execute(
            select(LLMProvider).where(LLMProvider.id == provider_id)
        )
        provider = result.scalar_one_or_none()

        if not provider:
            return None

        update_data = provider_data.model_dump(exclude_unset=True)

        # Encrypt API key if provided
        if "api_key" in update_data and update_data["api_key"]:
            update_data["api_key"] = self.encrypt_api_key(update_data["api_key"])

        # If setting as default, unset other defaults
        if update_data.get("is_default"):
            await self._unset_all_defaults(exclude_id=provider_id)

        for field, value in update_data.items():
            setattr(provider, field, value)

        self.db.add(provider)
        await self.db.flush()
        await self.db.refresh(provider)

        logger.info(
            f"LLM provider updated: {provider.name} ({provider.id}) by user {current_user.id}"
        )

        return provider

    async def delete_provider(
        self,
        provider_id: str,
        current_user: User,
    ) -> bool:
        """Delete an LLM provider.

        Args:
            provider_id: Provider ID.
            current_user: Current authenticated user.

        Returns:
            bool: True if deleted, False if not found.
        """
        result = await self.db.execute(
            select(LLMProvider).where(LLMProvider.id == provider_id)
        )
        provider = result.scalar_one_or_none()

        if not provider:
            return False

        # Cannot delete default provider
        if provider.is_default:
            # Find another provider to set as default
            other_result = await self.db.execute(
                select(LLMProvider)
                .where(LLMProvider.id != provider_id)
                .where(LLMProvider.is_active == True)
            )
            other_provider = other_result.scalar_one_or_none()
            if other_provider:
                other_provider.is_default = True
                self.db.add(other_provider)

        await self.db.delete(provider)

        logger.info(
            f"LLM provider deleted: {provider.name} ({provider.id}) by user {current_user.id}"
        )

        return True

    async def set_default_provider(self, provider_id: str) -> Optional[LLMProvider]:
        """Set a provider as the default.

        Args:
            provider_id: Provider ID.

        Returns:
            Optional[LLMProvider]: Updated provider if found.
        """
        await self._unset_all_defaults(exclude_id=provider_id)

        result = await self.db.execute(
            select(LLMProvider).where(LLMProvider.id == provider_id)
        )
        provider = result.scalar_one_or_none()

        if provider:
            provider.is_default = True
            self.db.add(provider)
            await self.db.flush()
            await self.db.refresh(provider)

        return provider

    async def get_default_provider(self) -> Optional[LLMProvider]:
        """Get the default LLM provider.

        Returns:
            Optional[LLMProvider]: Default provider if configured.
        """
        result = await self.db.execute(
            select(LLMProvider)
            .where(LLMProvider.is_default == True)
            .where(LLMProvider.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_active_provider(
        self, provider_id: str
    ) -> Optional[LLMProvider]:
        """Get an active provider by ID.

        Args:
            provider_id: Provider ID.

        Returns:
            Optional[LLMProvider]: Active provider if found.
        """
        result = await self.db.execute(
            select(LLMProvider).where(
                and_(
                    LLMProvider.id == provider_id,
                    LLMProvider.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def _unset_all_defaults(self, exclude_id: Optional[str] = None) -> None:
        """Unset default flag for all providers.

        Args:
            exclude_id: Optional provider ID to exclude.
        """
        query = select(LLMProvider).where(LLMProvider.is_default == True)
        if exclude_id:
            query = query.where(LLMProvider.id != exclude_id)

        result = await self.db.execute(query)
        providers = result.scalars().all()

        for provider in providers:
            provider.is_default = False
            self.db.add(provider)

        await self.db.flush()

    async def log_usage(
        self,
        provider_id: str,
        user_id: str,
        model_used: str,
        request_type: str,
        status: str,
        response_time_ms: int,
        agent_id: Optional[str] = None,
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost_usd: Optional[Decimal] = None,
        error_message: Optional[str] = None,
    ) -> LLMUsageLog:
        """Log LLM API usage.

        Args:
            provider_id: Provider ID.
            user_id: User ID.
            model_used: Model name used.
            request_type: Request type (completion, embedding, chat).
            status: Request status (success, failed).
            response_time_ms: Response time in milliseconds.
            agent_id: Optional agent ID.
            tokens_input: Input tokens count.
            tokens_output: Output tokens count.
            cost_usd: Cost in USD.
            error_message: Error message if failed.

        Returns:
            LLMUsageLog: Created usage log.
        """
        usage_log = LLMUsageLog(
            id=str(uuid4()),
            provider_id=provider_id,
            user_id=user_id,
            agent_id=agent_id,
            model_used=model_used,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost_usd=cost_usd,
            request_type=request_type,
            status=status,
            error_message=error_message,
            response_time_ms=response_time_ms,
            created_at=datetime.now(timezone.utc),
        )

        self.db.add(usage_log)
        await self.db.flush()
        await self.db.refresh(usage_log)

        return usage_log

    async def get_usage_stats(
        self,
        request: LLMUsageStatsRequest,
    ) -> LLMUsageStats:
        """Get LLM usage statistics.

        Args:
            request: Statistics request with filters.

        Returns:
            LLMUsageStats: Usage statistics.
        """
        # Build base query with filters
        base_query = select(LLMUsageLog)

        if request.start_date:
            base_query = base_query.where(LLMUsageLog.created_at >= request.start_date)
        if request.end_date:
            base_query = base_query.where(LLMUsageLog.created_at <= request.end_date)
        if request.provider_id:
            base_query = base_query.where(LLMUsageLog.provider_id == request.provider_id)
        if request.user_id:
            base_query = base_query.where(LLMUsageLog.user_id == request.user_id)
        if request.agent_id:
            base_query = base_query.where(LLMUsageLog.agent_id == request.agent_id)

        # Get total requests
        total_requests_query = select(func.count()).select_from(base_query.subquery())
        total_requests_result = await self.db.execute(total_requests_query)
        total_requests = total_requests_result.scalar() or 0

        # Get successful requests
        success_query = base_query.where(LLMUsageLog.status == "success")
        success_count_query = select(func.count()).select_from(success_query.subquery())
        success_count_result = await self.db.execute(success_count_query)
        success_count = success_count_result.scalar() or 0

        # Calculate success rate
        success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0.0

        # Get token totals
        tokens_query = select(
            func.sum(LLMUsageLog.tokens_input).label("input"),
            func.sum(LLMUsageLog.tokens_output).label("output"),
        ).select_from(base_query.subquery())
        tokens_result = await self.db.execute(tokens_query)
        tokens_row = tokens_result.first()
        total_tokens_input = tokens_row[0] or 0
        total_tokens_output = tokens_row[1] or 0

        # Get cost total
        cost_query = select(func.sum(LLMUsageLog.cost_usd)).select_from(
            base_query.subquery()
        )
        cost_result = await self.db.execute(cost_query)
        total_cost = cost_result.scalar() or Decimal("0.00")

        # Get average response time
        avg_time_query = select(func.avg(LLMUsageLog.response_time_ms)).select_from(
            base_query.subquery()
        )
        avg_time_result = await self.db.execute(avg_time_query)
        avg_response_time = float(avg_time_result.scalar() or 0)

        # Get requests by provider
        provider_query = select(
            LLMUsageLog.provider_id,
            func.count().label("count"),
        ).select_from(base_query.subquery())
        provider_query = provider_query.group_by(LLMUsageLog.provider_id)
        provider_result = await self.db.execute(provider_query)
        requests_by_provider = {row[0]: row[1] for row in provider_result.all()}

        # Get tokens by model
        model_query = select(
            LLMUsageLog.model_used,
            func.sum(LLMUsageLog.tokens_input + LLUsageLog.tokens_output).label("total"),
        ).select_from(base_query.subquery())
        model_query = model_query.group_by(LLMUsageLog.model_used)
        model_result = await self.db.execute(model_query)
        tokens_by_model = {row[0]: row[1] for row in model_result.all()}

        # Get cost by provider
        cost_by_provider_query = select(
            LLMUsageLog.provider_id,
            func.sum(LLMUsageLog.cost_usd).label("total"),
        ).select_from(base_query.subquery())
        cost_by_provider_query = cost_by_provider_query.group_by(LLMUsageLog.provider_id)
        cost_by_provider_result = await self.db.execute(cost_by_provider_query)
        cost_by_provider = {
            row[0]: row[1] or Decimal("0.00") for row in cost_by_provider_result.all()
        }

        return LLMUsageStats(
            total_requests=total_requests,
            total_tokens_input=total_tokens_input,
            total_tokens_output=total_tokens_output,
            total_cost_usd=total_cost,
            success_rate=success_rate,
            avg_response_time_ms=avg_response_time,
            requests_by_provider=requests_by_provider,
            tokens_by_model=tokens_by_model,
            cost_by_provider=cost_by_provider,
        )

    async def get_usage_logs(
        self,
        provider_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[LLMUsageLog]:
        """Get usage logs with filters.

        Args:
            provider_id: Filter by provider ID.
            user_id: Filter by user ID.
            agent_id: Filter by agent ID.
            start_date: Filter by start date.
            end_date: Filter by end date.
            status: Filter by status.
            skip: Number of records to skip.
            limit: Maximum number of records.

        Returns:
            List[LLMUsageLog]: List of usage logs.
        """
        query = select(LLMUsageLog)

        if provider_id:
            query = query.where(LLMUsageLog.provider_id == provider_id)
        if user_id:
            query = query.where(LLMUsageLog.user_id == user_id)
        if agent_id:
            query = query.where(LLMUsageLog.agent_id == agent_id)
        if start_date:
            query = query.where(LLMUsageLog.created_at >= start_date)
        if end_date:
            query = query.where(LLMUsageLog.created_at <= end_date)
        if status:
            query = query.where(LLMUsageLog.status == status)

        query = query.order_by(LLMUsageLog.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())


def get_llm_provider_service(db: AsyncSession) -> LLMProviderService:
    """Get LLM provider service instance.

    Args:
        db: Database session.

    Returns:
        LLMProviderService: Service instance.
    """
    return LLMProviderService(db)
