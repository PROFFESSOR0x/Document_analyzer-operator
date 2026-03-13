"""Base agent abstract class with lifecycle management."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Awaitable
from datetime import datetime, timezone
import asyncio
import logging

from app.agents.core.states import AgentState, AgentLifecycleState, AgentStatus, StateTransition
from app.agents.core.messages import (
    AgentMessage,
    RequestMessage,
    ResponseMessage,
    EventMessage,
    CommandMessage,
    ResultMessage,
    ErrorMessage,
    MessagePriority,
)
from app.agents.core.errors import (
    AgentError,
    AgentExecutionError,
    AgentTimeoutError,
    AgentStateError,
    AgentCommunicationError,
)
from app.agents.core.telemetry import AgentTelemetry


class BaseAgent(ABC):
    """Abstract base class for all agent types.

    This class provides the core agent functionality including:
    - Lifecycle management (init, start, execute, pause, resume, stop)
    - State management
    - Task execution interface
    - Communication protocol
    - Logging and telemetry
    - Error handling and recovery

    Subclasses must implement:
    - _execute_task(): Core task execution logic
    - get_capabilities(): Agent capabilities description
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize base agent.

        Args:
            agent_id: Unique agent identifier.
            name: Agent name.
            agent_type: Type of agent.
            config: Optional configuration dictionary.
        """
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.config = config or {}

        # State management
        self._status = AgentStatus()
        self._lifecycle_state = AgentLifecycleState.CREATED

        # Message handling
        self._message_handlers: Dict[str, Callable[[AgentMessage], Awaitable[AgentMessage]]] = {}
        self._outgoing_messages: asyncio.Queue[AgentMessage] = asyncio.Queue()
        self._incoming_messages: asyncio.Queue[AgentMessage] = asyncio.Queue()

        # Task management
        self._current_task: Optional[Dict[str, Any]] = None
        self._task_history: List[Dict[str, Any]] = []

        # Telemetry and logging
        self._telemetry = AgentTelemetry(agent_id)
        self._logger = logging.getLogger(f"agent.{agent_id}")

        # Cancellation
        self._cancel_event = asyncio.Event()
        self._current_task_handle: Optional[asyncio.Task] = None

        # Callbacks
        self._state_change_callbacks: List[Callable[[StateTransition], Awaitable[None]]] = []

        self._logger.info(f"Agent {name} ({agent_id}) created with type {agent_type}")

    @property
    def state(self) -> AgentState:
        """Get current agent state.

        Returns:
            AgentState: Current state.
        """
        return self._status.state

    @property
    def lifecycle_state(self) -> AgentLifecycleState:
        """Get current lifecycle state.

        Returns:
            AgentLifecycleState: Current lifecycle phase.
        """
        return self._lifecycle_state

    @property
    def status(self) -> AgentStatus:
        """Get agent status.

        Returns:
            AgentStatus: Current status.
        """
        return self._status

    @property
    def telemetry(self) -> AgentTelemetry:
        """Get agent telemetry.

        Returns:
            AgentTelemetry: Telemetry collector.
        """
        return self._telemetry

    @property
    def is_running(self) -> bool:
        """Check if agent is running.

        Returns:
            bool: True if running.
        """
        return self.state == AgentState.RUNNING

    @property
    def is_idle(self) -> bool:
        """Check if agent is idle.

        Returns:
            bool: True if idle.
        """
        return self.state == AgentState.IDLE

    @property
    def current_task(self) -> Optional[Dict[str, Any]]:
        """Get current task.

        Returns:
            Optional[Dict]: Current task data.
        """
        return self._current_task

    # ========== Lifecycle Management ==========

    async def initialize(self) -> None:
        """Initialize the agent.

        This method sets up the agent and prepares it for execution.
        Subclasses can override _on_initialize() for custom initialization.
        """
        if self._lifecycle_state != AgentLifecycleState.CREATED:
            raise AgentStateError(
                f"Cannot initialize agent in state {self._lifecycle_state.value}",
                current_state=self._lifecycle_state.value,
                agent_id=self.agent_id,
            )

        self._logger.info(f"Initializing agent {self.name}")
        self._update_state(AgentState.INITIALIZING, "Initializing")

        try:
            await self._on_initialize()
            self._lifecycle_state = AgentLifecycleState.INITIALIZED
            self._update_state(AgentState.IDLE, "Initialized")
            self._logger.info(f"Agent {self.name} initialized successfully")
        except Exception as e:
            self._logger.error(f"Failed to initialize agent {self.name}: {e}")
            self._update_state(AgentState.ERROR, f"Initialization failed: {e}")
            self._lifecycle_state = AgentLifecycleState.TERMINATED
            raise

    async def start(self) -> None:
        """Start the agent.

        This method starts the agent and makes it ready to accept tasks.
        """
        if self._lifecycle_state not in [
            AgentLifecycleState.INITIALIZED,
            AgentLifecycleState.STOPPED,
        ]:
            raise AgentStateError(
                f"Cannot start agent in state {self._lifecycle_state.value}",
                current_state=self._lifecycle_state.value,
                agent_id=self.agent_id,
            )

        self._logger.info(f"Starting agent {self.name}")
        self._update_state(AgentState.RUNNING, "Starting")
        self._lifecycle_state = AgentLifecycleState.STARTED
        self._cancel_event.clear()

        await self._on_start()
        self._logger.info(f"Agent {self.name} started")

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task.

        Args:
            task: Task data dictionary.

        Returns:
            Dict: Task result.

        Raises:
            AgentExecutionError: If task execution fails.
        """
        if self.state not in [AgentState.IDLE, AgentState.RUNNING]:
            raise AgentStateError(
                f"Cannot execute task in state {self.state.value}",
                current_state=self.state.value,
                agent_id=self.agent_id,
            )

        self._current_task = task
        self._status.current_task_id = task.get("id")
        self._update_state(AgentState.RUNNING, f"Executing task {task.get('id')}")
        self._lifecycle_state = AgentLifecycleState.EXECUTING

        start_time = datetime.now(timezone.utc)
        success = False

        try:
            self._logger.info(f"Executing task {task.get('id')} on agent {self.name}")
            result = await self._execute_task(task)
            success = True
            self._logger.info(f"Task {task.get('id')} completed successfully")
            return result
        except asyncio.CancelledError:
            self._logger.info(f"Task {task.get('id')} cancelled")
            raise
        except Exception as e:
            self._logger.error(f"Task execution failed: {e}")
            raise AgentExecutionError(
                str(e),
                task_id=task.get("id"),
                agent_id=self.agent_id,
                cause=e,
            ) from e
        finally:
            end_time = datetime.now(timezone.utc)
            execution_time_ms = (end_time - start_time).total_seconds() * 1000
            self._telemetry.record_execution(execution_time_ms, success, task.get("id"))
            self._task_history.append(
                {
                    "task": task,
                    "success": success,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                }
            )
            self._current_task = None
            self._status.current_task_id = None
            if not self._cancel_event.is_set():
                self._update_state(AgentState.IDLE, "Task completed")
                self._lifecycle_state = AgentLifecycleState.STARTED

    async def pause(self) -> None:
        """Pause the agent.

        This method pauses agent execution.
        """
        if self.state != AgentState.RUNNING:
            raise AgentStateError(
                f"Cannot pause agent in state {self.state.value}",
                current_state=self.state.value,
                agent_id=self.agent_id,
            )

        self._logger.info(f"Pausing agent {self.name}")
        self._update_state(AgentState.PAUSED, "Pausing")
        self._lifecycle_state = AgentLifecycleState.PAUSED

        await self._on_pause()
        self._logger.info(f"Agent {self.name} paused")

    async def resume(self) -> None:
        """Resume the agent.

        This method resumes agent execution after a pause.
        """
        if self.state != AgentState.PAUSED:
            raise AgentStateError(
                f"Cannot resume agent in state {self.state.value}",
                current_state=self.state.value,
                agent_id=self.agent_id,
            )

        self._logger.info(f"Resuming agent {self.name}")
        self._update_state(AgentState.RUNNING, "Resuming")
        self._lifecycle_state = AgentLifecycleState.RESUMED

        await self._on_resume()
        self._logger.info(f"Agent {self.name} resumed")

    async def stop(self) -> None:
        """Stop the agent.

        This method gracefully stops the agent.
        """
        self._logger.info(f"Stopping agent {self.name}")
        self._update_state(AgentState.STOPPED, "Stopping")
        self._cancel_event.set()

        # Cancel current task if running
        if self._current_task_handle and not self._current_task_handle.done():
            self._current_task_handle.cancel()
            try:
                await self._current_task_handle
            except asyncio.CancelledError:
                pass

        await self._on_stop()
        self._lifecycle_state = AgentLifecycleState.STOPPED
        self._logger.info(f"Agent {self.name} stopped")

    async def terminate(self) -> None:
        """Terminate the agent.

        This method terminates the agent and releases resources.
        """
        self._logger.info(f"Terminating agent {self.name}")

        if self.state != AgentState.STOPPED:
            await self.stop()

        await self._on_terminate()
        self._lifecycle_state = AgentLifecycleState.TERMINATED
        self._update_state(AgentState.TERMINATED, "Terminated")
        self._logger.info(f"Agent {self.name} terminated")

    # ========== Abstract Methods ==========

    @abstractmethod
    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task.

        This method must be implemented by subclasses to define
        the agent's core task execution logic.

        Args:
            task: Task data dictionary.

        Returns:
            Dict: Task result.
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities.

        This method must be implemented by subclasses to describe
        what the agent can do.

        Returns:
            Dict: Capabilities description.
        """
        pass

    # ========== Lifecycle Hooks ==========

    async def _on_initialize(self) -> None:
        """Hook for custom initialization.

        Subclasses can override this method for custom initialization logic.
        """
        pass

    async def _on_start(self) -> None:
        """Hook for custom start logic.

        Subclasses can override this method for custom start logic.
        """
        pass

    async def _on_pause(self) -> None:
        """Hook for custom pause logic.

        Subclasses can override this method for custom pause logic.
        """
        pass

    async def _on_resume(self) -> None:
        """Hook for custom resume logic.

        Subclasses can override this method for custom resume logic.
        """
        pass

    async def _on_stop(self) -> None:
        """Hook for custom stop logic.

        Subclasses can override this method for custom stop logic.
        """
        pass

    async def _on_terminate(self) -> None:
        """Hook for custom termination logic.

        Subclasses can override this method for resource cleanup.
        """
        pass

    # ========== Communication Protocol ==========

    async def send_message(self, message: AgentMessage) -> None:
        """Send a message.

        Args:
            message: Message to send.
        """
        message.sender_id = self.agent_id
        await self._outgoing_messages.put(message)
        self._logger.debug(f"Message sent: {message.id} to {message.receiver_id}")

    async def receive_message(self, timeout: Optional[float] = None) -> Optional[AgentMessage]:
        """Receive a message.

        Args:
            timeout: Optional timeout in seconds.

        Returns:
            Optional[AgentMessage]: Received message or None if timeout.
        """
        try:
            message = await asyncio.wait_for(
                self._incoming_messages.get(),
                timeout=timeout,
            )
            self._logger.debug(f"Message received: {message.id} from {message.sender_id}")
            return message
        except asyncio.TimeoutError:
            return None

    async def send_request(
        self,
        receiver_id: str,
        payload: Dict[str, Any],
        timeout_seconds: float = 30.0,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> ResponseMessage:
        """Send a request and wait for response.

        Args:
            receiver_id: Target agent ID.
            payload: Request payload.
            timeout_seconds: Request timeout.
            priority: Message priority.

        Returns:
            ResponseMessage: Response message.

        Raises:
            AgentTimeoutError: If request times out.
        """
        request = RequestMessage(
            receiver_id=receiver_id,
            payload=payload,
            timeout_seconds=timeout_seconds,
            priority=priority,
        )
        await self.send_message(request)

        # Wait for response
        start_time = datetime.now(timezone.utc)
        while True:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            if elapsed >= timeout_seconds:
                raise AgentTimeoutError(
                    f"Request timed out after {timeout_seconds}s",
                    timeout_seconds=timeout_seconds,
                    agent_id=self.agent_id,
                    operation="request_response",
                )

            message = await self.receive_message(timeout=1.0)
            if message and isinstance(message, ResponseMessage):
                if message.correlation_id == request.id:
                    return message

    async def send_event(
        self,
        event_name: str,
        payload: Dict[str, Any],
        broadcast: bool = False,
        receiver_id: Optional[str] = None,
    ) -> None:
        """Send an event notification.

        Args:
            event_name: Name of the event.
            payload: Event payload.
            broadcast: Whether to broadcast to all agents.
            receiver_id: Optional specific receiver.
        """
        event = EventMessage(
            event_name=event_name,
            payload=payload,
            broadcast=broadcast,
            receiver_id=receiver_id,
        )
        await self.send_message(event)

    async def send_command(
        self,
        receiver_id: str,
        command: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> ResultMessage:
        """Send a command and get result.

        Args:
            receiver_id: Target agent ID.
            command: Command name.
            args: Command arguments.
            kwargs: Command keyword arguments.

        Returns:
            ResultMessage: Command result.
        """
        cmd = CommandMessage(
            receiver_id=receiver_id,
            command=command,
            args=args or [],
            kwargs=kwargs or {},
        )
        await self.send_message(cmd)

        # Wait for result
        while True:
            message = await self.receive_message(timeout=5.0)
            if message and isinstance(message, ResultMessage):
                if message.correlation_id == cmd.id:
                    return message

    async def send_error(
        self,
        receiver_id: str,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        recoverable: bool = True,
    ) -> None:
        """Send an error notification.

        Args:
            receiver_id: Target agent ID.
            error_type: Type of error.
            error_message: Error message.
            stack_trace: Optional stack trace.
            recoverable: Whether error is recoverable.
        """
        error = ErrorMessage(
            receiver_id=receiver_id,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            recoverable=recoverable,
        )
        await self.send_message(error)

    # ========== Message Handling ==========

    def register_handler(
        self,
        message_type: str,
        handler: Callable[[AgentMessage], Awaitable[AgentMessage]],
    ) -> None:
        """Register a message handler.

        Args:
            message_type: Type of message to handle.
            handler: Handler function.
        """
        self._message_handlers[message_type] = handler
        self._logger.debug(f"Registered handler for message type: {message_type}")

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle an incoming message.

        Args:
            message: Message to handle.

        Returns:
            Optional[AgentMessage]: Response message if any.
        """
        handler = self._message_handlers.get(message.type.value)
        if handler:
            try:
                return await handler(message)
            except Exception as e:
                self._logger.error(f"Error handling message: {e}")
                return ErrorMessage(
                    receiver_id=message.sender_id,
                    error_type="HandlerError",
                    error_message=str(e),
                    recoverable=True,
                )
        return None

    # ========== State Management ==========

    def _update_state(
        self,
        new_state: AgentState,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StateTransition:
        """Update agent state.

        Args:
            new_state: New state.
            reason: Reason for transition.
            metadata: Additional metadata.

        Returns:
            StateTransition: The transition record.
        """
        transition = self._status.update_state(new_state, reason, metadata)
        self._logger.info(f"State transition: {transition.from_state.value} -> {new_state.value}")

        # Notify callbacks
        for callback in self._state_change_callbacks:
            asyncio.create_task(callback(transition))

        return transition

    def on_state_change(
        self,
        callback: Callable[[StateTransition], Awaitable[None]],
    ) -> None:
        """Register a state change callback.

        Args:
            callback: Callback function.
        """
        self._state_change_callbacks.append(callback)

    # ========== Utility Methods ==========

    def get_info(self) -> Dict[str, Any]:
        """Get agent information.

        Returns:
            Dict: Agent information.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "agent_type": self.agent_type,
            "state": self.state.value,
            "lifecycle_state": self._lifecycle_state.value,
            "config": self.config,
            "capabilities": self.get_capabilities(),
            "telemetry": self._telemetry.to_dict(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            str: Agent representation.
        """
        return f"<{self.__class__.__name__} {self.name} ({self.agent_id}) state={self.state.value}>"
