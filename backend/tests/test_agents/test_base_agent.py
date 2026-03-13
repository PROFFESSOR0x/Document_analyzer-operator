"""Tests for base agent functionality."""

import pytest
import asyncio
from typing import Dict, Any

from app.agents.core.base import BaseAgent
from app.agents.core.states import AgentState, AgentLifecycleState
from app.agents.core.messages import RequestMessage, ResponseMessage, EventMessage
from app.agents.core.errors import AgentStateError, AgentExecutionError


class TestAgent(BaseAgent):
    """Test agent implementation."""

    def __init__(
        self,
        agent_id: str = "test-agent-1",
        name: str = "TestAgent",
        agent_type: str = "test",
        config: Dict[str, Any] = None,
    ) -> None:
        super().__init__(agent_id, name, agent_type, config or {})

    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test task."""
        await asyncio.sleep(0.01)  # Simulate work
        return {"result": "success", "task": task}

    def get_capabilities(self) -> Dict[str, Any]:
        """Get capabilities."""
        return {
            "category": "test",
            "skills": ["testing", "validation"],
        }


class TestBaseAgent:
    """Tests for BaseAgent class."""

    def test_agent_creation(self) -> None:
        """Test agent creation."""
        agent = TestAgent()
        assert agent.agent_id == "test-agent-1"
        assert agent.name == "TestAgent"
        assert agent.agent_type == "test"
        assert agent.state == AgentState.IDLE
        assert agent.lifecycle_state == AgentLifecycleState.CREATED

    def test_agent_initialization(self) -> None:
        """Test agent initialization."""
        agent = TestAgent()
        assert agent.lifecycle_state == AgentLifecycleState.CREATED

    @pytest.mark.asyncio
    async def test_agent_lifecycle(self) -> None:
        """Test agent lifecycle."""
        agent = TestAgent()

        # Initialize
        await agent.initialize()
        assert agent.lifecycle_state == AgentLifecycleState.INITIALIZED
        assert agent.state == AgentState.IDLE

        # Start
        await agent.start()
        assert agent.lifecycle_state == AgentLifecycleState.STARTED
        assert agent.state == AgentState.RUNNING

        # Execute task
        result = await agent.execute({"type": "test"})
        assert result["result"] == "success"

        # Pause
        await agent.pause()
        assert agent.state == AgentState.PAUSED

        # Resume
        await agent.resume()
        assert agent.state == AgentState.RUNNING

        # Stop
        await agent.stop()
        assert agent.lifecycle_state == AgentLifecycleState.STOPPED
        assert agent.state == AgentState.STOPPED

        # Terminate
        await agent.terminate()
        assert agent.lifecycle_state == AgentLifecycleState.TERMINATED

    @pytest.mark.asyncio
    async def test_agent_state_transitions(self) -> None:
        """Test state transition validation."""
        agent = TestAgent()

        # Cannot execute before initialization
        with pytest.raises(AgentStateError):
            await agent.execute({"type": "test"})

        # Initialize first
        await agent.initialize()

        # Cannot pause before starting
        with pytest.raises(AgentStateError):
            await agent.pause()

        # Start
        await agent.start()

        # Cannot start again
        with pytest.raises(AgentStateError):
            await agent.start()

    @pytest.mark.asyncio
    async def test_agent_telemetry(self) -> None:
        """Test telemetry collection."""
        agent = TestAgent()
        await agent.initialize()
        await agent.start()

        # Execute multiple tasks
        for i in range(5):
            await agent.execute({"type": "test", "iteration": i})

        # Check metrics
        metrics = agent.telemetry.metrics
        assert metrics.execution_count == 5
        assert metrics.success_count == 5
        assert metrics.success_rate == 100.0

    @pytest.mark.asyncio
    async def test_agent_message_handling(self) -> None:
        """Test message handling."""
        agent = TestAgent()
        await agent.initialize()

        # Send message
        msg = RequestMessage(
            receiver_id="target-agent",
            payload={"test": "data"},
        )
        await agent.send_message(msg)

        # Receive message
        received = await agent.receive_message(timeout=0.1)
        assert received is None  # Queue was empty

    @pytest.mark.asyncio
    async def test_agent_event_publishing(self) -> None:
        """Test event publishing."""
        agent = TestAgent()
        await agent.initialize()

        # Send event
        await agent.send_event(
            event_name="test_event",
            payload={"data": "value"},
            broadcast=True,
        )

        # Check outgoing queue
        msg = await agent.receive_message(timeout=0.1)
        assert msg is None  # Events go to outgoing queue

    def test_agent_info(self) -> None:
        """Test agent info retrieval."""
        agent = TestAgent()
        info = agent.get_info()

        assert info["agent_id"] == "test-agent-1"
        assert info["name"] == "TestAgent"
        assert info["agent_type"] == "test"
        assert "capabilities" in info
        assert "telemetry" in info

    def test_agent_repr(self) -> None:
        """Test agent string representation."""
        agent = TestAgent()
        repr_str = repr(agent)
        assert "TestAgent" in repr_str
        assert "test-agent-1" in repr_str

    @pytest.mark.asyncio
    async def test_agent_cancellation(self) -> None:
        """Test task cancellation."""
        agent = TestAgent()
        await agent.initialize()
        await agent.start()

        # Set cancel event
        agent._cancel_event.set()

        # Task should still complete (cancellation is cooperative)
        result = await agent.execute({"type": "test"})
        assert result["result"] == "success"
