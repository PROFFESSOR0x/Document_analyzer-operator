"""Tests for the workflow engine."""

import asyncio
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.workflow.engine import (
    WorkflowEngine,
    WorkflowDefinition,
    WorkflowState,
    WorkflowContext,
    WorkflowStatus,
    WorkflowPriority,
)
from app.workflow.activities import (
    ActivityStatus,
    ActivityInput,
    ActivityOutput,
)
from app.workflow.management import (
    WorkflowManager,
    WorkflowScheduler,
    WorkflowMonitor,
    WorkflowHistory,
    WorkflowExecution,
)
from app.workflow.lightweight import (
    LightweightWorkflowEngine,
    LightweightWorkflowStatus,
    sequential_workflow,
    parallel_workflow,
)


class TestWorkflowDefinition:
    """Test WorkflowDefinition class."""

    def test_create_definition(self):
        """Test creating a workflow definition."""
        definition = WorkflowDefinition(
            name="Test Workflow",
            description="Test description",
            version="1.0.0",
        )

        assert definition.name == "Test Workflow"
        assert definition.description == "Test description"
        assert definition.version == "1.0.0"
        assert definition.id is not None

    def test_definition_to_dict(self):
        """Test converting definition to dictionary."""
        definition = WorkflowDefinition(name="Test")
        data = definition.to_dict()

        assert data["name"] == "Test"
        assert data["version"] == "1.0.0"
        assert "id" in data

    def test_definition_from_dict(self):
        """Test creating definition from dictionary."""
        data = {
            "id": "test-id",
            "name": "Test Workflow",
            "version": "2.0.0",
            "tasks": [{"id": "task1"}],
        }

        definition = WorkflowDefinition.from_dict(data)

        assert definition.id == "test-id"
        assert definition.name == "Test Workflow"
        assert definition.version == "2.0.0"
        assert len(definition.tasks) == 1


class TestWorkflowState:
    """Test WorkflowState class."""

    def test_create_state(self):
        """Test creating a workflow state."""
        state = WorkflowState(
            definition_id="test-def",
            status=WorkflowStatus.PENDING,
            priority=WorkflowPriority.HIGH,
        )

        assert state.definition_id == "test-def"
        assert state.status == WorkflowStatus.PENDING
        assert state.priority == WorkflowPriority.HIGH
        assert state.progress == 0

    def test_state_to_dict(self):
        """Test converting state to dictionary."""
        state = WorkflowState(definition_id="test")
        data = state.to_dict()

        assert data["definition_id"] == "test"
        assert data["status"] == "pending"
        assert data["priority"] == "medium"

    def test_update_progress(self):
        """Test updating workflow progress."""
        state = WorkflowState(definition_id="test")

        state.update_progress(50)
        assert state.progress == 50

        state.update_progress(150)  # Should cap at 100
        assert state.progress == 100

        state.update_progress(-10)  # Should cap at 0
        assert state.progress == 0

    def test_mark_task_completed(self):
        """Test marking task as completed."""
        state = WorkflowState(definition_id="test")

        state.mark_task_completed("task1")
        assert "task1" in state.completed_tasks
        assert state.progress > 0

    def test_mark_task_failed(self):
        """Test marking task as failed."""
        state = WorkflowState(definition_id="test")

        state.mark_task_failed("task1")
        assert "task1" in state.failed_tasks


