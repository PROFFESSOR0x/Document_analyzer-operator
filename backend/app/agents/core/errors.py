"""Agent error types and exception hierarchy."""

from typing import Any, Optional


class AgentError(Exception):
    """Base exception for all agent-related errors.

    Attributes:
        agent_id: ID of the agent that encountered the error.
        message: Error message.
        details: Additional error details.
        recoverable: Whether the error is recoverable.
    """

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        details: Optional[dict] = None,
        recoverable: bool = True,
    ) -> None:
        """Initialize agent error.

        Args:
            message: Error message.
            agent_id: ID of the agent.
            details: Additional details.
            recoverable: Whether recoverable.
        """
        self.agent_id = agent_id
        self.message = message
        self.details = details or {}
        self.recoverable = recoverable
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert error to dictionary.

        Returns:
            dict: Error data as dictionary.
        """
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "agent_id": self.agent_id,
            "details": self.details,
            "recoverable": self.recoverable,
        }


class AgentExecutionError(AgentError):
    """Error during agent task execution.

    This exception is raised when an agent encounters an error
    while executing a task.
    """

    def __init__(
        self,
        message: str,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize execution error.

        Args:
            message: Error message.
            task_id: ID of the task being executed.
            agent_id: ID of the agent.
            cause: Original exception that caused this error.
        """
        details = {"task_id": task_id}
        if cause:
            details["cause"] = str(cause)
            details["cause_type"] = type(cause).__name__

        super().__init__(
            message=message,
            agent_id=agent_id,
            details=details,
            recoverable=False,
        )
        self.task_id = task_id
        self.cause = cause


class AgentTimeoutError(AgentError):
    """Error when agent operation times out.

    This exception is raised when an agent operation exceeds
    the specified timeout period.
    """

    def __init__(
        self,
        message: str,
        timeout_seconds: float,
        agent_id: Optional[str] = None,
        operation: Optional[str] = None,
    ) -> None:
        """Initialize timeout error.

        Args:
            message: Error message.
            timeout_seconds: Timeout duration in seconds.
            agent_id: ID of the agent.
            operation: Operation that timed out.
        """
        details = {
            "timeout_seconds": timeout_seconds,
            "operation": operation,
        }
        super().__init__(
            message=message,
            agent_id=agent_id,
            details=details,
            recoverable=True,
        )
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class AgentRegistrationError(AgentError):
    """Error during agent registration.

    This exception is raised when there's an issue registering
    an agent with the registry.
    """

    def __init__(
        self,
        message: str,
        agent_type: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> None:
        """Initialize registration error.

        Args:
            message: Error message.
            agent_type: Type of agent being registered.
            agent_id: ID of the agent.
        """
        details = {
            "agent_type": agent_type,
            "agent_id": agent_id,
        }
        super().__init__(
            message=message,
            agent_id=agent_id,
            details=details,
            recoverable=False,
        )
        self.agent_type = agent_type


class AgentConfigurationError(AgentError):
    """Error in agent configuration.

    This exception is raised when agent configuration is invalid
    or missing required fields.
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> None:
        """Initialize configuration error.

        Args:
            message: Error message.
            config_key: Configuration key that caused the error.
            agent_id: ID of the agent.
        """
        details = {"config_key": config_key}
        super().__init__(
            message=message,
            agent_id=agent_id,
            details=details,
            recoverable=False,
        )
        self.config_key = config_key


class AgentCommunicationError(AgentError):
    """Error in agent communication.

    This exception is raised when there's an issue with
    inter-agent communication.
    """

    def __init__(
        self,
        message: str,
        target_agent_id: Optional[str] = None,
        message_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> None:
        """Initialize communication error.

        Args:
            message: Error message.
            target_agent_id: ID of the target agent.
            message_id: ID of the message.
            agent_id: ID of the source agent.
        """
        details = {
            "target_agent_id": target_agent_id,
            "message_id": message_id,
        }
        super().__init__(
            message=message,
            agent_id=agent_id,
            details=details,
            recoverable=True,
        )
        self.target_agent_id = target_agent_id
        self.message_id = message_id


class AgentResourceError(AgentError):
    """Error accessing agent resources.

    This exception is raised when an agent cannot access
    required resources.
    """

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> None:
        """Initialize resource error.

        Args:
            message: Error message.
            resource_type: Type of resource.
            resource_id: ID of the resource.
            agent_id: ID of the agent.
        """
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
        }
        super().__init__(
            message=message,
            agent_id=agent_id,
            details=details,
            recoverable=False,
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class AgentStateError(AgentError):
    """Error related to agent state transitions.

    This exception is raised when an invalid state transition
    is attempted.
    """

    def __init__(
        self,
        message: str,
        current_state: Optional[str] = None,
        target_state: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> None:
        """Initialize state error.

        Args:
            message: Error message.
            current_state: Current agent state.
            target_state: Desired agent state.
            agent_id: ID of the agent.
        """
        details = {
            "current_state": current_state,
            "target_state": target_state,
        }
        super().__init__(
            message=message,
            agent_id=agent_id,
            details=details,
            recoverable=False,
        )
        self.current_state = current_state
        self.target_state = target_state
