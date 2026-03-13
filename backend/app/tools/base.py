"""Base tool system with abstract classes and core functionality."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar, Callable, Awaitable
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ValidationError
import logging
from enum import Enum


TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class ToolCategory(str, Enum):
    """Tool category enumeration."""

    WEB = "web"
    DOCUMENT = "document"
    AI = "ai"
    AUTOMATION = "automation"
    DATA = "data"
    UTILITY = "utility"


class ToolStatus(str, Enum):
    """Tool execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ToolMetadata(BaseModel):
    """Tool metadata for registration and discovery."""

    name: str
    description: str
    category: ToolCategory
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    requires_auth: bool = False
    rate_limit_per_minute: Optional[int] = None
    timeout_seconds: float = 300.0


class ToolResult(BaseModel, Generic[TOutput]):
    """Tool execution result."""

    success: bool
    data: Optional[TOutput] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ToolError(Exception):
    """Base tool error."""

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.tool_name = tool_name
        self.cause = cause


class ToolValidationError(ToolError):
    """Tool input/output validation error."""

    pass


class ToolExecutionError(ToolError):
    """Tool execution error."""

    pass


class ToolTimeoutError(ToolError):
    """Tool execution timeout error."""

    pass


class ToolNotFoundError(ToolError):
    """Tool not found error."""

    pass


class ToolRateLimitError(ToolError):
    """Tool rate limit exceeded error."""

    pass


class BaseTool(ABC, Generic[TInput, TOutput]):
    """Abstract base class for all tools.

    This class provides the core tool functionality including:
    - Input/output validation
    - Execution tracking
    - Error handling
    - Logging and telemetry

    Subclasses must implement:
    - metadata: Tool metadata
    - Input/Output models
    - _execute(): Core execution logic
    """

    metadata: ToolMetadata

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize tool.

        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        self._logger = logging.getLogger(f"tool.{self.metadata.name}")
        self._execution_count = 0
        self._last_execution: Optional[datetime] = None

    @property
    def name(self) -> str:
        """Get tool name."""
        return self.metadata.name

    @property
    def category(self) -> ToolCategory:
        """Get tool category."""
        return self.metadata.category

    @abstractmethod
    async def _execute(self, input_data: TInput) -> TOutput:
        """Execute the tool.

        This method must be implemented by subclasses to define
        the tool's core functionality.

        Args:
            input_data: Validated input data.

        Returns:
            TOutput: Tool output.
        """
        pass

    async def execute(self, input_dict: Dict[str, Any]) -> ToolResult[TOutput]:
        """Execute the tool with input validation.

        Args:
            input_dict: Input data dictionary.

        Returns:
            ToolResult: Execution result.
        """
        start_time = datetime.now(timezone.utc)
        self._execution_count += 1
        self._last_execution = start_time

        self._logger.info(f"Executing tool {self.name}")

        try:
            # Validate input
            input_data = self._validate_input(input_dict)

            # Execute tool
            output_data = await self._execute(input_data)

            # Validate output
            self._validate_output(output_data)

            execution_time_ms = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000

            self._logger.info(
                f"Tool {self.name} executed successfully in {execution_time_ms:.2f}ms"
            )

            return ToolResult[TOutput](
                success=True,
                data=output_data,
                metadata={
                    "execution_count": self._execution_count,
                    "input": input_dict,
                },
                execution_time_ms=execution_time_ms,
            )

        except ValidationError as e:
            execution_time_ms = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000
            error_msg = f"Validation error: {e}"
            self._logger.error(error_msg)
            return ToolResult[TOutput](
                success=False,
                error=error_msg,
                error_type="ValidationError",
                execution_time_ms=execution_time_ms,
            )

        except asyncio.TimeoutError as e:
            execution_time_ms = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000
            error_msg = f"Tool execution timed out after {self.metadata.timeout_seconds}s"
            self._logger.error(error_msg)
            return ToolResult[TOutput](
                success=False,
                error=error_msg,
                error_type="TimeoutError",
                execution_time_ms=execution_time_ms,
            )

        except ToolError as e:
            execution_time_ms = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000
            error_msg = f"Tool error: {e}"
            self._logger.error(error_msg)
            return ToolResult[TOutput](
                success=False,
                error=error_msg,
                error_type=type(e).__name__,
                execution_time_ms=execution_time_ms,
            )

        except Exception as e:
            execution_time_ms = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000
            error_msg = f"Unexpected error: {e}"
            self._logger.exception(error_msg)
            return ToolResult[TOutput](
                success=False,
                error=error_msg,
                error_type=type(e).__name__,
                execution_time_ms=execution_time_ms,
            )

    def _validate_input(self, input_dict: Dict[str, Any]) -> TInput:
        """Validate input data.

        Args:
            input_dict: Input data dictionary.

        Returns:
            TInput: Validated input data.

        Raises:
            ToolValidationError: If validation fails.
        """
        if hasattr(self, "InputModel") and self.InputModel is not None:
            try:
                return self.InputModel(**input_dict)
            except ValidationError as e:
                raise ToolValidationError(
                    f"Invalid input: {e}",
                    tool_name=self.name,
                    cause=e,
                )
        return input_dict  # type: ignore

    def _validate_output(self, output: Any) -> None:
        """Validate output data.

        Args:
            output: Output data to validate.

        Raises:
            ToolValidationError: If validation fails.
        """
        if hasattr(self, "OutputModel") and self.OutputModel is not None:
            try:
                self.OutputModel.model_validate(output)
            except ValidationError as e:
                raise ToolValidationError(
                    f"Invalid output: {e}",
                    tool_name=self.name,
                    cause=e,
                )

    def get_info(self) -> Dict[str, Any]:
        """Get tool information.

        Returns:
            Dict: Tool information.
        """
        return {
            "name": self.name,
            "description": self.metadata.description,
            "category": self.category.value,
            "version": self.metadata.version,
            "tags": self.metadata.tags,
            "requires_auth": self.metadata.requires_auth,
            "rate_limit": self.metadata.rate_limit_per_minute,
            "timeout_seconds": self.metadata.timeout_seconds,
            "execution_count": self._execution_count,
            "last_execution": (
                self._last_execution.isoformat() if self._last_execution else None
            ),
        }

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<{self.__class__.__name__} {self.name} category={self.category.value}>"


