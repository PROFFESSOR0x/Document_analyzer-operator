"""WebSocket connection manager for real-time events."""

from collections.abc import AsyncGenerator
from typing import Dict, List, Optional, Set
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting.

    This class handles:
    - Connection lifecycle (connect/disconnect)
    - User-to-connection mapping
    - Room-based subscriptions
    - Message broadcasting
    """

    def __init__(self) -> None:
        """Initialize the connection manager."""
        # Active connections: {connection_id: WebSocket}
        self._active_connections: Dict[str, WebSocket] = {}
        # User connections: {user_id: set[connection_id]}
        self._user_connections: Dict[str, Set[str]] = {}
        # Room connections: {room_id: set[connection_id]}
        self._room_connections: Dict[str, Set[str]] = {}
        # Connection metadata: {connection_id: dict}
        self._connection_metadata: Dict[str, dict] = {}

    async def connect(
        self,
        websocket: WebSocket,
        user_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """Accept and register a new WebSocket connection.

        Args:
            websocket: The WebSocket connection.
            user_id: Optional user ID for user-specific routing.
            metadata: Optional connection metadata.

        Returns:
            str: The generated connection ID.
        """
        await websocket.accept()

        connection_id = str(uuid4())
        self._active_connections[connection_id] = websocket
        self._connection_metadata[connection_id] = metadata or {}

        if user_id:
            if user_id not in self._user_connections:
                self._user_connections[user_id] = set()
            self._user_connections[user_id].add(connection_id)

        logger.info(f"WebSocket connected: {connection_id} (user={user_id})")
        return connection_id

    def disconnect(self, connection_id: str) -> None:
        """Remove a WebSocket connection.

        Args:
            connection_id: The connection ID to remove.
        """
        if connection_id not in self._active_connections:
            return

        # Remove from rooms
        for room_connections in self._room_connections.values():
            room_connections.discard(connection_id)

        # Remove from user connections
        metadata = self._connection_metadata.get(connection_id, {})
        user_id = metadata.get("user_id")
        if user_id and user_id in self._user_connections:
            self._user_connections[user_id].discard(connection_id)
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]

        # Remove connection
        del self._active_connections[connection_id]
        del self._connection_metadata[connection_id]

        logger.info(f"WebSocket disconnected: {connection_id}")

    async def send_personal(self, connection_id: str, message: dict) -> bool:
        """Send a message to a specific connection.

        Args:
            connection_id: The target connection ID.
            message: The message to send.

        Returns:
            bool: True if message was sent successfully.
        """
        websocket = self._active_connections.get(connection_id)
        if not websocket:
            return False

        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            return False

    async def send_to_user(self, user_id: str, message: dict) -> int:
        """Send a message to all connections of a user.

        Args:
            user_id: The target user ID.
            message: The message to send.

        Returns:
            int: Number of connections the message was sent to.
        """
        connection_ids = self._user_connections.get(user_id, set())
        sent_count = 0

        for connection_id in connection_ids:
            if await self.send_personal(connection_id, message):
                sent_count += 1

        return sent_count

    async def send_to_room(self, room_id: str, message: dict) -> int:
        """Send a message to all connections in a room.

        Args:
            room_id: The target room ID.
            message: The message to send.

        Returns:
            int: Number of connections the message was sent to.
        """
        connection_ids = self._room_connections.get(room_id, set())
        sent_count = 0

        for connection_id in connection_ids:
            if await self.send_personal(connection_id, message):
                sent_count += 1

        return sent_count

    async def broadcast(self, message: dict) -> int:
        """Broadcast a message to all active connections.

        Args:
            message: The message to broadcast.

        Returns:
            int: Number of connections the message was sent to.
        """
        sent_count = 0

        for connection_id in list(self._active_connections.keys()):
            if await self.send_personal(connection_id, message):
                sent_count += 1

        return sent_count

    def join_room(self, connection_id: str, room_id: str) -> bool:
        """Add a connection to a room.

        Args:
            connection_id: The connection ID.
            room_id: The room ID to join.

        Returns:
            bool: True if successfully joined.
        """
        if connection_id not in self._active_connections:
            return False

        if room_id not in self._room_connections:
            self._room_connections[room_id] = set()

        self._room_connections[room_id].add(connection_id)
        logger.info(f"Connection {connection_id} joined room {room_id}")
        return True

    def leave_room(self, connection_id: str, room_id: str) -> bool:
        """Remove a connection from a room.

        Args:
            connection_id: The connection ID.
            room_id: The room ID to leave.

        Returns:
            bool: True if successfully left.
        """
        if room_id in self._room_connections:
            self._room_connections[room_id].discard(connection_id)
            if not self._room_connections[room_id]:
                del self._room_connections[room_id]
            logger.info(f"Connection {connection_id} left room {room_id}")
            return True
        return False

    def get_connection_count(self) -> int:
        """Get the total number of active connections.

        Returns:
            int: Number of active connections.
        """
        return len(self._active_connections)

    def get_user_connection_count(self, user_id: str) -> int:
        """Get the number of connections for a user.

        Args:
            user_id: The user ID.

        Returns:
            int: Number of connections.
        """
        return len(self._user_connections.get(user_id, set()))

    def get_room_connection_count(self, room_id: str) -> int:
        """Get the number of connections in a room.

        Args:
            room_id: The room ID.

        Returns:
            int: Number of connections.
        """
        return len(self._room_connections.get(room_id, set()))


# Global connection manager instance
connection_manager = ConnectionManager()
