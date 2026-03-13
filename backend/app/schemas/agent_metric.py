"""Agent metric schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class AgentMetricBase(BaseModel):
    """Base agent metric schema."""

    agent_id: str = Field(..., description="Agent ID")
    metric_type: str = Field(..., description="Metric type")
    metric_name: str = Field(..., description="Metric name")
    metric_value: float = Field(..., description="Metric value")
    task_id: Optional[str] = Field(default=None, description="Task ID")


class AgentMetricCreate(AgentMetricBase):
    """Schema for creating a metric."""

    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata")


class AgentMetricResponse(BaseModel):
    """Schema for metric response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Metric ID")
    agent_id: str = Field(..., description="Agent ID")
    metric_type: str = Field(..., description="Metric type")
    metric_name: str = Field(..., description="Metric name")
    metric_value: float = Field(..., description="Metric value")
    timestamp: datetime = Field(..., description="Timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata")
    task_id: Optional[str] = Field(default=None, description="Task ID")