class TestWorkflowContext:
    """Test WorkflowContext class."""

    def test_create_context(self):
        """Test creating a workflow context."""
        context = WorkflowContext(
            workflow_id="test-workflow",
            user_id="user-123",
            workspace_id="ws-456",
        )

        assert context.workflow_id == "test-workflow"
        assert context.user_id == "user-123"
        assert context.workspace_id == "ws-456"
        assert context.correlation_id is not None

    def test_context_is_expired(self):
        """Test checking if context is expired."""
        from datetime import timedelta

        # Not expired
        context = WorkflowContext(workflow_id="test")
        assert not context.is_expired()

        # Expired
        context = WorkflowContext(
            workflow_id="test",
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
        assert context.is_expired()


class TestWorkflowEngine:
    """Test WorkflowEngine class."""

    @pytest.mark.asyncio
    async def test_engine_initialization(self):
        """Test engine initialization."""
        engine = WorkflowEngine(
            temporal_host="localhost",
            temporal_port=7233,
            task_queue="test-queue",
        )

        assert engine.temporal_host == "localhost"
        assert engine.temporal_port == 7233
        assert engine.task_queue == "test-queue"
        assert engine.client is None

    @pytest.mark.asyncio
    async def test_register_workflow(self):
        """Test registering a workflow."""
        engine = WorkflowEngine()

        class TestWorkflow:
            pass

        engine.register_workflow(TestWorkflow)

        assert "TestWorkflow" in engine.workflows
        assert engine.workflows["TestWorkflow"] == TestWorkflow

    @pytest.mark.asyncio
    async def test_register_activity(self):
        """Test registering an activity."""
        engine = WorkflowEngine()

        def test_activity():
            pass

        engine.register_activity(test_activity)

        assert "test_activity" in engine.activities

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """Test connection failure handling."""
        engine = WorkflowEngine(temporal_host="invalid-host")

        with pytest.raises(Exception):
            await engine.connect()

    @pytest.mark.asyncio
    async def test_execute_workflow_not_connected(self):
        """Test executing workflow without connection."""
        engine = WorkflowEngine()

        with pytest.raises(RuntimeError, match="Not connected"):
            await engine.execute_workflow(
                workflow_id="test",
                workflow_type="TestWorkflow",
                input_data={},
            )

    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self):
        """Test executing non-existent workflow."""
        engine = WorkflowEngine()
        engine.client = MagicMock()

        with pytest.raises(RuntimeError, match="Workflow type not found"):
            await engine.execute_workflow(
                workflow_id="test",
                workflow_type="NonExistentWorkflow",
                input_data={},
            )


class TestLightweightWorkflowEngine:
    """Test LightweightWorkflowEngine class."""

    @pytest.mark.asyncio
    async def test_lightweight_engine_initialization(self):
        """Test lightweight engine initialization."""
        engine = LightweightWorkflowEngine(max_concurrent=5)

        assert engine.max_concurrent == 5
        assert len(engine.workflows) == 0

    @pytest.mark.asyncio
    async def test_register_workflow(self):
        """Test registering a workflow in lightweight engine."""
        engine = LightweightWorkflowEngine()

        async def test_workflow(input_data):
            return {"result": "success"}

        engine.register_workflow("test_workflow", test_workflow)

        assert "test_workflow" in engine.workflows

    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        """Test executing a workflow in lightweight engine."""
        engine = LightweightWorkflowEngine()

        async def test_workflow(input_data):
            return {"result": "success", "data": input_data}

        engine.register_workflow("test_workflow", test_workflow)

        execution_id = await engine.execute(
            workflow_type="test_workflow",
            input_data={"key": "value"},
        )

        assert execution_id is not None
        assert execution_id in engine.executions

        status = await engine.get_status(execution_id)
        assert status.status == LightweightWorkflowStatus.COMPLETED
        assert status.output_data["result"] == "success"

    @pytest.mark.asyncio
    async def test_execute_nonexistent_workflow(self):
        """Test executing non-existent workflow."""
        engine = LightweightWorkflowEngine()

        with pytest.raises(ValueError, match="Workflow type not found"):
            await engine.execute(
                workflow_type="nonexistent",
                input_data={},
            )

    @pytest.mark.asyncio
    async def test_cancel_workflow(self):
        """Test cancelling a workflow."""
        engine = LightweightWorkflowEngine()

        async def slow_workflow(input_data):
            await asyncio.sleep(10)
            return {"result": "done"}

        engine.register_workflow("slow_workflow", slow_workflow)

        execution_id = await engine.execute(
            workflow_type="slow_workflow",
            input_data={},
            background=True,
        )

        # Wait a bit for workflow to start
        await asyncio.sleep(0.1)

        # Cancel workflow
        await engine.cancel(execution_id)

        status = await engine.get_status(execution_id)
        assert status.status == LightweightWorkflowStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_list_executions(self):
        """Test listing executions."""
        engine = LightweightWorkflowEngine()

        async def test_workflow(input_data):
            return {"result": "success"}

        engine.register_workflow("test_workflow", test_workflow)

        # Create multiple executions
        await engine.execute("test_workflow", {})
        await engine.execute("test_workflow", {})

        executions = engine.list_executions()
        assert len(executions) == 2

    @pytest.mark.asyncio
    async def test_list_executions_with_filter(self):
        """Test listing executions with status filter."""
        engine = LightweightWorkflowEngine()

        async def test_workflow(input_data):
            return {"result": "success"}

        engine.register_workflow("test_workflow", test_workflow)

        await engine.execute("test_workflow", {})

        completed = engine.list_executions(
            status_filter=LightweightWorkflowStatus.COMPLETED
        )
        assert len(completed) == 1

        failed = engine.list_executions(
            status_filter=LightweightWorkflowStatus.FAILED
        )
        assert len(failed) == 0


