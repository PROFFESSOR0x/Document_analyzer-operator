"""Agent CRUD endpoints."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ActiveUser
from app.db.session import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate

router = APIRouter()


@router.get("", response_model=list[AgentResponse])
async def list_agents(
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by agent status"),
) -> list[Agent]:
    """List all agents owned by the current user.

    Args:
        current_user: Current authenticated user.
        db: Database session.
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        status_filter: Optional status filter.

    Returns:
        list[Agent]: List of agents.
    """
    query = select(Agent).where(Agent.owner_id == current_user.id)

    if status_filter:
        query = query.where(Agent.status == status_filter)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Agent:
    """Get a specific agent by ID.

    Args:
        agent_id: Agent ID.
        current_user: Current authenticated user.
        db: Database session.

    Returns:
        Agent: The requested agent.

    Raises:
        HTTPException: If agent not found or access denied.
    """
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.owner_id == current_user.id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    return agent


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Agent:
    """Create a new agent.

    Args:
        agent_data: Agent creation data.
        current_user: Current authenticated user.
        db: Database session.

    Returns:
        Agent: The created agent.
    """
    agent = Agent(
        name=agent_data.name,
        description=agent_data.description,
        owner_id=current_user.id,
        agent_type_id=agent_data.agent_type_id,
        model=agent_data.model,
        temperature=agent_data.temperature,
        max_tokens=agent_data.max_tokens,
        system_prompt=agent_data.system_prompt,
        is_public=agent_data.is_public,
        config=agent_data.config,
    )

    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return agent


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Agent:
    """Update an existing agent.

    Args:
        agent_id: Agent ID.
        agent_data: Agent update data.
        current_user: Current authenticated user.
        db: Database session.

    Returns:
        Agent: The updated agent.

    Raises:
        HTTPException: If agent not found or access denied.
    """
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.owner_id == current_user.id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Update only provided fields
    update_data = agent_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete an agent.

    Args:
        agent_id: Agent ID.
        current_user: Current authenticated user.
        db: Database session.

    Raises:
        HTTPException: If agent not found or access denied.
    """
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.owner_id == current_user.id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    await db.delete(agent)
    await db.commit()
