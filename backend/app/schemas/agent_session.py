"""Agent session schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class AgentSessionBase(BaseModel):
    """Base agent session schema."""

    agent_id: str = Field(..., description="Agent ID")
    session_type: str = Field(default="execution", description="Session type")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Session context")


class AgentSessionCreate(AgentSessionBase):
    """Schema for creating a session."""

    pass


class AgentSessionResponse(BaseModel):
    """Schema for session response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Session ID")
    agent_id: str = Field(..., description="Agent ID")
    session_type: str = Field(..., description="Session type")
    status: str = Field(..., description="Session status")
    started_at: datetime = Field(..., description="Start timestamp")
    ended_at: Optional[datetime] = Field(default=None, description="End timestamp")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Context")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata")
    error_message: Optional[str] = Field(default=None, description="Error message")
