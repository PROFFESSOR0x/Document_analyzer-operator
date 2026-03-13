"""Agent communication protocol and message types."""

from enum import Enum
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Enumeration of message types.

    Attributes:
        REQUEST: Request message expecting a response.
        RESPONSE: Response to a request.
        EVENT: One-way event notification.
        COMMAND: Command to execute.
        RESULT: Result of a command execution.
        ERROR: Error notification.
    """

    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    COMMAND = "command"
    RESULT = "result"
    ERROR = "error"


class MessagePriority(int, Enum):
    """Enumeration of message priorities.

    Attributes:
        LOW: Low priority messages.
        NORMAL: Normal priority (default).
        HIGH: High priority messages.
        CRITICAL: Critical messages processed immediately.
    """

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class MessageStatus(str, Enum):
    """Enumeration of message statuses.

    Attributes:
        PENDING: Message pending processing.
        PROCESSING: Message being processed.
        COMPLETED: Message processing completed.
        FAILED: Message processing failed.
        TIMEOUT: Message processing timed out.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class AgentMessage(BaseModel):
    """Base class for all agent messages.

    Attributes:
        id: Unique message identifier.
        type: Type of message.
        priority: Message priority level.
        sender_id: ID of the sending agent.
        receiver_id: ID of the receiving agent.
        correlation_id: ID for correlating request/response pairs.
        timestamp: Message creation timestamp.
        payload: Message payload data.
        metadata: Additional message metadata.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: MessageType = Field(default=MessageType.EVENT)
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)
    sender_id: Optional[str] = Field(default=None)
    receiver_id: Optional[str] = Field(default=None)
    correlation_id: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary.

        Returns:
            Dict: Message as dictionary.
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "priority": self.priority.value,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary.

        Args:
            data: Message data dictionary.

        Returns:
            AgentMessage: Created message instance.
        """
        return cls(
            id=data.get("id", str(uuid4())),
            type=MessageType(data.get("type", "event")),
            priority=MessagePriority(data.get("priority", 1)),
            sender_id=data.get("sender_id"),
            receiver_id=data.get("receiver_id"),
            correlation_id=data.get("correlation_id"),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.now(timezone.utc),
            payload=data.get("payload", {}),
            metadata=data.get("metadata", {}),
        )


class RequestMessage(AgentMessage):
    """Request message expecting a response.

    Attributes:
        timeout_seconds: Request timeout in seconds.
        retry_count: Number of retry attempts.
        requires_ack: Whether acknowledgment is required.
    """

    type: MessageType = Field(default=MessageType.REQUEST, init=False)
    timeout_seconds: float = Field(default=30.0)
    retry_count: int = Field(default=0)
    requires_ack: bool = Field(default=True)

    def create_response(
        self,
        payload: Dict[str, Any],
        sender_id: Optional[str] = None,
    ) -> "ResponseMessage":
        """Create a response message for this request.

        Args:
            payload: Response payload.
            sender_id: ID of the responding agent.

        Returns:
            ResponseMessage: Response message.
        """
        return ResponseMessage(
            correlation_id=self.id,
            sender_id=sender_id or self.receiver_id,
            receiver_id=self.sender_id,
            payload=payload,
            priority=self.priority,
        )


class ResponseMessage(AgentMessage):
    """Response to a request message.

    Attributes:
        success: Whether the request was successful.
        error_message: Error message if request failed.
    """

    type: MessageType = Field(default=MessageType.RESPONSE, init=False)
    success: bool = Field(default=True)
    error_message: Optional[str] = Field(default=None)


class EventMessage(AgentMessage):
    """One-way event notification.

    Attributes:
        event_name: Name of the event.
        broadcast: Whether to broadcast to all agents.
    """

    type: MessageType = Field(default=MessageType.EVENT, init=False)
    event_name: str = Field(default="")
    broadcast: bool = Field(default=False)


class CommandMessage(AgentMessage):
    """Command to execute on an agent.

    Attributes:
        command: Command name.
        args: Command arguments.
        kwargs: Command keyword arguments.
    """

    type: MessageType = Field(default=MessageType.COMMAND, init=False)
    command: str = Field(default="")
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)


class ResultMessage(AgentMessage):
    """Result of a command execution.

    Attributes:
        command: Command that was executed.
        success: Whether execution was successful.
        result: Execution result.
        error_message: Error message if execution failed.
    """

    type: MessageType = Field(default=MessageType.RESULT, init=False)
    command: str = Field(default="")
    success: bool = Field(default=True)
    result: Any = Field(default=None)
    error_message: Optional[str] = Field(default=None)


class ErrorMessage(AgentMessage):
    """Error notification message.

    Attributes:
        error_type: Type of error.
        error_message: Detailed error message.
        stack_trace: Optional stack trace.
        recoverable: Whether the error is recoverable.
    """

    type: MessageType = Field(default=MessageType.ERROR, init=False)
    error_type: str = Field(default="")
    error_message: str = Field(default="")
    stack_trace: Optional[str] = Field(default=None)
    recoverable: bool = Field(default=True)


@dataclass
class MessageEnvelope:
    """Envelope for message transport with routing information.

    Attributes:
        message: The encapsulated message.
        route: Routing path for the message.
        hops: Number of hops the message has taken.
        created_at: When the envelope was created.
        expires_at: When the envelope expires.
    """

    message: AgentMessage
    route: List[str] = field(default_factory=list)
    hops: int = field(default=0)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if the envelope has expired.

        Returns:
            bool: True if expired.
        """
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def add_hop(self, agent_id: str) -> None:
        """Record a hop in the message route.

        Args:
            agent_id: ID of the agent that processed the message.
        """
        self.route.append(agent_id)
        self.hops += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert envelope to dictionary.

        Returns:
            Dict: Envelope data as dictionary.
        """
        return {
            "message": self.message.to_dict(),
            "route": self.route,
            "hops": self.hops,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
