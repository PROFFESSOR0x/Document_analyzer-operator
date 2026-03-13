"""Agent schemas for request/response validation."""

from datetime import datetime
from typing import Any, Dict, Optional, List

from pydantic import BaseModel, ConfigDict, Field


class AgentBase(BaseModel):
    """Base agent schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    description: Optional[str] = Field(default=None, description="Agent description")
    agent_type_id: Optional[str] = Field(default=None, description="Agent type ID")
    model: str = Field(default="gpt-4", description="LLM model identifier")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Model temperature"
    )
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens")
    system_prompt: Optional[str] = Field(default=None, description="System prompt")
    is_public: bool = Field(default=False, description="Public visibility")


class AgentCreate(AgentBase):
    """Schema for creating a new agent."""

    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Agent configuration"
    )


class AgentUpdate(BaseModel):
    """Schema for updating an agent."""

    name: Optional[str] = Field(
        default=None, min_length=1, max_length=100, description="Agent name"
    )
    description: Optional[str] = Field(default=None, description="Agent description")
    agent_type_id: Optional[str] = Field(default=None, description="Agent type ID")
    status: Optional[str] = Field(default=None, description="Agent status")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Configuration")
    system_prompt: Optional[str] = Field(default=None, description="System prompt")
    model: Optional[str] = Field(default=None, description="LLM model")
    temperature: Optional[float] = Field(
        default=None, ge=0.0, le=2.0, description="Temperature"
    )
    max_tokens: Optional[int] = Field(default=None, description="Max tokens")
    is_public: Optional[bool] = Field(default=None, description="Public visibility")
    version: Optional[str] = Field(default=None, description="Version")


class AgentResponse(AgentBase):
    """Schema for agent response data."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Agent ID")
    owner_id: str = Field(..., description="Owner user ID")
    status: str = Field(default="idle", description="Agent status")
    version: str = Field(default="1.0.0", description="Agent version")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class AgentInDB(AgentResponse):
    """Schema for agent data stored in database."""

    config: Optional[Dict[str, Any]] = Field(default=None, description="Configuration")


class AgentCapabilitiesSchema(BaseModel):
    """Schema for agent capabilities."""

    category: str = Field(..., description="Agent category")
    skills: List[str] = Field(default_factory=list, description="Agent skills")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class AgentStatusSchema(BaseModel):
    """Schema for agent status."""

    state: str = Field(..., description="Agent state")
    lifecycle_state: str = Field(..., description="Lifecycle state")
    current_task_id: Optional[str] = Field(default=None, description="Current task ID")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    error_message: Optional[str] = Field(default=None, description="Error message")


class AgentTelemetrySchema(BaseModel):
    """Schema for agent telemetry data."""

    agent_id: str = Field(..., description="Agent ID")
    uptime_seconds: float = Field(..., description="Uptime in seconds")
    health_score: float = Field(..., description="Health score (0-100)")
    metrics: Dict[str, Any] = Field(..., description="Execution metrics")
    recent_events: List[Dict[str, Any]] = Field(default_factory=list, description="Recent events")


class AgentInfoSchema(BaseModel):
    """Schema for complete agent information."""

    agent: AgentResponse
    capabilities: Optional[AgentCapabilitiesSchema] = None
    status: Optional[AgentStatusSchema] = None
    telemetry: Optional[AgentTelemetrySchema] = None
