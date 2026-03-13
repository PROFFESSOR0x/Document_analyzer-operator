"""Agent state management and lifecycle."""

from enum import Enum
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field


class AgentState(str, Enum):
    """Enumeration of agent states.

    Attributes:
        IDLE: Agent is idle and ready for tasks.
        RUNNING: Agent is actively executing a task.
        PAUSED: Agent execution is paused.
        STOPPED: Agent has been stopped.
        ERROR: Agent encountered an error.
        INITIALIZING: Agent is being initialized.
        TERMINATED: Agent has been terminated.
    """

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    INITIALIZING = "initializing"
    TERMINATED = "terminated"


class AgentLifecycleState(str, Enum):
    """Enumeration of agent lifecycle phases.

    Attributes:
        CREATED: Agent instance created but not initialized.
        INITIALIZED: Agent initialized and ready to start.
        STARTED: Agent started and can accept tasks.
        EXECUTING: Agent is executing a task.
        PAUSED: Agent execution paused.
        RESUMED: Agent resumed after pause.
        STOPPED: Agent stopped gracefully.
        TERMINATED: Agent terminated and resources released.
    """

    CREATED = "created"
    INITIALIZED = "initialized"
    STARTED = "started"
    EXECUTING = "executing"
    PAUSED = "paused"
    RESUMED = "resumed"
    STOPPED = "stopped"
    TERMINATED = "terminated"


@dataclass
class StateTransition:
    """Represents a state transition event.

    Attributes:
        from_state: The previous state.
        to_state: The new state.
        timestamp: When the transition occurred.
        reason: Optional reason for the transition.
        metadata: Additional transition metadata.
    """

    from_state: AgentState
    to_state: AgentState
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reason: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert transition to dictionary.

        Returns:
            dict: Transition data as dictionary.
        """
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
            "metadata": self.metadata,
        }


@dataclass
class AgentStatus:
    """Current status of an agent.

    Attributes:
        state: Current agent state.
        lifecycle_state: Current lifecycle phase.
        current_task_id: ID of currently executing task, if any.
        last_activity: Timestamp of last activity.
        error_message: Last error message, if any.
        transition_history: Recent state transitions.
    """

    state: AgentState = AgentState.IDLE
    lifecycle_state: AgentLifecycleState = AgentLifecycleState.CREATED
    current_task_id: Optional[str] = None
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None
    transition_history: list[StateTransition] = field(default_factory=list)

    def update_state(
        self,
        new_state: AgentState,
        reason: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> StateTransition:
        """Update agent state and record transition.

        Args:
            new_state: The new state to transition to.
            reason: Optional reason for the transition.
            metadata: Optional additional metadata.

        Returns:
            StateTransition: The recorded transition.
        """
        transition = StateTransition(
            from_state=self.state,
            to_state=new_state,
            reason=reason,
            metadata=metadata or {},
        )
        self.state = new_state
        self.last_activity = datetime.now(timezone.utc)
        self.transition_history.append(transition)

        # Keep only last 100 transitions
        if len(self.transition_history) > 100:
            self.transition_history = self.transition_history[-100:]

        return transition

    def set_error(self, error_message: str) -> None:
        """Set agent to error state.

        Args:
            error_message: The error message.
        """
        self.error_message = error_message
        self.update_state(AgentState.ERROR, reason=error_message)

    def clear_error(self) -> None:
        """Clear error state and return to idle."""
        self.error_message = None
        self.update_state(AgentState.IDLE, reason="Error cleared")

    def to_dict(self) -> dict:
        """Convert status to dictionary.

        Returns:
            dict: Status data as dictionary.
        """
        return {
            "state": self.state.value,
            "lifecycle_state": self.lifecycle_state.value,
            "current_task_id": self.current_task_id,
            "last_activity": self.last_activity.isoformat(),
            "error_message": self.error_message,
            "transition_history": [t.to_dict() for t in self.transition_history[-10:]],
        }
