"""LLM Provider schemas for request/response validation."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProviderTypeSchema(str):
    """Schema for provider type enumeration."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    VLLM = "vllm"
    CUSTOM = "custom"


class LLMProviderBase(BaseModel):
    """Base LLM provider schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Provider name")
    provider_type: str = Field(..., description="Provider type (openai, anthropic, ollama, etc.)")
    base_url: str = Field(..., description="API base URL")
    model_name: str = Field(..., description="Default model name")
    api_key: Optional[str] = Field(default=None, description="API key (encrypted)")
    is_active: bool = Field(default=True, description="Provider enabled status")
    is_default: bool = Field(default=False, description="Default provider flag")
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional configuration",
    )


class LLMProviderCreate(LLMProviderBase):
    """Schema for creating a new LLM provider."""

    pass


class LLMProviderUpdate(BaseModel):
    """Schema for updating an LLM provider."""

    name: Optional[str] = Field(
        default=None, min_length=1, max_length=100, description="Provider name"
    )
    provider_type: Optional[str] = Field(default=None, description="Provider type")
    base_url: Optional[str] = Field(default=None, description="API base URL")
    model_name: Optional[str] = Field(default=None, description="Default model name")
    api_key: Optional[str] = Field(default=None, description="API key")
    is_active: Optional[bool] = Field(default=None, description="Enabled status")
    is_default: Optional[bool] = Field(default=None, description="Default provider flag")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Configuration")


class LLMProviderResponse(LLMProviderBase):
    """Schema for LLM provider response data."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Provider ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_validator("api_key")
    @classmethod
    def mask_api_key(cls, v: Optional[str]) -> Optional[str]:
        """Mask API key for security."""
        if v and len(v) > 8:
            return f"{v[:4]}••••••{v[-4:]}"
        return "••••••••" if v else None


class LLMProviderList(BaseModel):
    """Schema for LLM provider list response."""

    providers: List[LLMProviderResponse]
    total: int = Field(..., description="Total number of providers")


class LLMProviderPreset(BaseModel):
    """Schema for LLM provider preset configuration."""

    name: str = Field(..., description="Preset name")
    provider_type: str = Field(..., description="Provider type")
    base_url: str = Field(..., description="Default base URL")
    model_name: str = Field(..., description="Default model")
    requires_api_key: bool = Field(..., description="Whether API key is required")
    description: str = Field(..., description="Preset description")
    config_template: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default configuration template",
    )


class LLMProviderPresets(BaseModel):
    """Schema for list of provider presets."""

    presets: List[LLMProviderPreset]


class LLMTestRequest(BaseModel):
    """Schema for testing LLM provider connection."""

    model_name: Optional[str] = Field(default=None, description="Model to test")
    test_prompt: Optional[str] = Field(
        default="Hello, this is a test.",
        description="Test prompt",
    )


class LLMTestResponse(BaseModel):
    """Schema for LLM provider test response."""

    success: bool = Field(..., description="Test success status")
    message: str = Field(..., description="Test result message")
    model_tested: str = Field(..., description="Model that was tested")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class LLMUsageLogBase(BaseModel):
    """Base usage log schema with common fields."""

    provider_id: str = Field(..., description="Provider ID")
    user_id: str = Field(..., description="User ID")
    agent_id: Optional[str] = Field(default=None, description="Agent ID")
    model_used: str = Field(..., description="Model used")
    tokens_input: int = Field(default=0, description="Input tokens")
    tokens_output: int = Field(default=0, description="Output tokens")
    cost_usd: Optional[Decimal] = Field(default=None, description="Cost in USD")
    request_type: str = Field(..., description="Request type (completion, embedding, chat)")
    status: str = Field(..., description="Request status (success, failed)")
    error_message: Optional[str] = Field(default=None, description="Error message")
    response_time_ms: int = Field(..., description="Response time in ms")


class LLMUsageLogCreate(LLMUsageLogBase):
    """Schema for creating a usage log entry."""

    pass


class LLMUsageLogResponse(LLMUsageLogBase):
    """Schema for usage log response data."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Log ID")
    created_at: datetime = Field(..., description="Creation timestamp")


class LLMUsageLogList(BaseModel):
    """Schema for usage log list response."""

    logs: List[LLMUsageLogResponse]
    total: int = Field(..., description="Total number of logs")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")


class LLMUsageStats(BaseModel):
    """Schema for LLM usage statistics."""

    total_requests: int = Field(..., description="Total number of requests")
    total_tokens_input: int = Field(..., description="Total input tokens")
    total_tokens_output: int = Field(..., description="Total output tokens")
    total_cost_usd: Decimal = Field(..., description="Total cost in USD")
    success_rate: float = Field(..., description="Success rate percentage")
    avg_response_time_ms: float = Field(..., description="Average response time in ms")
    requests_by_provider: Dict[str, int] = Field(
        default_factory=dict,
        description="Requests count by provider",
    )
    tokens_by_model: Dict[str, int] = Field(
        default_factory=dict,
        description="Total tokens by model",
    )
    cost_by_provider: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Cost by provider",
    )


class LLMUsageStatsRequest(BaseModel):
    """Schema for usage statistics request filters."""

    start_date: Optional[datetime] = Field(default=None, description="Start date")
    end_date: Optional[datetime] = Field(default=None, description="End date")
    provider_id: Optional[str] = Field(default=None, description="Filter by provider")
    user_id: Optional[str] = Field(default=None, description="Filter by user")
    agent_id: Optional[str] = Field(default=None, description="Filter by agent")