class ToolRegistry:
    """Registry for tool discovery and management.

    This class provides:
    - Tool registration
    - Tool lookup by name/category
    - Capability-based tool discovery
    - Tool instance management
    """

    _instance: Optional["ToolRegistry"] = None

    def __new__(cls) -> "ToolRegistry":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize registry."""
        if self._initialized:
            return

        self._tools: Dict[str, BaseTool] = {}
        self._tool_classes: Dict[str, type] = {}
        self._categories: Dict[ToolCategory, set[str]] = {
            category: set() for category in ToolCategory
        }
        self._logger = logging.getLogger("tool.registry")
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "ToolRegistry":
        """Get registry singleton instance.

        Returns:
            ToolRegistry: Registry instance.
        """
        return cls()

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance.

        Args:
            tool: Tool instance to register.
        """
        tool_name = tool.name

        if tool_name in self._tools:
            self._logger.warning(f"Tool {tool_name} already registered, replacing")

        self._tools[tool_name] = tool
        self._categories[tool.category].add(tool_name)
        self._logger.info(f"Registered tool: {tool_name} in category {tool.category.value}")

    def register_class(
        self,
        tool_class: type[BaseTool],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a tool class for lazy instantiation.

        Args:
            tool_class: Tool class to register.
            config: Optional default configuration.
        """
        if not hasattr(tool_class, "metadata"):
            raise ToolError(f"Tool class {tool_class.__name__} missing metadata")

        tool_name = tool_class.metadata.name
        self._tool_classes[tool_name] = tool_class

        if config:
            self._tools[tool_name] = tool_class(config=config)
            self._categories[tool_class.metadata.category].add(tool_name)

        self._logger.info(f"Registered tool class: {tool_name}")

    def get(self, tool_name: str) -> BaseTool:
        """Get a tool by name.

        Args:
            tool_name: Tool name.

        Returns:
            BaseTool: Tool instance.

        Raises:
            ToolNotFoundError: If tool not found.
        """
        if tool_name in self._tools:
            return self._tools[tool_name]

        if tool_name in self._tool_classes:
            tool_class = self._tool_classes[tool_name]
            tool = tool_class()
            self.register(tool)
            return tool

        raise ToolNotFoundError(f"Tool not found: {tool_name}", tool_name=tool_name)

    def get_by_category(self, category: ToolCategory) -> list[BaseTool]:
        """Get all tools in a category.

        Args:
            category: Tool category.

        Returns:
            list[BaseTool]: List of tools.
        """
        tool_names = self._categories.get(category, set())
        return [self.get(name) for name in tool_names]

    def get_by_tag(self, tag: str) -> list[BaseTool]:
        """Get all tools with a specific tag.

        Args:
            tag: Tool tag.

        Returns:
            list[BaseTool]: List of tools.
        """
        return [
            tool for tool in self._tools.values()
            if tag in tool.metadata.tags
        ]

    def list_all(self) -> list[Dict[str, Any]]:
        """List all registered tools.

        Returns:
            list[Dict]: List of tool information dictionaries.
        """
        return [tool.get_info() for tool in self._tools.values()]

    def unregister(self, tool_name: str) -> None:
        """Unregister a tool.

        Args:
            tool_name: Tool name.
        """
        if tool_name in self._tools:
            tool = self._tools[tool_name]
            self._categories[tool.category].discard(tool_name)
            del self._tools[tool_name]
            self._logger.info(f"Unregistered tool: {tool_name}")

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        self._tool_classes.clear()
        for category in self._categories:
            self._categories[category].clear()
        self._logger.info("Cleared all registered tools")


class ToolExecutionEngine:
    """Engine for executing tools with advanced features.

    This class provides:
    - Tool execution with timeout
    - Rate limiting
    - Concurrent execution
    - Execution history
    """

    def __init__(self, registry: Optional[ToolRegistry] = None) -> None:
        """Initialize execution engine.

        Args:
            registry: Optional tool registry.
        """
        self.registry = registry or ToolRegistry.get_instance()
        self._logger = logging.getLogger("tool.engine")
        self._execution_history: list[Dict[str, Any]] = []
        self._rate_limits: Dict[str, list[datetime]] = {}

    async def execute(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> ToolResult:
        """Execute a tool.

        Args:
            tool_name: Name of tool to execute.
            input_data: Tool input data.
            timeout: Optional timeout override.

        Returns:
            ToolResult: Execution result.
        """
        tool = self.registry.get(tool_name)
        metadata = tool.metadata

        # Check rate limit
        await self._check_rate_limit(tool_name, metadata.rate_limit_per_minute)

        # Set timeout
        exec_timeout = timeout or metadata.timeout_seconds

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                tool.execute(input_data),
                timeout=exec_timeout,
            )

            # Record execution
            self._record_execution(tool_name, input_data, result)

            return result

        except asyncio.TimeoutError:
            self._logger.error(f"Tool {tool_name} timed out after {exec_timeout}s")
            return ToolResult(
                success=False,
                error=f"Timeout after {exec_timeout}s",
                error_type="TimeoutError",
                execution_time_ms=exec_timeout * 1000,
            )

    async def execute_batch(
        self,
        executions: list[Dict[str, Any]],
        concurrent: bool = True,
    ) -> list[ToolResult]:
        """Execute multiple tools.

        Args:
            executions: List of execution configs.
            concurrent: Whether to execute concurrently.

        Returns:
            list[ToolResult]: List of results.
        """
        if concurrent:
            tasks = [
                self.execute(
                    exec_config["tool_name"],
                    exec_config["input_data"],
                    exec_config.get("timeout"),
                )
                for exec_config in executions
            ]
            return await asyncio.gather(*tasks, return_exceptions=False)
        else:
            results = []
            for exec_config in executions:
                result = await self.execute(
                    exec_config["tool_name"],
                    exec_config["input_data"],
                    exec_config.get("timeout"),
                )
                results.append(result)
            return results

    async def _check_rate_limit(
        self,
        tool_name: str,
        limit_per_minute: Optional[int],
    ) -> None:
        """Check rate limit for tool.

        Args:
            tool_name: Tool name.
            limit_per_minute: Rate limit per minute.

        Raises:
            ToolRateLimitError: If rate limit exceeded.
        """
        if not limit_per_minute:
            return

        now = datetime.now(timezone.utc)
        window_start = now.timestamp() - 60

        if tool_name not in self._rate_limits:
            self._rate_limits[tool_name] = []

        # Clean old entries
        self._rate_limits[tool_name] = [
            ts for ts in self._rate_limits[tool_name]
            if ts.timestamp() > window_start
        ]

        if len(self._rate_limits[tool_name]) >= limit_per_minute:
            raise ToolRateLimitError(
                f"Rate limit exceeded for tool {tool_name}",
                tool_name=tool_name,
            )

        self._rate_limits[tool_name].append(now)

    def _record_execution(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        result: ToolResult,
    ) -> None:
        """Record execution in history.

        Args:
            tool_name: Tool name.
            input_data: Input data.
            result: Execution result.
        """
        self._execution_history.append(
            {
                "tool_name": tool_name,
                "input": input_data,
                "success": result.success,
                "execution_time_ms": result.execution_time_ms,
                "timestamp": result.timestamp.isoformat(),
            }
        )

        # Keep last 1000 executions
        if len(self._execution_history) > 1000:
            self._execution_history = self._execution_history[-1000:]

    def get_execution_history(
        self,
        tool_name: Optional[str] = None,
        limit: int = 100,
    ) -> list[Dict[str, Any]]:
        """Get execution history.

        Args:
            tool_name: Optional tool name filter.
            limit: Maximum number of records.

        Returns:
            list[Dict]: Execution history.
        """
        history = self._execution_history
        if tool_name:
            history = [h for h in history if h["tool_name"] == tool_name]
        return history[-limit:]


# Import asyncio for timeout handling
import asyncio