class TestSequentialWorkflow:
    """Test sequential workflow pattern."""

    @pytest.mark.asyncio
    async def test_sequential_workflow_basic(self):
        """Test basic sequential workflow."""
        results = []

        async def task1(data):
            results.append("task1")
            return {"step": 1}

        async def task2(data):
            results.append("task2")
            return {"step": 2}

        result = await sequential_workflow(
            {
                "tasks": [task1, task2],
                "initial_data": {"start": True},
            }
        )

        assert results == ["task1", "task2"]
        assert result["task_results"] == [{"step": 1}, {"step": 2}]


class TestParallelWorkflow:
    """Test parallel workflow pattern."""

    @pytest.mark.asyncio
    async def test_parallel_workflow_basic(self):
        """Test basic parallel workflow."""
        executed = []

        async def task1(data):
            executed.append("task1")
            return {"result": "task1"}

        async def task2(data):
            executed.append("task2")
            return {"result": "task2"}

        result = await parallel_workflow(
            {
                "tasks": [task1, task2],
                "input_data": {"start": True},
            }
        )

        # Both tasks should be executed (order may vary)
        assert set(executed) == {"task1", "task2"}
        assert len(result["results"]) == 2


class TestWorkflowManager:
    """Test WorkflowManager class."""

    @pytest.mark.asyncio
    async def test_manager_creation(self):
        """Test creating a workflow manager."""
        engine = WorkflowEngine()
        manager = WorkflowManager(engine)

        assert manager.engine == engine
        assert len(manager.executions) == 0
        assert len(manager.definitions) == 0

    @pytest.mark.asyncio
    async def test_register_definition(self):
        """Test registering a workflow definition."""
        engine = WorkflowEngine()
        manager = WorkflowManager(engine)

        definition = WorkflowDefinition(name="Test")
        manager.register_definition(definition)

        assert definition.id in manager.definitions

    @pytest.mark.asyncio
    async def test_create_workflow(self):
        """Test creating a workflow."""
        engine = WorkflowEngine()
        engine.workflows["TestWorkflow"] = MagicMock()
        manager = WorkflowManager(engine)

        execution = await manager.create_workflow(
            workflow_type="TestWorkflow",
            input_data={"key": "value"},
        )

        assert execution is not None
        assert execution.workflow_type == "TestWorkflow"
        assert execution.state.status == WorkflowStatus.PENDING
        assert execution.execution_id in manager.executions

    @pytest.mark.asyncio
    async def test_create_nonexistent_workflow(self):
        """Test creating non-existent workflow."""
        engine = WorkflowEngine()
        manager = WorkflowManager(engine)

        with pytest.raises(ValueError, match="Workflow type not found"):
            await manager.create_workflow(
                workflow_type="NonExistent",
                input_data={},
            )


