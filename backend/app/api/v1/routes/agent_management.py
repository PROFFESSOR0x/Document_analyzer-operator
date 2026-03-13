"""Agent management API endpoints."""

from typing import Annotated, Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ActiveUser, get_db
from app.db.session import get_db
from app.models.agent import Agent
from app.schemas.agent import (
    AgentCreate,
    AgentResponse,
    AgentUpdate,
    AgentInfoSchema,
    AgentStatusSchema,
    AgentTelemetrySchema,
    AgentCapabilitiesSchema,
)
from app.schemas.agent_session import AgentSessionResponse
from app.schemas.agent_metric import AgentMetricResponse
from app.services.agent_service import AgentService
from app.websocket.events import WebSocketEvent, EventType, event_subscriber
from app.websocket.manager import connection_manager

router = APIRouter()


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0, description="Number to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    agent_type: Optional[str] = Query(None, description="Filter by type"),
) -> List[Agent]:
    """List all agents owned by the current user."""
    service = AgentService(db)
    return await service.list_agents(
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        agent_type=agent_type,
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Agent:
    """Get a specific agent by ID."""
    service = AgentService(db)
    agent = await service.get_agent(agent_id, owner_id=current_user.id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    return agent


@router.get("/{agent_id}/info", response_model=AgentInfoSchema)
async def get_agent_info(
    agent_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AgentInfoSchema:
    """Get complete agent information including status and telemetry."""
    service = AgentService(db)
    agent = await service.get_agent(agent_id, owner_id=current_user.id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Build agent info (in production, this would come from the agent framework)
    return AgentInfoSchema(
        agent=AgentResponse.model_validate(agent),
        status=AgentStatusSchema(
            state=agent.status,
            lifecycle_state="initialized",
            last_activity=datetime.now(timezone.utc),
        ),
    )


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Agent:
    """Create a new agent."""
    service = AgentService(db)
    return await service.create_agent(agent_data, owner_id=current_user.id)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Agent:
    """Update an existing agent."""
    service = AgentService(db)
    agent = await service.update_agent(agent_id, agent_data, owner_id=current_user.id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete an agent."""
    service = AgentService(db)
    deleted = await service.delete_agent(agent_id, owner_id=current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )


@router.get("/{agent_id}/sessions", response_model=List[AgentSessionResponse])
async def list_agent_sessions(
    agent_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=500),
) -> List:
    """List sessions for an agent."""
    service = AgentService(db)
    
    # Verify agent ownership
    agent = await service.get_agent(agent_id, owner_id=current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Get sessions (would need to add this method to service)
    return []


@router.get("/{agent_id}/metrics", response_model=List[AgentMetricResponse])
async def list_agent_metrics(
    agent_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    metric_type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(100, ge=1, le=1000),
) -> List:
    """List metrics for an agent."""
    service = AgentService(db)
    
    # Verify agent ownership
    agent = await service.get_agent(agent_id, owner_id=current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    metrics = await service.get_agent_metrics(agent_id, metric_type=metric_type, limit=limit)
    return [AgentMetricResponse.model_validate(m) for m in metrics]


@router.post("/{agent_id}/start")
async def start_agent(
    agent_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Start an agent."""
    service = AgentService(db)
    agent = await service.get_agent(agent_id, owner_id=current_user.id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Update status
    agent.status = "running"
    db.add(agent)
    await db.commit()

    # Publish event
    await event_subscriber.publish(WebSocketEvent(
        event_type=EventType.AGENT_STATUS_CHANGED,
        data={"agent_id": agent_id, "status": "running"},
    ))

    return {"status": "started", "agent_id": agent_id}


@router.post("/{agent_id}/stop")
async def stop_agent(
    agent_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Stop an agent."""
    service = AgentService(db)
    agent = await service.get_agent(agent_id, owner_id=current_user.id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Update status
    agent.status = "stopped"
    db.add(agent)
    await db.commit()

    # Publish event
    await event_subscriber.publish(WebSocketEvent(
        event_type=EventType.AGENT_STATUS_CHANGED,
        data={"agent_id": agent_id, "status": "stopped"},
    ))

    return {"status": "stopped", "agent_id": agent_id}


@router.websocket("/ws/{agent_id}")
async def agent_websocket(
    websocket: WebSocket,
    agent_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """WebSocket endpoint for agent real-time updates."""
    service = AgentService(db)
    
    # Verify agent ownership
    agent = await service.get_agent(agent_id, owner_id=current_user.id)
    if not agent:
        await websocket.close(code=4004, reason="Agent not found")
        return

    # Connect
    connection_id = await connection_manager.connect(
        websocket,
        user_id=current_user.id,
        metadata={"agent_id": agent_id},
    )

    # Subscribe to agent events
    event_subscriber.subscribe(connection_id, EventType.AGENT_STATUS_CHANGED, current_user.id)
    event_subscriber.subscribe(connection_id, EventType.AGENT_OUTPUT, current_user.id)

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        pass
    finally:
        event_subscriber.unsubscribe(connection_id)
        connection_manager.disconnect(connection_id)
