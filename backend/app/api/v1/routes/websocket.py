"""WebSocket endpoints for real-time events."""

from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.logging_config import get_logger
from app.db.session import get_db
from app.models.user import User
from app.websocket.manager import connection_manager
from app.websocket.events import (
    EventSubscriber,
    EventType,
    WebSocketEvent,
    event_subscriber,
)

logger = get_logger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
) -> None:
    """WebSocket endpoint for real-time events.

    Args:
        websocket: The WebSocket connection.
        db: Database session.
    """
    # Accept connection without authentication first
    connection_id = await connection_manager.connect(websocket)

    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()

            # Handle different message types
            message_type = data.get("type")

            if message_type == "auth":
                # Handle authentication
                token = data.get("token")
                if token:
                    try:
                        # Validate token and get user
                        from app.api.deps import get_current_user
                        from fastapi.security import HTTPAuthorizationCredentials

                        credentials = HTTPAuthorizationCredentials(
                            scheme="Bearer", credentials=token
                        )
                        user = await get_current_user(credentials, db)

                        # Update connection metadata
                        connection_manager._connection_metadata[connection_id][
                            "user_id"
                        ] = user.id

                        # Send auth success event
                        await websocket.send_json(
                            WebSocketEvent(
                                event_type=EventType.AUTH_SUCCESS,
                                data={"user_id": user.id, "connection_id": connection_id},
                            ).to_dict()
                        )

                        logger.info(f"WebSocket authenticated: {user.id}")
                    except Exception as e:
                        await websocket.send_json(
                            WebSocketEvent(
                                event_type=EventType.AUTH_ERROR,
                                data={"error": str(e)},
                            ).to_dict()
                        )

            elif message_type == "subscribe":
                # Handle subscription to event types
                event_types = data.get("event_types", [])
                user_id = connection_manager._connection_metadata.get(connection_id, {}).get(
                    "user_id"
                )

                for event_type_str in event_types:
                    try:
                        event_type = EventType(event_type_str)
                        event_subscriber.subscribe(connection_id, event_type, user_id)
                    except ValueError:
                        logger.warning(f"Invalid event type: {event_type_str}")

            elif message_type == "unsubscribe":
                # Handle unsubscription
                event_type_str = data.get("event_type")
                if event_type_str:
                    try:
                        event_type = EventType(event_type_str)
                        event_subscriber.unsubscribe(connection_id, event_type)
                    except ValueError:
                        logger.warning(f"Invalid event type: {event_type_str}")
                else:
                    event_subscriber.unsubscribe(connection_id)

            elif message_type == "join_room":
                # Handle room joining
                room_id = data.get("room_id")
                if room_id:
                    connection_manager.join_room(connection_id, room_id)

            elif message_type == "leave_room":
                # Handle room leaving
                room_id = data.get("room_id")
                if room_id:
                    connection_manager.leave_room(connection_id, room_id)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Clean up subscriptions
        event_subscriber.unsubscribe(connection_id)
        connection_manager.disconnect(connection_id)