class TestWorkflowHistory:
    """Test WorkflowHistory class."""

    def test_record_event(self):
        """Test recording an event."""
        history = WorkflowHistory()

        history.record_event(
            execution_id="exec-123",
            event_type="started",
            event_data={"timestamp": "2024-01-01"},
        )

        assert len(history.history_records) == 1
        assert history.history_records[0]["execution_id"] == "exec-123"

    def test_get_history(self):
        """Test getting history."""
        history = WorkflowHistory()

        history.record_event("exec-1", "started", {})
        history.record_event("exec-2", "started", {})
        history.record_event("exec-1", "completed", {})

        # Get all
        all_records = history.get_history()
        assert len(all_records) == 3

        # Filter by execution_id
        exec1_records = history.get_history(execution_id="exec-1")
        assert len(exec1_records) == 2

        # Filter by event_type
        started_records = history.get_history(event_type_filter="started")
        assert len(started_records) == 2

    def test_clear_history(self):
        """Test clearing history."""
        history = WorkflowHistory()

        history.record_event("exec-1", "started", {})
        history.record_event("exec-2", "started", {})

        # Clear all
        history.clear_history()
        assert len(history.history_records) == 0

        # Add more and clear specific
        history.record_event("exec-1", "started", {})
        history.record_event("exec-2", "started", {})
        history.clear_history(execution_id="exec-1")
        assert len(history.history_records) == 1
        assert history.history_records[0]["execution_id"] == "exec-2"

    def test_max_records_limit(self):
        """Test max records limit."""
        history = WorkflowHistory(max_records=5)

        for i in range(10):
            history.record_event(f"exec-{i}", "started", {})

        # Should only keep last 5
        assert len(history.history_records) == 5
        assert history.history_records[0]["execution_id"] == "exec-5"


class TestActivityOutput:
    """Test ActivityOutput class."""

    def test_success_output(self):
        """Test creating success output."""
        started_at = datetime.now(timezone.utc)

        output = ActivityOutput.success(
            activity_id="act-123",
            output_data={"result": "success"},
            started_at=started_at,
        )

        assert output.status == ActivityStatus.COMPLETED
        assert output.output_data["result"] == "success"
        assert output.error_message is None

    def test_failure_output(self):
        """Test creating failure output."""
        started_at = datetime.now(timezone.utc)

        output = ActivityOutput.failure(
            activity_id="act-123",
            error_message="Test error",
            started_at=started_at,
        )

        assert output.status == ActivityStatus.FAILED
        assert output.error_message == "Test error"

    def test_output_to_dict(self):
        """Test converting output to dictionary."""
        started_at = datetime.now(timezone.utc)

        output = ActivityOutput.success(
            activity_id="act-123",
            output_data={"key": "value"},
            started_at=started_at,
        )

        data = output.to_dict()

        assert data["activity_id"] == "act-123"
        assert data["status"] == "completed"
        assert data["output_data"]["key"] == "value"
        assert "duration_ms" in data


