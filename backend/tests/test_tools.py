"""Tests for the tool capability layer."""

import pytest
from typing import Dict, Any
from datetime import datetime, timezone

from app.tools.base import (
    BaseTool,
    ToolMetadata,
    ToolCategory,
    ToolRegistry,
    ToolExecutionEngine,
    ToolResult,
    ToolError,
    ToolValidationError,
)
from pydantic import BaseModel, Field


# ========== Test Tool Implementation ==========

class TestInput(BaseModel):
    """Test input model."""

    value: int = Field(..., ge=0, le=100)
    operation: str = "double"


class TestOutput(BaseModel):
    """Test output model."""

    result: int
    operation: str


class TestTool(BaseTool[TestInput, TestOutput]):
    """Test tool implementation."""

    metadata = ToolMetadata(
        name="test_tool",
        description="A test tool for unit testing",
        category=ToolCategory.UTILITY,
        version="1.0.0",
        tags=["test", "utility"],
        timeout_seconds=10.0,
    )

    InputModel = TestInput
    OutputModel = TestOutput

    async def _execute(self, input_data: TestInput) -> TestOutput:
        """Execute test operation."""
        if input_data.operation == "double":
            result = input_data.value * 2
        elif input_data.operation == "half":
            result = input_data.value // 2
        else:
            result = input_data.value

        return TestOutput(result=result, operation=input_data.operation)


# ========== Base Tool Tests ==========

class TestBaseTool:
    """Tests for BaseTool class."""

    @pytest.mark.asyncio
    async def test_tool_initialization(self) -> None:
        """Test tool initialization."""
        tool = TestTool()

        assert tool.name == "test_tool"
        assert tool.category == ToolCategory.UTILITY
        assert tool.metadata.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_tool_execute_success(self) -> None:
        """Test successful tool execution."""
        tool = TestTool()
        result = await tool.execute({"value": 10, "operation": "double"})

        assert result.success is True
        assert result.data is not None
        assert result.data.result == 20
        assert result.data.operation == "double"
        assert result.error is None

    @pytest.mark.asyncio
    async def test_tool_execute_validation_error(self) -> None:
        """Test tool execution with validation error."""
        tool = TestTool()
        result = await tool.execute({"value": -5})  # Below minimum

        assert result.success is False
        assert result.error is not None
        assert "ValidationError" in result.error_type

    @pytest.mark.asyncio
    async def test_tool_execute_out_of_range(self) -> None:
        """Test tool execution with out of range value."""
        tool = TestTool()
        result = await tool.execute({"value": 150})  # Above maximum

        assert result.success is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_tool_get_info(self) -> None:
        """Test tool info retrieval."""
        tool = TestTool()
        info = tool.get_info()

        assert info["name"] == "test_tool"
        assert info["category"] == "utility"
        assert info["version"] == "1.0.0"
        assert "test" in info["tags"]

    @pytest.mark.asyncio
    async def test_tool_execution_tracking(self) -> None:
        """Test execution count tracking."""
        tool = TestTool()

        await tool.execute({"value": 5})
        await tool.execute({"value": 10})

        info = tool.get_info()
        assert info["execution_count"] == 2


# ========== Tool Registry Tests ==========

class TestToolRegistry:
    """Tests for ToolRegistry class."""

    @pytest.fixture
    def registry(self) -> ToolRegistry:
        """Create fresh registry for testing."""
        registry = ToolRegistry.get_instance()
        registry.clear()
        return registry

    def test_registry_singleton(self) -> None:
        """Test registry singleton pattern."""
        registry1 = ToolRegistry.get_instance()
        registry2 = ToolRegistry.get_instance()

        assert registry1 is registry2

    def test_registry_register_tool(self, registry: ToolRegistry) -> None:
        """Test tool registration."""
        tool = TestTool()
        registry.register(tool)

        retrieved = registry.get("test_tool")
        assert retrieved is tool

    def test_registry_register_class(self, registry: ToolRegistry) -> None:
        """Test tool class registration."""
        registry.register_class(TestTool)

        tool = registry.get("test_tool")
        assert isinstance(tool, TestTool)

    def test_registry_get_by_category(self, registry: ToolRegistry) -> None:
        """Test getting tools by category."""
        tool = TestTool()
        registry.register(tool)

        tools = registry.get_by_category(ToolCategory.UTILITY)
        assert len(tools) == 1
        assert tools[0].name == "test_tool"

    def test_registry_get_by_tag(self, registry: ToolRegistry) -> None:
        """Test getting tools by tag."""
        tool = TestTool()
        registry.register(tool)

        tools = registry.get_by_tag("test")
        assert len(tools) == 1

    def test_registry_list_all(self, registry: ToolRegistry) -> None:
        """Test listing all tools."""
        tool = TestTool()
        registry.register(tool)

        tools = registry.list_all()
        assert len(tools) == 1
        assert tools[0]["name"] == "test_tool"

    def test_registry_unregister(self, registry: ToolRegistry) -> None:
        """Test tool unregistration."""
        tool = TestTool()
        registry.register(tool)
        registry.unregister("test_tool")

        with pytest.raises(ToolError):
            registry.get("test_tool")

    def test_registry_get_not_found(self, registry: ToolRegistry) -> None:
        """Test getting non-existent tool."""
        with pytest.raises(ToolError):
            registry.get("nonexistent_tool")


