"""Tests for agent registry."""

import pytest
from typing import Dict, Any

from app.agents.core.base import BaseAgent
from app.agents.registry.agent_registry import AgentRegistry, AgentTypeRegistration
from app.agents.core.errors import AgentRegistrationError


class RegistryTestAgent(BaseAgent):
    """Test agent for registry tests."""

    def __init__(
        self,
        agent_id: str = "registry-test-1",
        name: str = "RegistryTestAgent",
        agent_type: str = "registry_test",
        config: Dict[str, Any] = None,
    ) -> None:
        super().__init__(agent_id, name, agent_type, config or {})

    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": "success"}

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "category": "test",
            "skills": ["testing", "registry"],
        }


class TestAgentRegistry:
    """Tests for AgentRegistry class."""

    def test_registry_creation(self) -> None:
        """Test registry creation."""
        registry = AgentRegistry()
        assert len(registry.list_types()) == 0
        assert len(registry.list_instances()) == 0

    def test_register_type(self) -> None:
        """Test agent type registration."""
        registry = AgentRegistry()

        registry.register_type(
            type_name="test_type",
            agent_class=RegistryTestAgent,
            description="Test agent type",
            capabilities={"skill1": "description1"},
        )

        types = registry.list_types()
        assert len(types) == 1
        assert types[0].type_name == "test_type"

    def test_register_duplicate_type(self) -> None:
        """Test duplicate type registration raises error."""
        registry = AgentRegistry()

        registry.register_type("test_type", RegistryTestAgent)

        with pytest.raises(AgentRegistrationError):
            registry.register_type("test_type", RegistryTestAgent)

    def test_unregister_type(self) -> None:
        """Test type unregistration."""
        registry = AgentRegistry()

        registry.register_type("test_type", RegistryTestAgent)
        registry.unregister_type("test_type")

        assert len(registry.list_types()) == 0

    def test_get_type(self) -> None:
        """Test getting a type."""
        registry = AgentRegistry()
        registry.register_type("test_type", RegistryTestAgent)

        reg = registry.get_type("test_type")
        assert isinstance(reg, AgentTypeRegistration)
        assert reg.agent_class == RegistryTestAgent

    def test_get_nonexistent_type(self) -> None:
        """Test getting nonexistent type raises error."""
        registry = AgentRegistry()

        with pytest.raises(AgentRegistrationError):
            registry.get_type("nonexistent")

    def test_create_instance(self) -> None:
        """Test creating agent instance."""
        registry = AgentRegistry()
        registry.register_type("test_type", RegistryTestAgent)

        agent = registry.create_instance(
            type_name="test_type",
            agent_id="test-1",
            name="Test Instance",
            config={"key": "value"},
        )

        assert agent.agent_id == "test-1"
        assert agent.name == "Test Instance"
        assert agent.agent_type == "test_type"
        assert agent.config == {"key": "value"}

    def test_register_instance(self) -> None:
        """Test instance registration."""
        registry = AgentRegistry()
        registry.register_type("test_type", RegistryTestAgent)

        agent = registry.create_instance("test_type", "test-1", "Test")
        registry.register_instance(agent)

        instances = registry.list_instances()
        assert len(instances) == 1
        assert instances[0].agent_id == "test-1"

    def test_unregister_instance(self) -> None:
        """Test instance unregistration."""
        registry = AgentRegistry()
        registry.register_type("test_type", RegistryTestAgent)

        agent = registry.create_instance("test_type", "test-1", "Test")
        registry.register_instance(agent)
        registry.unregister_instance("test-1")

        assert len(registry.list_instances()) == 0

    def test_get_agent(self) -> None:
        """Test getting registered agent."""
        registry = AgentRegistry()
        registry.register_type("test_type", RegistryTestAgent)

        agent = registry.create_instance("test_type", "test-1", "Test")
        registry.register_instance(agent)

        retrieved = registry.get_agent("test-1")
        assert retrieved.agent_id == "test-1"
        assert retrieved.name == "Test"

    def test_list_instances_by_type(self) -> None:
        """Test listing instances filtered by type."""
        registry = AgentRegistry()
        registry.register_type("type1", RegistryTestAgent)
        registry.register_type("type2", RegistryTestAgent)

        agent1 = registry.create_instance("type1", "test-1", "Test1")
        agent2 = registry.create_instance("type2", "test-2", "Test2")

        registry.register_instance(agent1)
        registry.register_instance(agent2)

        type1_instances = registry.list_instances(agent_type="type1")
        assert len(type1_instances) == 1
        assert type1_instances[0].agent_type == "type1"

    def test_find_by_capability(self) -> None:
        """Test finding agents by capability."""
        registry = AgentRegistry()
        registry.register_type("test_type", RegistryTestAgent)

        agent = registry.create_instance("test_type", "test-1", "Test")
        registry.register_instance(agent)

        # Find by capability
        agents = registry.find_by_capability("testing")
        assert len(agents) == 1
        assert agents[0].agent_id == "test-1"

    def test_registry_stats(self) -> None:
        """Test registry statistics."""
        registry = AgentRegistry()
        registry.register_type("test_type", RegistryTestAgent)

        agent = registry.create_instance("test_type", "test-1", "Test")
        registry.register_instance(agent)

        stats = registry.get_stats()
        assert stats["total_types"] == 1
        assert stats["total_instances"] == 1

    def test_registry_to_dict(self) -> None:
        """Test registry serialization."""
        registry = AgentRegistry()
        registry.register_type("test_type", RegistryTestAgent)

        data = registry.to_dict()
        assert "types" in data
        assert "instances" in data
        assert "stats" in data
