"""Agent registry for managing agent types and instances."""

from typing import Dict, List, Optional, Type, Any, Callable, Awaitable
from datetime import datetime, timezone
import asyncio
import logging

from app.agents.core.base import BaseAgent
from app.agents.core.states import AgentState
from app.agents.core.errors import AgentRegistrationError, AgentError


class AgentTypeRegistration:
    """Registration information for an agent type.

    Attributes:
        type_name: Name of the agent type.
        agent_class: The agent class.
        description: Type description.
        capabilities: Type capabilities.
        config_schema: Configuration schema.
        created_at: Registration timestamp.
        is_active: Whether the type is active.
    """

    def __init__(
        self,
        type_name: str,
        agent_class: Type[BaseAgent],
        description: str = "",
        capabilities: Optional[Dict[str, Any]] = None,
        config_schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize agent type registration.

        Args:
            type_name: Name of the agent type.
            agent_class: The agent class.
            description: Type description.
            capabilities: Type capabilities.
            config_schema: Configuration schema.
        """
        self.type_name = type_name
        self.agent_class = agent_class
        self.description = description
        self.capabilities = capabilities or {}
        self.config_schema = config_schema or {}
        self.created_at = datetime.now(timezone.utc)
        self.is_active = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert registration to dictionary.

        Returns:
            Dict: Registration data.
        """
        return {
            "type_name": self.type_name,
            "agent_class": self.agent_class.__name__,
            "description": self.description,
            "capabilities": self.capabilities,
            "config_schema": self.config_schema,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
        }


class AgentInstanceInfo:
    """Information about a registered agent instance.

    Attributes:
        agent_id: Agent instance ID.
        agent_type: Type of agent.
        name: Agent name.
        instance: The agent instance.
        registered_at: Registration timestamp.
        last_heartbeat: Last heartbeat timestamp.
        metadata: Additional metadata.
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        name: str,
        instance: BaseAgent,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize agent instance info.

        Args:
            agent_id: Agent instance ID.
            agent_type: Type of agent.
            name: Agent name.
            instance: The agent instance.
            metadata: Additional metadata.
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.instance = instance
        self.registered_at = datetime.now(timezone.utc)
        self.last_heartbeat = datetime.now(timezone.utc)
        self.metadata = metadata or {}

    def update_heartbeat(self) -> None:
        """Update the heartbeat timestamp."""
        self.last_heartbeat = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance info to dictionary.

        Returns:
            Dict: Instance data.
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "name": self.name,
            "state": self.instance.state.value,
            "registered_at": self.registered_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "metadata": self.metadata,
        }


class AgentRegistry:
    """Registry for agent types and instances.

    This class provides:
    - Agent type registration
    - Agent instance management
    - Capability-based agent discovery
    - Agent health monitoring
    - Agent metadata storage

    Usage:
        registry = AgentRegistry()
        registry.register_type("analyzer", AnalyzerAgent)
        agent = registry.create_instance("analyzer", "my-agent", config={})
        registry.register_instance(agent)
    """

    def __init__(self) -> None:
        """Initialize agent registry."""
        self._type_registrations: Dict[str, AgentTypeRegistration] = {}
        self._instances: Dict[str, AgentInstanceInfo] = {}
        self._capability_index: Dict[str, List[str]] = {}  # capability -> [agent_ids]
        self._logger = logging.getLogger("agent.registry")

        # Health monitoring
        self._health_check_interval = 30.0  # seconds
        self._heartbeat_timeout = 90.0  # seconds
        self._health_check_task: Optional[asyncio.Task] = None

        self._logger.info("Agent registry initialized")

    def register_type(
        self,
        type_name: str,
        agent_class: Type[BaseAgent],
        description: str = "",
        capabilities: Optional[Dict[str, Any]] = None,
        config_schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register an agent type.

        Args:
            type_name: Name of the agent type.
            agent_class: The agent class.
            description: Type description.
            capabilities: Type capabilities.
            config_schema: Configuration schema.

        Raises:
            AgentRegistrationError: If type already exists.
        """
        if type_name in self._type_registrations:
            raise AgentRegistrationError(
                f"Agent type '{type_name}' is already registered",
                agent_type=type_name,
            )

        registration = AgentTypeRegistration(
            type_name=type_name,
            agent_class=agent_class,
            description=description,
            capabilities=capabilities or {},
            config_schema=config_schema or {},
        )
        self._type_registrations[type_name] = registration

        # Index capabilities
        for capability in capabilities or []:
            if capability not in self._capability_index:
                self._capability_index[capability] = []
            self._capability_index[capability].append(f"type:{type_name}")

        self._logger.info(f"Registered agent type: {type_name}")

    def unregister_type(self, type_name: str) -> None:
        """Unregister an agent type.

        Args:
            type_name: Name of the agent type.

        Raises:
            AgentRegistrationError: If type not found.
        """
        if type_name not in self._type_registrations:
            raise AgentRegistrationError(
                f"Agent type '{type_name}' not found",
                agent_type=type_name,
            )

        # Remove from capability index
        registration = self._type_registrations[type_name]
        for capability in registration.capabilities:
            if capability in self._capability_index:
                self._capability_index[capability] = [
                    a for a in self._capability_index[capability]
                    if not a.startswith(f"type:{type_name}")
                ]

        del self._type_registrations[type_name]
        self._logger.info(f"Unregistered agent type: {type_name}")

    def get_type(self, type_name: str) -> AgentTypeRegistration:
        """Get an agent type registration.

        Args:
            type_name: Name of the agent type.

        Returns:
            AgentTypeRegistration: Type registration.

        Raises:
            AgentRegistrationError: If type not found.
        """
        if type_name not in self._type_registrations:
            raise AgentRegistrationError(
                f"Agent type '{type_name}' not found",
                agent_type=type_name,
            )
        return self._type_registrations[type_name]

    def list_types(self) -> List[AgentTypeRegistration]:
        """List all registered agent types.

        Returns:
            List[AgentTypeRegistration]: List of type registrations.
        """
        return list(self._type_registrations.values())

    def create_instance(
        self,
        type_name: str,
        agent_id: str,
        name: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> BaseAgent:
        """Create an agent instance.

        Args:
            type_name: Name of the agent type.
            agent_id: Agent instance ID.
            name: Agent name.
            config: Optional configuration.

        Returns:
            BaseAgent: Created agent instance.

        Raises:
            AgentRegistrationError: If type not found.
        """
        registration = self.get_type(type_name)
        agent = registration.agent_class(
            agent_id=agent_id,
            name=name,
            agent_type=type_name,
            config=config or {},
        )
        self._logger.info(f"Created agent instance: {name} ({agent_id})")
        return agent

    def register_instance(
        self,
        agent: BaseAgent,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register an agent instance.

        Args:
            agent: The agent instance.
            metadata: Optional metadata.

        Raises:
            AgentRegistrationError: If agent already registered.
        """
        if agent.agent_id in self._instances:
            raise AgentRegistrationError(
                f"Agent '{agent.agent_id}' is already registered",
                agent_id=agent.agent_id,
            )

        info = AgentInstanceInfo(
            agent_id=agent.agent_id,
            agent_type=agent.agent_type,
            name=agent.name,
            instance=agent,
            metadata=metadata or {},
        )
        self._instances[agent.agent_id] = info

        # Index capabilities
        capabilities = agent.get_capabilities()
        for capability in capabilities.get("skills", []):
            if capability not in self._capability_index:
                self._capability_index[capability] = []
            self._capability_index[capability].append(agent.agent_id)

        self._logger.info(f"Registered agent instance: {agent.name} ({agent.agent_id})")

    def unregister_instance(self, agent_id: str) -> None:
        """Unregister an agent instance.

        Args:
            agent_id: Agent instance ID.

        Raises:
            AgentRegistrationError: If agent not found.
        """
        if agent_id not in self._instances:
            raise AgentRegistrationError(
                f"Agent '{agent_id}' not found",
                agent_id=agent_id,
            )

        # Remove from capability index
        info = self._instances[agent_id]
        capabilities = info.instance.get_capabilities()
        for capability in capabilities.get("skills", []):
            if capability in self._capability_index:
                self._capability_index[capability] = [
                    a for a in self._capability_index[capability] if a != agent_id
                ]

        del self._instances[agent_id]
        self._logger.info(f"Unregistered agent instance: {agent_id}")

    def get_instance(self, agent_id: str) -> AgentInstanceInfo:
        """Get an agent instance info.

        Args:
            agent_id: Agent instance ID.

        Returns:
            AgentInstanceInfo: Instance info.

        Raises:
            AgentRegistrationError: If agent not found.
        """
        if agent_id not in self._instances:
            raise AgentRegistrationError(
                f"Agent '{agent_id}' not found",
                agent_id=agent_id,
            )
        return self._instances[agent_id]

    def get_agent(self, agent_id: str) -> BaseAgent:
        """Get an agent instance.

        Args:
            agent_id: Agent instance ID.

        Returns:
            BaseAgent: Agent instance.

        Raises:
            AgentRegistrationError: If agent not found.
        """
        info = self.get_instance(agent_id)
        return info.instance

    def list_instances(
        self,
        agent_type: Optional[str] = None,
        state: Optional[AgentState] = None,
    ) -> List[AgentInstanceInfo]:
        """List agent instances.

        Args:
            agent_type: Optional filter by type.
            state: Optional filter by state.

        Returns:
            List[AgentInstanceInfo]: List of instance infos.
        """
        instances = list(self._instances.values())

        if agent_type:
            instances = [i for i in instances if i.agent_type == agent_type]

        if state:
            instances = [i for i in instances if i.instance.state == state]

        return instances

    def find_by_capability(self, capability: str) -> List[BaseAgent]:
        """Find agents by capability.

        Args:
            capability: Capability to search for.

        Returns:
            List[BaseAgent]: List of matching agents.
        """
        agent_ids = self._capability_index.get(capability, [])
        agents = []

        for agent_id in agent_ids:
            if agent_id.startswith("type:"):
                continue  # Skip type registrations
            try:
                info = self.get_instance(agent_id)
                if info.instance.state == AgentState.IDLE:
                    agents.append(info.instance)
            except AgentError:
                pass

        return agents

    async def start_health_monitoring(self) -> None:
        """Start health monitoring background task."""
        if self._health_check_task is None:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._logger.info("Started health monitoring")

    async def stop_health_monitoring(self) -> None:
        """Stop health monitoring background task."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
            self._logger.info("Stopped health monitoring")

    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        while True:
            try:
                await asyncio.sleep(self._health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Health check error: {e}")

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all agents."""
        now = datetime.now(timezone.utc)
        unhealthy_agents = []

        for agent_id, info in self._instances.items():
            # Check heartbeat timeout
            heartbeat_age = (now - info.last_heartbeat).total_seconds()
            if heartbeat_age > self._heartbeat_timeout:
                unhealthy_agents.append(agent_id)
                self._logger.warning(
                    f"Agent {agent_id} heartbeat timeout ({heartbeat_age:.1f}s)"
                )

        # Handle unhealthy agents
        for agent_id in unhealthy_agents:
            try:
                info = self._instances[agent_id]
                if info.instance.state == AgentState.RUNNING:
                    self._logger.error(f"Marking unresponsive agent {agent_id} as error")
                    info.instance.status.set_error("Heartbeat timeout")
            except Exception as e:
                self._logger.error(f"Error handling unhealthy agent {agent_id}: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics.

        Returns:
            Dict: Registry statistics.
        """
        state_counts = {}
        type_counts = {}

        for info in self._instances.values():
            state = info.instance.state.value
            state_counts[state] = state_counts.get(state, 0) + 1

            agent_type = info.agent_type
            type_counts[agent_type] = type_counts.get(agent_type, 0) + 1

        return {
            "total_types": len(self._type_registrations),
            "total_instances": len(self._instances),
            "state_counts": state_counts,
            "type_counts": type_counts,
            "capability_count": len(self._capability_index),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary.

        Returns:
            Dict: Registry data.
        """
        return {
            "types": {
                name: reg.to_dict()
                for name, reg in self._type_registrations.items()
            },
            "instances": {
                agent_id: info.to_dict()
                for agent_id, info in self._instances.items()
            },
            "stats": self.get_stats(),
        }