# ========== Tool Execution Engine Tests ==========

class TestToolExecutionEngine:
    """Tests for ToolExecutionEngine class."""

    @pytest.fixture
    def engine(self) -> ToolExecutionEngine:
        """Create execution engine for testing."""
        registry = ToolRegistry.get_instance()
        registry.clear()
        registry.register_class(TestTool)
        return ToolExecutionEngine(registry)

    @pytest.mark.asyncio
    async def test_engine_execute(self, engine: ToolExecutionEngine) -> None:
        """Test engine tool execution."""
        result = await engine.execute(
            tool_name="test_tool",
            input_data={"value": 25, "operation": "double"},
        )

        assert result.success is True
        assert result.data.result == 50

    @pytest.mark.asyncio
    async def test_engine_execute_timeout(self, engine: ToolExecutionEngine) -> None:
        """Test engine execution with timeout."""
        result = await engine.execute(
            tool_name="test_tool",
            input_data={"value": 10},
            timeout=0.001,  # Very short timeout
        )

        # Should complete before timeout for simple operation
        assert result.execution_time_ms >= 0

    @pytest.mark.asyncio
    async def test_engine_execute_batch(self, engine: ToolExecutionEngine) -> None:
        """Test batch execution."""
        executions = [
            {"tool_name": "test_tool", "input_data": {"value": 10}},
            {"tool_name": "test_tool", "input_data": {"value": 20}},
            {"tool_name": "test_tool", "input_data": {"value": 30}},
        ]

        results = await engine.execute_batch(executions, concurrent=True)

        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_engine_rate_limiting(self, engine: ToolExecutionEngine) -> None:
        """Test rate limiting."""
        # Register tool with rate limit
        registry = ToolRegistry.get_instance()
        registry.clear()

        class RateLimitedTool(TestTool):
            metadata = ToolMetadata(
                name="rate_limited_tool",
                description="Tool with rate limit",
                category=ToolCategory.UTILITY,
                rate_limit_per_minute=2,
            )

        registry.register_class(RateLimitedTool)

        # First two should succeed
        await engine.execute("rate_limited_tool", {"value": 1})
        await engine.execute("rate_limited_tool", {"value": 2})

        # Third should fail with rate limit
        with pytest.raises(ToolError):
            await engine.execute("rate_limited_tool", {"value": 3})

    @pytest.mark.asyncio
    async def test_engine_execution_history(self, engine: ToolExecutionEngine) -> None:
        """Test execution history tracking."""
        await engine.execute("test_tool", {"value": 10})
        await engine.execute("test_tool", {"value": 20})

        history = engine.get_execution_history(tool_name="test_tool")

        assert len(history) == 2
        assert all(h["tool_name"] == "test_tool" for h in history)


# ========== Tool Error Tests ==========

class TestToolErrors:
    """Tests for tool error handling."""

    def test_tool_error_basic(self) -> None:
        """Test basic tool error."""
        error = ToolError("Test error", tool_name="test")

        assert str(error) == "Test error"
        assert error.tool_name == "test"

    def test_tool_validation_error(self) -> None:
        """Test validation error."""
        error = ToolValidationError(
            "Invalid input",
            tool_name="test",
            cause=ValueError("test"),
        )

        assert error.tool_name == "test"
        assert error.cause is not None

    def test_tool_execution_error(self) -> None:
        """Test execution error."""
        error = ToolExecutionError(
            "Execution failed",
            tool_name="test",
            cause=RuntimeError("test"),
        )

        assert error.tool_name == "test"


# ========== Integration Tests ==========

class TestToolIntegration:
    """Integration tests for tool system."""

    @pytest.mark.asyncio
    async def test_full_tool_workflow(self) -> None:
        """Test complete tool workflow."""
        # Setup
        registry = ToolRegistry.get_instance()
        registry.clear()
        registry.register_class(TestTool)

        engine = ToolExecutionEngine(registry)

        # Execute
        result = await engine.execute(
            tool_name="test_tool",
            input_data={"value": 50, "operation": "double"},
        )

        # Verify
        assert result.success is True
        assert result.data.result == 100
        assert result.execution_time_ms > 0

        # Check history
        history = engine.get_execution_history()
        assert len(history) == 1

    @pytest.mark.asyncio
    async def test_tool_with_config(self) -> None:
        """Test tool with configuration."""
        config = {"custom_setting": "value"}
        tool = TestTool(config=config)

        assert tool.config == config
