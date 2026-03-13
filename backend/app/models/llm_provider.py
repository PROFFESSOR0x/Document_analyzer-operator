"""LLM Provider model for managing AI model providers."""

from typing import TYPE_CHECKING, Optional, List
from enum import Enum

from sqlalchemy import String, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.agent import Agent
    from app.models.llm_usage import LLMUsageLog


class ProviderType(str, Enum):
    """Enumeration of supported LLM provider types.
    
    Provider types include:
    - Cloud providers: openai, anthropic
    - Local providers: ollama, lm_studio, vllm
    - Compatible providers: openai_compatible (custom OpenAI-compatible APIs)
    - Generic: custom
    """

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    VLLM = "vllm"
    OPENAI_COMPATIBLE = "openai_compatible"
    CUSTOM = "custom"


class LLMProvider(BaseModel):
    """LLM Provider model representing AI model provider configurations.

    Attributes:
        name: Provider name (e.g., "OpenAI", "Anthropic", "Local Ollama").
        provider_type: Type of provider (openai, anthropic, ollama, etc.).
        base_url: API endpoint URL.
        api_key: Encrypted API key (nullable for local providers).
        model_name: Default model to use.
        is_active: Enable/disable provider.
        is_default: Default provider for agents.
        config: Additional configuration (temperature, max_tokens, etc.).
    """

    __tablename__ = "llm_providers"

    # Basic info
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    provider_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    base_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    api_key: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Configuration
    config: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )

    # Relationships
    usage_logs: Mapped[List["LLMUsageLog"]] = relationship(
        "LLMUsageLog",
        back_populates="provider",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of the provider.

        Returns:
            str: Provider representation.
        """
        return f"<LLMProvider {self.name} ({self.provider_type})>"
