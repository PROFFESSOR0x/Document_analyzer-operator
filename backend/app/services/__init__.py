"""Services module initialization."""

from app.services.agent_service import AgentService
from app.services.user_service import UserService
from app.services.llm_provider_service import (
    LLMProviderService,
    get_llm_provider_service,
    EncryptionError,
)
from app.services.llm_client import (
    LLMClient,
    create_llm_client,
    BaseProvider,
    OpenAIProvider,
    AnthropicProvider,
    OllamaProvider,
    LMStudioProvider,
    VLLMProvider,
    CustomProvider,
    LLMResponse,
    LLMStreamChunk,
    TokenUsage,
    LLMError,
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    ProviderError,
)
from app.services.settings_service import (
    SettingsService,
    get_settings_service,
    SettingsEncryptionError,
    SettingsValidationError,
)

__all__ = [
    # Agent & User Services
    "AgentService",
    "UserService",
    # LLM Provider Service
    "LLMProviderService",
    "get_llm_provider_service",
    "EncryptionError",
    # LLM Client
    "LLMClient",
    "create_llm_client",
    # Provider Classes
    "BaseProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "LMStudioProvider",
    "VLLMProvider",
    "CustomProvider",
    # Response Types
    "LLMResponse",
    "LLMStreamChunk",
    "TokenUsage",
    # Exceptions
    "LLMError",
    "AuthenticationError",
    "RateLimitError",
    "TimeoutError",
    "ProviderError",
    # Settings Service
    "SettingsService",
    "get_settings_service",
    "SettingsEncryptionError",
    "SettingsValidationError",
]
