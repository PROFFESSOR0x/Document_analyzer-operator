"""Tests for agent orchestrator."""

import pytest
import asyncio

from app.agents.orchestration.orchestrator import AgentOrchestrator
from app.agents.orchestration.load_balancer import LoadBalancer, LoadBalancingStrategy
from app.agents.orchestration.task_assigner import TaskAssigner, Task, TaskStatus


class TestLoadBalancer:
    """Tests for LoadBalancer class."""

    def test_load_balancer_creation(self) -> None:
        """Test load balancer creation."""
        from app.agents.registry.agent_registry import AgentRegistry
        registry = AgentRegistry()
        balancer = LoadBalancer(registry)
        assert balancer._strategy == LoadBalancingStrategy.ROUND_ROBIN

    def test_set_strategy(self) -> None:
        """Test setting strategy."""
        from app.agents.registry.agent_registry import AgentRegistry
        registry = AgentRegistry()
        balancer = LoadBalancer(registry)

        balancer.set_strategy(LoadBalancingStrategy.LEAST_BUSY)
        assert balancer._strategy == LoadBalancingStrategy.LEAST_BUSY

    def test_select_agent_no_agents(self) -> None:
        """Test selecting agent when none available."""
        from app.agents.registry.agent_registry import AgentRegistry
        registry = AgentRegistry()
        balancer = LoadBalancer(registry)

        agent = balancer.select_agent()
        assert agent is None


class TestTaskAssigner:
    """Tests for TaskAssigner class."""

    def test_task_creation(self) -> None:
        """Test task creation."""
        task = Task(type="test", payload={"data": "value"})
        assert task.type == "test"
        assert task.status == TaskStatus.PENDING
        assert task.payload == {"data": "value"}

    def test_task_to_dict(self) -> None:
        """Test task serialization."""
        task = Task(type="test", payload={"key": "value"})
        data = task.to_dict()

        assert data["type"] == "test"
        assert data["status"] == "pending"
        assert "id" in data

    def test_task_assigner_creation(self) -> None:
        """Test task assigner creation."""
        from app.agents.registry.agent_registry import AgentRegistry
        registry = AgentRegistry()
        assigner = TaskAssigner(registry)
        assert assigner._max_concurrent_tasks == 100


class TestAgentOrchestrator:
    """Tests for AgentOrchestrator class."""

    def test_orchestrator_creation(self) -> None:
        """Test orchestrator creation."""
        orchestrator = AgentOrchestrator()
        assert orchestrator._running is False
        assert orchestrator.registry is not None
        assert orchestrator.factory is not None
        assert orchestrator.load_balancer is not None
        assert orchestrator.task_assigner is not None

    def test_register_agent_type(self) -> None:
        """Test registering agent type through orchestrator."""
        from app.agents.types.cognitive.base import BaseCognitiveAgent
        from typing import Dict, Any

        class TestAgent(BaseCognitiveAgent):
            async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
                return {}
            def get_capabilities(self) -> Dict[str, Any]:
                return {"category": "test", "skills": []}

        orchestrator = AgentOrchestrator()
        orchestrator.register_agent_type("test", TestAgent)

        types = orchestrator.registry.list_types()
        assert len(types) == 1
        assert types[0].type_name == "test"

    def test_create_agent(self) -> None:
        """Test creating agent through orchestrator."""
        from app.agents.types.cognitive.base import BaseCognitiveAgent
        from typing import Dict, Any

        class TestAgent(BaseCognitiveAgent):
            async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
                return {}
            def get_capabilities(self) -> Dict[str, Any]:
                return {"category": "test", "skills": []}

        orchestrator = AgentOrchestrator()
        orchestrator.register_agent_type("test", TestAgent)

        agent = orchestrator.create_agent("test", name="TestAgent")
        assert agent.name == "TestAgent"
        assert agent.agent_type == "test"

    def test_get_status(self) -> None:
        """Test getting orchestrator status."""
        orchestrator = AgentOrchestrator()
        status = orchestrator.get_status()

        assert "running" in status
        assert "registry" in status
        assert "task_assigner" in status
        assert "load_balancer" in status

    def test_get_health(self) -> None:
        """Test getting orchestrator health."""
        orchestrator = AgentOrchestrator()
        health = orchestrator.get_health()

        assert "overall_health" in health
        assert "agent_health" in health
        assert "task_health" in health

    @pytest.mark.asyncio
    async def test_orchestrator_lifecycle(self) -> None:
        """Test orchestrator lifecycle."""
        orchestrator = AgentOrchestrator()

        # Initialize
        await orchestrator.initialize()
        assert orchestrator._running is True

        # Shutdown
        await orchestrator.shutdown()
        assert orchestrator._running is False

    def test_collaboration_groups(self) -> None:
        """Test collaboration groups."""
        orchestrator = AgentOrchestrator()

        # Create group
        orchestrator.create_collaboration_group("test_group", ["agent1", "agent2"])
        assert "test_group" in orchestrator._collaboration_groups

        # Add to group
        orchestrator.add_to_collaboration_group("test_group", "agent3")
        assert len(orchestrator._collaboration_groups["test_group"]) == 3

        # Remove from group
        orchestrator.remove_from_collaboration_group("test_group", "agent2")
        assert "agent2" not in orchestrator._collaboration_groups["test_group"]

    def test_scaling_configuration(self) -> None:
        """Test scaling configuration."""
        orchestrator = AgentOrchestrator()

        orchestrator.configure_scaling("test_type", min_agents=2, max_agents=10)
        assert orchestrator._min_agents["test_type"] == 2
        assert orchestrator._max_agents["test_type"] == 10
