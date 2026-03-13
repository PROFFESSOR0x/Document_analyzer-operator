"""Agent telemetry and metrics collection."""

from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from collections import deque
import statistics


@dataclass
class AgentMetrics:
    """Metrics collected from agent execution.

    Attributes:
        execution_count: Total number of executions.
        success_count: Number of successful executions.
        failure_count: Number of failed executions.
        total_execution_time_ms: Total execution time in milliseconds.
        avg_execution_time_ms: Average execution time.
        min_execution_time_ms: Minimum execution time.
        max_execution_time_ms: Maximum execution time.
        last_execution_time: Timestamp of last execution.
        success_rate: Success rate percentage.
    """

    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_execution_time_ms: float = 0.0
    execution_times: List[float] = field(default_factory=list)
    last_execution_time: Optional[datetime] = None

    @property
    def avg_execution_time_ms(self) -> float:
        """Calculate average execution time.

        Returns:
            float: Average execution time in milliseconds.
        """
        if not self.execution_times:
            return 0.0
        return statistics.mean(self.execution_times)

    @property
    def min_execution_time_ms(self) -> float:
        """Get minimum execution time.

        Returns:
            float: Minimum execution time.
        """
        if not self.execution_times:
            return 0.0
        return min(self.execution_times)

    @property
    def max_execution_time_ms(self) -> float:
        """Get maximum execution time.

        Returns:
            float: Maximum execution time.
        """
        if not self.execution_times:
            return 0.0
        return max(self.execution_times)

    @property
    def success_rate(self) -> float:
        """Calculate success rate.

        Returns:
            float: Success rate as percentage.
        """
        if self.execution_count == 0:
            return 0.0
        return (self.success_count / self.execution_count) * 100

    def record_execution(
        self,
        execution_time_ms: float,
        success: bool,
    ) -> None:
        """Record an execution.

        Args:
            execution_time_ms: Execution time in milliseconds.
            success: Whether execution was successful.
        """
        self.execution_count += 1
        self.total_execution_time_ms += execution_time_ms
        self.execution_times.append(execution_time_ms)
        self.last_execution_time = datetime.now(timezone.utc)

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        # Keep only last 1000 execution times
        if len(self.execution_times) > 1000:
            self.execution_times = self.execution_times[-1000:]

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary.

        Returns:
            Dict: Metrics data.
        """
        return {
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": round(self.success_rate, 2),
            "avg_execution_time_ms": round(self.avg_execution_time_ms, 2),
            "min_execution_time_ms": round(self.min_execution_time_ms, 2),
            "max_execution_time_ms": round(self.max_execution_time_ms, 2),
            "total_execution_time_ms": round(self.total_execution_time_ms, 2),
            "last_execution_time": self.last_execution_time.isoformat()
            if self.last_execution_time
            else None,
        }


@dataclass
class TelemetryEvent:
    """Telemetry event for tracking agent behavior.

    Attributes:
        event_type: Type of event.
        timestamp: When the event occurred.
        data: Event data.
        agent_id: ID of the agent.
        task_id: Optional task ID.
    """

    event_type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)
    agent_id: Optional[str] = None
    task_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary.

        Returns:
            Dict: Event data.
        """
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
        }


class AgentTelemetry:
    """Telemetry collector for agent monitoring.

    This class collects and manages telemetry data for agents,
    including metrics, events, and performance data.

    Attributes:
        agent_id: ID of the agent being monitored.
        metrics: Agent execution metrics.
        events: Recent telemetry events.
        start_time: When telemetry collection started.
    """

    def __init__(self, agent_id: str, max_events: int = 1000) -> None:
        """Initialize agent telemetry.

        Args:
            agent_id: ID of the agent.
            max_events: Maximum number of events to retain.
        """
        self.agent_id = agent_id
        self.metrics = AgentMetrics()
        self._events: deque[TelemetryEvent] = deque(maxlen=max_events)
        self.start_time = datetime.now(timezone.utc)
        self._custom_metrics: Dict[str, Any] = {}

    def record_event(
        self,
        event_type: str,
        data: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
    ) -> None:
        """Record a telemetry event.

        Args:
            event_type: Type of event.
            data: Event data.
            task_id: Optional task ID.
        """
        event = TelemetryEvent(
            event_type=event_type,
            data=data or {},
            agent_id=self.agent_id,
            task_id=task_id,
        )
        self._events.append(event)

    def record_execution(
        self,
        execution_time_ms: float,
        success: bool,
        task_id: Optional[str] = None,
    ) -> None:
        """Record an execution with metrics.

        Args:
            execution_time_ms: Execution time in milliseconds.
            success: Whether execution was successful.
            task_id: Optional task ID.
        """
        self.metrics.record_execution(execution_time_ms, success)
        self.record_event(
            event_type="execution",
            data={"execution_time_ms": execution_time_ms, "success": success},
            task_id=task_id,
        )

    def record_custom_metric(self, name: str, value: Any) -> None:
        """Record a custom metric.

        Args:
            name: Metric name.
            value: Metric value.
        """
        self._custom_metrics[name] = value
        self.record_event(
            event_type="custom_metric",
            data={"name": name, "value": value},
        )

    def get_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[TelemetryEvent]:
        """Get telemetry events.

        Args:
            event_type: Optional filter by event type.
            limit: Maximum number of events to return.

        Returns:
            List[TelemetryEvent]: List of events.
        """
        events = list(self._events)
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]

    def get_uptime(self) -> float:
        """Get agent uptime in seconds.

        Returns:
            float: Uptime in seconds.
        """
        delta = datetime.now(timezone.utc) - self.start_time
        return delta.total_seconds()

    def get_health_score(self) -> float:
        """Calculate agent health score.

        Returns:
            float: Health score from 0 to 100.
        """
        if self.metrics.execution_count == 0:
            return 100.0

        # Base score from success rate
        score = self.metrics.success_rate

        # Penalize high average execution time (> 10 seconds)
        if self.metrics.avg_execution_time_ms > 10000:
            score *= 0.9

        # Penalize very high execution time (> 30 seconds)
        if self.metrics.avg_execution_time_ms > 30000:
            score *= 0.8

        return min(100.0, max(0.0, score))

    def to_dict(self) -> Dict[str, Any]:
        """Convert telemetry to dictionary.

        Returns:
            Dict: Telemetry data.
        """
        return {
            "agent_id": self.agent_id,
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": self.get_uptime(),
            "health_score": round(self.get_health_score(), 2),
            "metrics": self.metrics.to_dict(),
            "custom_metrics": self._custom_metrics,
            "recent_events": [e.to_dict() for e in self.get_events(limit=10)],
        }