class TestWorkflowScheduler:
    """Test WorkflowScheduler class."""

    @pytest.mark.asyncio
    async def test_scheduler_creation(self):
        """Test creating a workflow scheduler."""
        engine = WorkflowEngine()
        manager = WorkflowManager(engine)
        scheduler = WorkflowScheduler(manager)

        assert scheduler.manager == manager
        assert not scheduler.running
        assert len(scheduler.scheduled_jobs) == 0

    def test_schedule_workflow(self):
        """Test scheduling a workflow."""
        engine = WorkflowEngine()
        engine.workflows["TestWorkflow"] = MagicMock()
        manager = WorkflowManager(engine)
        scheduler = WorkflowScheduler(manager)

        schedule_id = scheduler.schedule_workflow(
            workflow_type="TestWorkflow",
            cron_expression="0 9 * * *",  # Daily at 9 AM
            input_data={"key": "value"},
        )

        assert schedule_id is not None
        assert schedule_id in scheduler.scheduled_jobs
        assert scheduler.scheduled_jobs[schedule_id]["cron_expression"] == "0 9 * * *"

    def test_schedule_invalid_cron(self):
        """Test scheduling with invalid cron expression."""
        engine = WorkflowEngine()
        manager = WorkflowManager(engine)
        scheduler = WorkflowScheduler(manager)

        with pytest.raises(ValueError, match="Invalid cron"):
            scheduler.schedule_workflow(
                workflow_type="TestWorkflow",
                cron_expression="invalid",
                input_data={},
            )

    def test_unschedule_workflow(self):
        """Test unscheduling a workflow."""
        engine = WorkflowEngine()
        engine.workflows["TestWorkflow"] = MagicMock()
        manager = WorkflowManager(engine)
        scheduler = WorkflowScheduler(manager)

        schedule_id = scheduler.schedule_workflow(
            workflow_type="TestWorkflow",
            cron_expression="0 9 * * *",
            input_data={},
        )

        scheduler.unschedule_workflow(schedule_id)

        assert schedule_id not in scheduler.scheduled_jobs

    def test_enable_disable_schedule(self):
        """Test enabling and disabling a schedule."""
        engine = WorkflowEngine()
        engine.workflows["TestWorkflow"] = MagicMock()
        manager = WorkflowManager(engine)
        scheduler = WorkflowScheduler(manager)

        schedule_id = scheduler.schedule_workflow(
            workflow_type="TestWorkflow",
            cron_expression="0 9 * * *",
            input_data={},
        )

        # Disable
        scheduler.disable_schedule(schedule_id)
        assert not scheduler.scheduled_jobs[schedule_id]["enabled"]

        # Enable
        scheduler.enable_schedule(schedule_id)
        assert scheduler.scheduled_jobs[schedule_id]["enabled"]


class TestWorkflowMonitor:
    """Test WorkflowMonitor class."""

    @pytest.mark.asyncio
    async def test_monitor_creation(self):
        """Test creating a workflow monitor."""
        engine = WorkflowEngine()
        manager = WorkflowManager(engine)
        monitor = WorkflowMonitor(manager)

        assert monitor.manager == manager
        assert not monitor._running
        assert monitor.metrics["total_executions"] == 0

    @pytest.mark.asyncio
    async def test_register_health_check(self):
        """Test registering a health check."""
        engine = WorkflowEngine()
        manager = WorkflowManager(engine)
        monitor = WorkflowMonitor(manager)

        def health_check():
            return True

        monitor.register_health_check(health_check)

        assert len(monitor.health_checks) == 1
        assert monitor.health_checks[0] == health_check

    @pytest.mark.asyncio
    async def test_check_health(self):
        """Test checking health."""
        engine = WorkflowEngine()
        manager = WorkflowManager(engine)
        monitor = WorkflowMonitor(manager)

        def healthy_check():
            return True

        def unhealthy_check():
            return False

        monitor.register_health_check(healthy_check)
        monitor.register_health_check(unhealthy_check)

        health = await monitor.check_health()

        assert not health["healthy"]  # One check failed
        assert "healthy_check" in health["checks"]
        assert "unhealthy_check" in health["checks"]
        assert health["checks"]["healthy_check"]["healthy"]
        assert not health["checks"]["unhealthy_check"]["healthy"]


# Integration tests (require Temporal server)
class TestTemporalIntegration:
    """Integration tests requiring Temporal server."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires Temp server")
    async def test_full_workflow_execution(self):
        """Test full workflow execution with Temporal."""
        # This test requires a running Temporal server
        engine = WorkflowEngine()
        await engine.connect()

        try:
            engine.register_workflow(SequentialWorkflow)
            asyncio.create_task(engine.start_worker())

            await asyncio.sleep(1)  # Wait for worker to start

            run_id = await engine.execute_workflow(
                workflow_id="integration-test-001",
                workflow_type="SequentialWorkflow",
                input_data={"tasks": []},
            )

            assert run_id is not None

            # Wait for completion
            await asyncio.sleep(2)

            status = await engine.get_workflow_status("integration-test-001")
            assert status == WorkflowStatus.COMPLETED

        finally:
            await engine.shutdown()
