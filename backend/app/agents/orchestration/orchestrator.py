"""Main agent orchestrator for coordinating multi-agent operations."""

from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime, timezone
import asyncio
import logging
from uuid import uuid4

from app.agents.core.base import BaseAgent
from app.agents.core.states import AgentState
from app.agents.core.messages import EventMessage, AgentMessage
from app.agents.registry.agent_registry import AgentRegistry
from app.agents.registry.agent_factory import AgentFactory
from app.agents.orchestration.load_balancer import LoadBalancer, LoadBalancingStrategy
from app.agents.orchestration.task_assigner import TaskAssigner, Task, TaskStatus


class AgentOrchestrator:
    """Main orchestrator for coordinating multi-agent operations.

    This class provides:
    - Task assignment logic
    - Load balancing across agents
    - Agent scaling decisions
    - Failure recovery strategies
    - Agent collaboration patterns
    - Event publishing/subscribing

    Usage:
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        await orchestrator.submit_task(task)
        await orchestrator.shutdown()
    """

    def __init__(
        self,
        max_concurrent_tasks: int = 100,
        load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN,
    ) -> None:
        """Initialize agent orchestrator.

        Args:
            max_concurrent_tasks: Maximum concurrent tasks.
            load_balancing_strategy: Load balancing strategy.
        """
        self._registry = AgentRegistry()
        self._factory = AgentFactory(self._registry)
        self._load_balancer = LoadBalancer(
            self._registry,
            strategy=load_balancing_strategy,
        )
        self._task_assigner = TaskAssigner(
            self._registry,
            self._load_balancer,
            max_concurrent_tasks=max_concurrent_tasks,
        )

        self._logger = logging.getLogger("agent.orchestrator")

        # Event subscribers
        self._event_subscribers: Dict[str, List[Callable[[EventMessage], Awaitable[None]]]] = {}

        # Agent collaboration groups
        self._collaboration_groups: Dict[str, List[str]] = {}  # group_name -> [agent_ids]

        # Scaling configuration
        self._min_agents: Dict[str, int] = {}
        self._max_agents: Dict[str, int] = {}
        self._scale_up_threshold = 0.8  # 80% utilization
        self._scale_down_threshold = 0.2  # 20% utilization

        # Running state
        self._running = False
        self._scaling_task: Optional[asyncio.Task] = None

        self._logger.info("Agent orchestrator initialized")

    @property
    def registry(self) -> AgentRegistry:
        """Get agent registry.

        Returns:
            AgentRegistry: Registry instance.
        """
        return self._registry

    @property
    def factory(self) -> AgentFactory:
        """Get agent factory.

        Returns:
            AgentFactory: Factory instance.
        """
        return self._factory

    @property
    def load_balancer(self) -> LoadBalancer:
        """Get load balancer.

        Returns:
            LoadBalancer: Load balancer instance.
        """
        return self._load_balancer

    @property
    def task_assigner(self) -> TaskAssigner:
        """Get task assigner.

        Returns:
            TaskAssigner: Task assigner instance.
        """
        return self._task_assigner

    async def initialize(self) -> None:
        """Initialize the orchestrator."""
        self._running = True
        await self._task_assigner.start()
        await self._registry.start_health_monitoring()
        self._scaling_task = asyncio.create_task(self._scaling_loop())
        self._logger.info("Agent orchestrator initialized and running")

    async def shutdown(self) -> None:
        """Shutdown the orchestrator."""
        self._running = False

        await self._task_assigner.stop()
        await self._registry.stop_health_monitoring()

        if self._scaling_task:
            self._scaling_task.cancel()
            try:
                await self._scaling_task
            except asyncio.CancelledError:
                pass

        # Stop all agents
        for info in self._registry.list_instances():
            try:
                await info.instance.terminate()
            except Exception as e:
                self._logger.error(f"Error terminating agent {info.agent_id}: {e}")

        self._logger.info("Agent orchestrator shutdown complete")

    # ========== Task Management ==========

    async def submit_task(self, task: Task) -> str:
        """Submit a task for execution.

        Args:
            task: Task to submit.

        Returns:
            str: Task ID.
        """
        return await self._task_assigner.submit_task(task)

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task immediately.

        Args:
            task: Task to execute.

        Returns:
            Dict: Task result.
        """
        return await self._task_assigner.execute_task(task)

    async def execute_on_agent(
        self,
        agent_id: str,
        task_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a task on a specific agent.

        Args:
            agent_id: Target agent ID.
            task_payload: Task data.

        Returns:
            Dict: Task result.
        """
        agent = self._registry.get_agent(agent_id)
        return await agent.execute(task_payload)

    # ========== Agent Management ==========

    def register_agent_type(self, *args, **kwargs) -> None:
        """Register an agent type.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        self._registry.register_type(*args, **kwargs)

    def create_agent(
        self,
        agent_type: str,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        initialize: bool = True,
    ) -> BaseAgent:
        """Create an agent.

        Args:
            agent_type: Type of agent.
            name: Optional agent name.
            config: Optional configuration.
            initialize: Whether to initialize.

        Returns:
            BaseAgent: Created agent.
        """
        return self._factory.create_custom(
            agent_type=agent_type,
            name=name,
            config=config,
            initialize=initialize,
        )

    async def start_agent(self, agent_id: str) -> None:
        """Start an agent.

        Args:
            agent_id: Agent ID.
        """
        agent = self._registry.get_agent(agent_id)
        await agent.start()

    async def stop_agent(self, agent_id: str) -> None:
        """Stop an agent.

        Args:
            agent_id: Agent ID.
        """
        agent = self._registry.get_agent(agent_id)
        await agent.stop()

    async def remove_agent(self, agent_id: str) -> None:
        """Remove an agent.

        Args:
            agent_id: Agent ID.
        """
        agent = self._registry.get_agent(agent_id)
        await agent.terminate()
        self._registry.unregister_instance(agent_id)

    # ========== Scaling ==========

    def configure_scaling(
        self,
        agent_type: str,
        min_agents: int = 1,
        max_agents: int = 10,
    ) -> None:
        """Configure auto-scaling for an agent type.

        Args:
            agent_type: Type of agent.
            min_agents: Minimum number of agents.
            max_agents: Maximum number of agents.
        """
        self._min_agents[agent_type] = min_agents
        self._max_agents[agent_type] = max_agents
        self._logger.info(
            f"Configured scaling for {agent_type}: min={min_agents}, max={max_agents}"
        )

    async def _scaling_loop(self) -> None:
        """Background scaling loop."""
        while self._running:
            try:
                await asyncio.sleep(30.0)  # Check every 30 seconds
                await self._perform_scaling()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Scaling loop error: {e}")

    async def _perform_scaling(self) -> None:
        """Perform auto-scaling decisions."""
        for agent_type, max_agents in self._max_agents.items():
            instances = self._registry.list_instances(agent_type=agent_type)
            idle_count = sum(1 for i in instances if i.instance.state == AgentState.IDLE)
            total_count = len(instances)

            # Calculate utilization
            if max_agents > 0:
                utilization = total_count / max_agents

                # Scale up
                if utilization > self._scale_up_threshold and total_count < max_agents:
                    await self._scale_up(agent_type)

                # Scale down
                elif utilization < self._scale_down_threshold and total_count > self._min_agents.get(agent_type, 1):
                    await self._scale_down(agent_type)

    async def _scale_up(self, agent_type: str) -> None:
        """Scale up agents of a type.

        Args:
            agent_type: Type of agent.
        """
        try:
            agent = self.create_agent(agent_type, initialize=True)
            self._registry.register_instance(agent)
            await agent.start()
            self._logger.info(f"Scaled up agent type {agent_type}")
        except Exception as e:
            self._logger.error(f"Failed to scale up {agent_type}: {e}")

    async def _scale_down(self, agent_type: str) -> None:
        """Scale down agents of a type.

        Args:
            agent_type: Type of agent.
        """
        instances = self._registry.list_instances(agent_type=agent_type)
        idle_instances = [i for i in instances if i.instance.state == AgentState.IDLE]

        if idle_instances:
            # Remove oldest idle agent
            agent_to_remove = idle_instances[0]
            try:
                await agent_to_remove.instance.terminate()
                self._registry.unregister_instance(agent_to_remove.agent_id)
                self._logger.info(f"Scaled down agent type {agent_type}")
            except Exception as e:
                self._logger.error(f"Failed to scale down {agent_type}: {e}")

    # ========== Collaboration ==========

    def create_collaboration_group(self, name: str, agent_ids: List[str]) -> None:
        """Create a collaboration group.

        Args:
            name: Group name.
            agent_ids: Agent IDs in the group.
        """
        self._collaboration_groups[name] = agent_ids
        self._logger.info(f"Created collaboration group '{name}' with {len(agent_ids)} agents")

    def add_to_collaboration_group(self, name: str, agent_id: str) -> None:
        """Add an agent to a collaboration group.

        Args:
            name: Group name.
            agent_id: Agent ID.
        """
        if name not in self._collaboration_groups:
            self._collaboration_groups[name] = []
        self._collaboration_groups[name].append(agent_id)

    def remove_from_collaboration_group(self, name: str, agent_id: str) -> None:
        """Remove an agent from a collaboration group.

        Args:
            name: Group name.
            agent_id: Agent ID.
        """
        if name in self._collaboration_groups:
            self._collaboration_groups[name] = [
                a for a in self._collaboration_groups[name] if a != agent_id
            ]

    async def broadcast_to_group(
        self,
        group_name: str,
        event: EventMessage,
    ) -> int:
        """Broadcast an event to a collaboration group.

        Args:
            group_name: Group name.
            event: Event to broadcast.

        Returns:
            int: Number of agents notified.
        """
        agent_ids = self._collaboration_groups.get(group_name, [])
        sent_count = 0

        for agent_id in agent_ids:
            try:
                agent = self._registry.get_agent(agent_id)
                await agent.send_message(event)
                sent_count += 1
            except Exception:
                pass

        return sent_count

    # ========== Event System ==========

    def subscribe(
        self,
        event_type: str,
        callback: Callable[[EventMessage], Awaitable[None]],
    ) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Event type.
            callback: Callback function.
        """
        if event_type not in self._event_subscribers:
            self._event_subscribers[event_type] = []
        self._event_subscribers[event_type].append(callback)

    def unsubscribe(
        self,
        event_type: str,
        callback: Callable[[EventMessage], Awaitable[None]],
    ) -> None:
        """Unsubscribe from an event type.

        Args:
            event_type: Event type.
            callback: Callback function.
        """
        if event_type in self._event_subscribers:
            self._event_subscribers[event_type] = [
                c for c in self._event_subscribers[event_type] if c != callback
            ]

    async def publish_event(self, event: EventMessage) -> int:
        """Publish an event.

        Args:
            event: Event to publish.

        Returns:
            int: Number of subscribers notified.
        """
        callbacks = self._event_subscribers.get(event.event_name, [])
        notified = 0

        for callback in callbacks:
            try:
                await callback(event)
                notified += 1
            except Exception as e:
                self._logger.error(f"Error notifying event subscriber: {e}")

        return notified

    # ========== Status and Monitoring ==========

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status.

        Returns:
            Dict: Status data.
        """
        return {
            "running": self._running,
            "registry": self._registry.to_dict(),
            "task_assigner": self._task_assigner.to_dict(),
            "load_balancer": self._load_balancer.to_dict(),
            "collaboration_groups": list(self._collaboration_groups.keys()),
            "scaling_config": {
                "min_agents": self._min_agents,
                "max_agents": self._max_agents,
            },
        }

    def get_health(self) -> Dict[str, Any]:
        """Get orchestrator health.

        Returns:
            Dict: Health data.
        """
        registry_stats = self._registry.get_stats()
        task_stats = self._task_assigner.get_stats()

        # Calculate overall health
        healthy_agents = registry_stats["state_counts"].get("idle", 0) + \
                        registry_stats["state_counts"].get("running", 0)
        total_agents = registry_stats["total_instances"]
        agent_health = (healthy_agents / total_agents * 100) if total_agents > 0 else 100

        failed_tasks = task_stats["status_counts"].get("failed", 0) + \
                      task_stats["status_counts"].get("timeout", 0)
        total_tasks = sum(task_stats["status_counts"].values())
        task_health = 100 - (failed_tasks / total_tasks * 100) if total_tasks > 0 else 100

        overall_health = (agent_health + task_health) / 2

        return {
            "overall_health": round(overall_health, 2),
            "agent_health": round(agent_health, 2),
            "task_health": round(task_health, 2),
            "total_agents": total_agents,
            "healthy_agents": healthy_agents,
            "active_tasks": task_stats["active_tasks"],
            "queue_size": task_stats["queue_size"],
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            str: Orchestrator representation.
        """
        return f"<AgentOrchestrator running={self._running}>"
