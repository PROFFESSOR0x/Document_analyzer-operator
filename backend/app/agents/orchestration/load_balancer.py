"""Load balancer for distributing tasks across agents."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum
import logging

from app.agents.core.base import BaseAgent
from app.agents.core.states import AgentState
from app.agents.registry.agent_registry import AgentRegistry
from app.agents.registry.agent_registry import AgentInstanceInfo


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies.

    Attributes:
        ROUND_ROBIN: Distribute tasks evenly across agents.
        LEAST_BUSY: Send to agent with fewest active tasks.
        FASTEST: Send to agent with best performance metrics.
        CAPABILITY_BASED: Send to agent with best matching capabilities.
        WEIGHTED: Distribute based on agent weights.
    """

    ROUND_ROBIN = "round_robin"
    LEAST_BUSY = "least_busy"
    FASTEST = "fastest"
    CAPABILITY_BASED = "capability_based"
    WEIGHTED = "weighted"


class LoadBalancer:
    """Load balancer for distributing tasks across agents.

    This class provides:
    - Multiple load balancing strategies
    - Agent health-aware routing
    - Performance-based routing
    - Sticky sessions support

    Usage:
        balancer = LoadBalancer(registry, strategy=LoadBalancingStrategy.ROUND_ROBIN)
        agent = balancer.select_agent("analyzer", task)
    """

    def __init__(
        self,
        registry: AgentRegistry,
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN,
    ) -> None:
        """Initialize load balancer.

        Args:
            registry: Agent registry.
            strategy: Load balancing strategy.
        """
        self._registry = registry
        self._strategy = strategy
        self._logger = logging.getLogger("agent.load_balancer")

        # Round-robin state
        self._rr_index = 0
        self._rr_agents: List[str] = []

        # Weights for weighted strategy
        self._weights: Dict[str, int] = {}

        # Sticky sessions
        self._sticky_sessions: Dict[str, str] = {}  # session_id -> agent_id

        self._logger.info(f"Load balancer initialized with strategy: {strategy.value}")

    def set_strategy(self, strategy: LoadBalancingStrategy) -> None:
        """Set load balancing strategy.

        Args:
            strategy: New strategy.
        """
        self._strategy = strategy
        self._logger.info(f"Load balancing strategy changed to: {strategy.value}")

    def set_weight(self, agent_id: str, weight: int) -> None:
        """Set agent weight for weighted load balancing.

        Args:
            agent_id: Agent ID.
            weight: Agent weight (higher = more tasks).
        """
        self._weights[agent_id] = weight
        self._logger.debug(f"Set weight for agent {agent_id}: {weight}")

    def enable_sticky_session(self, session_id: str, agent_id: str) -> None:
        """Enable sticky session for a session.

        Args:
            session_id: Session ID.
            agent_id: Agent ID to stick to.
        """
        self._sticky_sessions[session_id] = agent_id
        self._logger.debug(f"Sticky session enabled: {session_id} -> {agent_id}")

    def disable_sticky_session(self, session_id: str) -> None:
        """Disable sticky session.

        Args:
            session_id: Session ID.
        """
        if session_id in self._sticky_sessions:
            del self._sticky_sessions[session_id]
            self._logger.debug(f"Sticky session disabled: {session_id}")

    def select_agent(
        self,
        agent_type: Optional[str] = None,
        task: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        required_capabilities: Optional[List[str]] = None,
    ) -> Optional[BaseAgent]:
        """Select an agent based on the configured strategy.

        Args:
            agent_type: Optional filter by agent type.
            task: Optional task data for capability-based routing.
            session_id: Optional session ID for sticky sessions.
            required_capabilities: Optional required capabilities.

        Returns:
            Optional[BaseAgent]: Selected agent or None.
        """
        # Check sticky session
        if session_id and session_id in self._sticky_sessions:
            try:
                agent = self._registry.get_agent(self._sticky_sessions[session_id])
                if agent.state == AgentState.IDLE:
                    return agent
            except Exception:
                pass  # Fall through to normal selection

        # Get available agents
        agents = self._get_available_agents(
            agent_type=agent_type,
            required_capabilities=required_capabilities,
        )

        if not agents:
            return None

        # Select based on strategy
        if self._strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._select_round_robin(agents)
        elif self._strategy == LoadBalancingStrategy.LEAST_BUSY:
            return self._select_least_busy(agents)
        elif self._strategy == LoadBalancingStrategy.FASTEST:
            return self._select_fastest(agents)
        elif self._strategy == LoadBalancingStrategy.CAPABILITY_BASED:
            return self._select_capability_based(agents, task)
        elif self._strategy == LoadBalancingStrategy.WEIGHTED:
            return self._select_weighted(agents)

        return None

    def _get_available_agents(
        self,
        agent_type: Optional[str] = None,
        required_capabilities: Optional[List[str]] = None,
    ) -> List[AgentInstanceInfo]:
        """Get available agents.

        Args:
            agent_type: Optional filter by type.
            required_capabilities: Optional required capabilities.

        Returns:
            List[AgentInstanceInfo]: Available agents.
        """
        instances = self._registry.list_instances(state=AgentState.IDLE)

        if agent_type:
            instances = [i for i in instances if i.agent_type == agent_type]

        if required_capabilities:
            filtered = []
            for info in instances:
                capabilities = info.instance.get_capabilities()
                skills = capabilities.get("skills", [])
                if all(cap in skills for cap in required_capabilities):
                    filtered.append(info)
            instances = filtered

        return instances

    def _select_round_robin(self, agents: List[AgentInstanceInfo]) -> BaseAgent:
        """Select agent using round-robin strategy.

        Args:
            agents: Available agents.

        Returns:
            BaseAgent: Selected agent.
        """
        if not agents:
            raise ValueError("No agents available")

        # Update agent list if changed
        current_agents = [a.agent_id for a in agents]
        if current_agents != self._rr_agents:
            self._rr_agents = current_agents
            self._rr_index = 0

        # Select next agent
        agent_info = agents[self._rr_index % len(agents)]
        self._rr_index = (self._rr_index + 1) % len(agents)

        self._logger.debug(f"Round-robin selected agent: {agent_info.agent_id}")
        return agent_info.instance

    def _select_least_busy(self, agents: List[AgentInstanceInfo]) -> BaseAgent:
        """Select agent with least active tasks.

        Args:
            agents: Available agents.

        Returns:
            BaseAgent: Selected agent.
        """
        if not agents:
            raise ValueError("No agents available")

        # All idle agents have 0 active tasks, so pick one with best health
        best_agent = max(
            agents,
            key=lambda a: a.instance.telemetry.get_health_score(),
        )

        self._logger.debug(f"Least-busy selected agent: {best_agent.agent_id}")
        return best_agent.instance

    def _select_fastest(self, agents: List[AgentInstanceInfo]) -> BaseAgent:
        """Select agent with best performance.

        Args:
            agents: Available agents.

        Returns:
            BaseAgent: Selected agent.
        """
        if not agents:
            raise ValueError("No agents available")

        # Select agent with lowest average execution time
        def get_avg_time(info: AgentInstanceInfo) -> float:
            metrics = info.instance.telemetry.metrics
            if metrics.execution_count == 0:
                return float("inf")
            return metrics.avg_execution_time_ms

        best_agent = min(agents, key=get_avg_time)

        self._logger.debug(f"Fastest selected agent: {best_agent.agent_id}")
        return best_agent.instance

    def _select_capability_based(
        self,
        agents: List[AgentInstanceInfo],
        task: Optional[Dict[str, Any]],
    ) -> BaseAgent:
        """Select agent based on task capabilities.

        Args:
            agents: Available agents.
            task: Task data.

        Returns:
            BaseAgent: Selected agent.
        """
        if not agents:
            raise ValueError("No agents available")

        if not task:
            return agents[0].instance

        # Get required capabilities from task
        required = task.get("required_capabilities", [])
        if not required:
            return agents[0].instance

        # Score agents by capability match
        def score_agent(info: AgentInstanceInfo) -> int:
            capabilities = info.instance.get_capabilities()
            skills = set(capabilities.get("skills", []))
            return len(set(required) & skills)

        best_agent = max(agents, key=score_agent)

        self._logger.debug(f"Capability-based selected agent: {best_agent.agent_id}")
        return best_agent.instance

    def _select_weighted(self, agents: List[AgentInstanceInfo]) -> BaseAgent:
        """Select agent using weighted distribution.

        Args:
            agents: Available agents.

        Returns:
            BaseAgent: Selected agent.
        """
        if not agents:
            raise ValueError("No agents available")

        # Get weights
        weights = []
        for info in agents:
            weight = self._weights.get(info.agent_id, 1)
            weights.append(weight)

        # Simple weighted selection (could use more sophisticated algorithm)
        total_weight = sum(weights)
        if total_weight == 0:
            return agents[0].instance

        # Select based on weight proportion
        import random
        r = random.uniform(0, total_weight)
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                self._logger.debug(f"Weighted selected agent: {agents[i].agent_id}")
                return agents[i].instance

        return agents[-1].instance

    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics.

        Returns:
            Dict: Statistics.
        """
        instances = self._registry.list_instances()
        idle_count = sum(1 for i in instances if i.instance.state == AgentState.IDLE)
        running_count = sum(1 for i in instances if i.instance.state == AgentState.RUNNING)

        return {
            "strategy": self._strategy.value,
            "total_agents": len(instances),
            "idle_agents": idle_count,
            "running_agents": running_count,
            "sticky_sessions": len(self._sticky_sessions),
            "weighted_agents": len(self._weights),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert load balancer to dictionary.

        Returns:
            Dict: Load balancer data.
        """
        return {
            "strategy": self._strategy.value,
            "stats": self.get_stats(),
            "weights": self._weights.copy(),
            "sticky_sessions": self._sticky_sessions.copy(),
        }
