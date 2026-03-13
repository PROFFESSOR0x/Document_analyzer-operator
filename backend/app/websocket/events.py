"""WebSocket event types and subscription system."""

from enum import Enum
from typing import Any, Callable, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json

from app.core.logging_config import get_logger
from app.websocket.manager import connection_manager

logger = get_logger(__name__)


class EventType(str, Enum):
    """Enumeration of WebSocket event types."""

    # Connection events
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"

    # Authentication events
    AUTH_SUCCESS = "auth.success"
    AUTH_ERROR = "auth.error"

    # Task events
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"

    # Agent events
    AGENT_STATUS_CHANGED = "agent.status_changed"
    AGENT_OUTPUT = "agent.output"

    # Workflow events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_PROGRESS = "workflow.progress"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"

    # Validation events
    VALIDATION_STARTED = "validation.started"
    VALIDATION_RESULT = "validation.result"
    VALIDATION_COMPLETED = "validation.completed"

    # System events
    NOTIFICATION = "notification"
    ERROR = "error"


@dataclass
class WebSocketEvent:
    """WebSocket event data structure."""

    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary.

        Returns:
            Dict: Event as dictionary.
        """
        return {
            "event_type": self.event_type.value,
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
        }

    def to_json(self) -> str:
        """Convert event to JSON string.

        Returns:
            str: Event as JSON string.
        """
        return json.dumps(self.to_dict())


class EventSubscriber:
    """Event subscription manager for WebSocket events.

    This class provides a pub-sub system for WebSocket events,
    allowing clients to subscribe to specific event types.
    """

    def __init__(self) -> None:
        """Initialize the event subscriber."""
        # Subscribers by event type: {event_type: set[connection_id]}
        self._subscribers: Dict[EventType, Set[str]] = {}
        # User subscriptions: {user_id: set[event_type]}
        self._user_subscriptions: Dict[str, Set[EventType]] = {}

    def subscribe(
        self,
        connection_id: str,
        event_type: EventType,
        user_id: Optional[str] = None,
    ) -> bool:
        """Subscribe a connection to an event type.

        Args:
            connection_id: The connection ID.
            event_type: The event type to subscribe to.
            user_id: Optional user ID for user-specific subscriptions.

        Returns:
            bool: True if successfully subscribed.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()

        self._subscribers[event_type].add(connection_id)

        if user_id:
            if user_id not in self._user_subscriptions:
                self._user_subscriptions[user_id] = set()
            self._user_subscriptions[user_id].add(event_type)

        logger.debug(f"Connection {connection_id} subscribed to {event_type.value}")
        return True

    def unsubscribe(
        self,
        connection_id: str,
        event_type: Optional[EventType] = None,
    ) -> bool:
        """Unsubscribe a connection from events.

        Args:
            connection_id: The connection ID.
            event_type: Optional specific event type to unsubscribe from.

        Returns:
            bool: True if successfully unsubscribed.
        """
        if event_type:
            if event_type in self._subscribers:
                self._subscribers[event_type].discard(connection_id)
        else:
            # Unsubscribe from all event types
            for subscribers in self._subscribers.values():
                subscribers.discard(connection_id)

        logger.debug(f"Connection {connection_id} unsubscribed from events")
        return True

    async def publish(self, event: WebSocketEvent) -> int:
        """Publish an event to all subscribers.

        Args:
            event: The event to publish.

        Returns:
            int: Number of connections the event was sent to.
        """
        subscribers = self._subscribers.get(event.event_type, set())
        sent_count = 0

        for connection_id in subscribers:
            if await connection_manager.send_personal(
                connection_id, event.to_dict()
            ):
                sent_count += 1

        return sent_count

    async def publish_to_user(
        self,
        user_id: str,
        event: WebSocketEvent,
    ) -> int:
        """Publish an event to all connections of a user.

        Args:
            user_id: The target user ID.
            event: The event to publish.

        Returns:
            int: Number of connections the event was sent to.
        """
        # Check if user is subscribed to this event type
        user_subs = self._user_subscriptions.get(user_id, set())
        if event.event_type not in user_subs:
            return 0

        return await connection_manager.send_to_user(user_id, event.to_dict())

    def get_subscriber_count(self, event_type: EventType) -> int:
        """Get the number of subscribers for an event type.

        Args:
            event_type: The event type.

        Returns:
            int: Number of subscribers.
        """
        return len(self._subscribers.get(event_type, set()))


# Global event subscriber instance
event_subscriber = EventSubscriber()


# Helper functions for publishing common events
async def publish_task_event(
    event_type: EventType,
    task_id: str,
    data: Optional[Dict[str, Any]] = None,
) -> int:
    """Publish a task-related event.

    Args:
        event_type: The task event type.
        task_id: The task ID.
        data: Additional event data.

    Returns:
        int: Number of connections the event was sent to.
    """
    event = WebSocketEvent(
        event_type=event_type,
        data={"task_id": task_id, **(data or {})},
    )
    return await event_subscriber.publish(event)


async def publish_workflow_event(
    event_type: EventType,
    workflow_id: str,
    data: Optional[Dict[str, Any]] = None,
) -> int:
    """Publish a workflow-related event.

    Args:
        event_type: The workflow event type.
        workflow_id: The workflow ID.
        data: Additional event data.

    Returns:
        int: Number of connections the event was sent to.
    """
    event = WebSocketEvent(
        event_type=event_type,
        data={"workflow_id": workflow_id, **(data or {})},
    )
    return await event_subscriber.publish(event)


async def publish_notification(
    message: str,
    level: str = "info",
    user_id: Optional[str] = None,
) -> int:
    """Publish a notification event.

    Args:
        message: Notification message.
        level: Notification level (info, warning, error).
        user_id: Optional user ID for user-specific notification.

    Returns:
        int: Number of connections the event was sent to.
    """
    event = WebSocketEvent(
        event_type=EventType.NOTIFICATION,
        data={"message": message, "level": level},
    )

    if user_id:
        return await event_subscriber.publish_to_user(user_id, event)
    return await event_subscriber.publish(event)
