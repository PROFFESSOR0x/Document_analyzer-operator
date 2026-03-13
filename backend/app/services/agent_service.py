"""Agent management service."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.agent_session import AgentSession
from app.models.agent_metric import AgentMetric
from app.schemas.agent import AgentCreate, AgentUpdate
from app.core.logging_config import get_logger


class AgentService:
    """Service for agent operations.

    This service provides:
    - Agent CRUD operations
    - Agent session management
    - Agent metrics collection
    - Agent status management
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize agent service.

        Args:
            db: Database session.
        """
        self._db = db
        self._logger = get_logger("service.agent")

    # ========== Agent CRUD ==========

    async def create_agent(
        self,
        agent_data: AgentCreate,
        owner_id: str,
    ) -> Agent:
        """Create a new agent.

        Args:
            agent_data: Agent creation data.
            owner_id: Owner user ID.

        Returns:
            Agent: Created agent.
        """
        agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            owner_id=owner_id,
            agent_type_id=agent_data.agent_type_id,
            model=agent_data.model,
            temperature=agent_data.temperature,
            max_tokens=agent_data.max_tokens,
            system_prompt=agent_data.system_prompt,
            is_public=agent_data.is_public,
            config=agent_data.config,
            status="idle",
        )

        self._db.add(agent)
        await self._db.commit()
        await self._db.refresh(agent)

        self._logger.info(f"Created agent: {agent.name} ({agent.id})")
        return agent

    async def get_agent(self, agent_id: str, owner_id: Optional[str] = None) -> Optional[Agent]:
        """Get an agent by ID.

        Args:
            agent_id: Agent ID.
            owner_id: Optional owner ID for filtering.

        Returns:
            Optional[Agent]: Agent or None.
        """
        query = select(Agent).where(Agent.id == agent_id)
        if owner_id:
            query = query.where(Agent.owner_id == owner_id)

        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def list_agents(
        self,
        owner_id: str,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None,
        agent_type: Optional[str] = None,
    ) -> List[Agent]:
        """List agents.

        Args:
            owner_id: Owner user ID.
            skip: Number to skip.
            limit: Maximum to return.
            status_filter: Optional status filter.
            agent_type: Optional type filter.

        Returns:
            List[Agent]: List of agents.
        """
        query = select(Agent).where(Agent.owner_id == owner_id)

        if status_filter:
            query = query.where(Agent.status == status_filter)

        if agent_type:
            query = query.where(Agent.agent_type_id == agent_type)

        query = query.offset(skip).limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def update_agent(
        self,
        agent_id: str,
        agent_data: AgentUpdate,
        owner_id: str,
    ) -> Optional[Agent]:
        """Update an agent.

        Args:
            agent_id: Agent ID.
            agent_data: Update data.
            owner_id: Owner user ID.

        Returns:
            Optional[Agent]: Updated agent or None.
        """
        agent = await self.get_agent(agent_id, owner_id)
        if not agent:
            return None

        update_data = agent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)

        agent.updated_at = datetime.now(timezone.utc)

        self._db.add(agent)
        await self._db.commit()
        await self._db.refresh(agent)

        self._logger.info(f"Updated agent: {agent.name} ({agent.id})")
        return agent

    async def delete_agent(self, agent_id: str, owner_id: str) -> bool:
        """Delete an agent.

        Args:
            agent_id: Agent ID.
            owner_id: Owner user ID.

        Returns:
            bool: True if deleted.
        """
        agent = await self.get_agent(agent_id, owner_id)
        if not agent:
            return False

        await self._db.delete(agent)
        await self._db.commit()

        self._logger.info(f"Deleted agent: {agent.name} ({agent.id})")
        return True

    # ========== Session Management ==========

    async def create_session(
        self,
        agent_id: str,
        session_type: str = "execution",
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentSession:
        """Create an agent session.

        Args:
            agent_id: Agent ID.
            session_type: Session type.
            context: Session context.

        Returns:
            AgentSession: Created session.
        """
        session = AgentSession(
            agent_id=agent_id,
            session_type=session_type,
            status="active",
            started_at=datetime.now(timezone.utc),
            context=context or {},
        )

        self._db.add(session)
        await self._db.commit()
        await self._db.refresh(session)

        return session

    async def end_session(
        self,
        session_id: str,
        error_message: Optional[str] = None,
    ) -> Optional[AgentSession]:
        """End an agent session.

        Args:
            session_id: Session ID.
            error_message: Optional error message.

        Returns:
            Optional[AgentSession]: Updated session or None.
        """
        query = select(AgentSession).where(AgentSession.id == session_id)
        result = await self._db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            return None

        session.status = "failed" if error_message else "completed"
        session.ended_at = datetime.now(timezone.utc)
        session.error_message = error_message

        self._db.add(session)
        await self._db.commit()

        return session

    async def get_active_session(self, agent_id: str) -> Optional[AgentSession]:
        """Get active session for an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            Optional[AgentSession]: Active session or None.
        """
        query = select(AgentSession).where(
            AgentSession.agent_id == agent_id,
            AgentSession.status == "active",
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    # ========== Metrics ==========

    async def record_metric(
        self,
        agent_id: str,
        metric_type: str,
        metric_name: str,
        metric_value: float,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentMetric:
        """Record an agent metric.

        Args:
            agent_id: Agent ID.
            metric_type: Metric type.
            metric_name: Metric name.
            metric_value: Metric value.
            task_id: Optional task ID.
            metadata: Optional metadata.

        Returns:
            AgentMetric: Created metric.
        """
        metric = AgentMetric(
            agent_id=agent_id,
            metric_type=metric_type,
            metric_name=metric_name,
            metric_value=metric_value,
            timestamp=datetime.now(timezone.utc),
            task_id=task_id,
            metadata=metadata or {},
        )

        self._db.add(metric)
        await self._db.commit()

        return metric

    async def get_agent_metrics(
        self,
        agent_id: str,
        metric_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[AgentMetric]:
        """Get metrics for an agent.

        Args:
            agent_id: Agent ID.
            metric_type: Optional type filter.
            limit: Maximum to return.

        Returns:
            List[AgentMetric]: List of metrics.
        """
        query = select(AgentMetric).where(AgentMetric.agent_id == agent_id)

        if metric_type:
            query = query.where(AgentMetric.metric_type == metric_type)

        query = query.order_by(AgentMetric.timestamp.desc()).limit(limit)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    # ========== Statistics ==========

    async def get_agent_count(self, owner_id: str) -> int:
        """Get agent count for a user.

        Args:
            owner_id: Owner user ID.

        Returns:
            int: Agent count.
        """
        query = select(func.count()).select_from(Agent).where(Agent.owner_id == owner_id)
        result = await self._db.execute(query)
        return result.scalar_one() or 0

    async def get_status_counts(self, owner_id: str) -> Dict[str, int]:
        """Get agent counts by status.

        Args:
            owner_id: Owner user ID.

        Returns:
            Dict[str, int]: Counts by status.
        """
        query = select(Agent.status, func.count()).where(
            Agent.owner_id == owner_id
        ).group_by(Agent.status)

        result = await self._db.execute(query)
        return {row[0]: row[1] for row in result.all()}
