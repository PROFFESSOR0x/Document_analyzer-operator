"""Workflow Patterns - Common workflow patterns implementation."""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Optional

from temporalio import workflow
from temporalio.common import RetryPolicy

from app.workflow.activities import (
    ActivityInput,
    ActivityOutput,
    ActivityStatus,
)

with workflow.unsafe.imports_passed_through():
    from app.core.logging_config import get_logger

logger = get_logger(__name__)


@workflow.defn
class SequentialWorkflow:
    """Linear task execution workflow.

    Executes tasks in a sequential order, where each task depends on
    the completion of the previous one.

    Workflow Input:
        tasks: List of task definitions to execute in order
        initial_data: Initial data to pass to the first task
        pass_output: Whether to pass output between tasks

    Workflow Output:
        dict: Final result with all task outputs
    """

    @workflow.run
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the sequential workflow.

        Args:
            input_data: Workflow input data.

        Returns:
            dict: Workflow execution results.
        """
        workflow.logger.info(f"Starting sequential workflow: {workflow.info().workflow_id}")

        tasks = input_data.get("tasks", [])
        initial_data = input_data.get("initial_data", {})
        pass_output = input_data.get("pass_output", True)

        if not tasks:
            return {"status": "completed", "result": None, "task_results": []}

        current_data = initial_data
        task_results = []

        for idx, task in enumerate(tasks):
            task_id = task.get("id", f"task-{idx}")
            task_type = task.get("type", "agent_activity")
            task_config = task.get("config", {})

            workflow.logger.info(f"Executing task {idx + 1}/{len(tasks)}: {task_id}")

            # Execute task
            result = await workflow.execute_activity(
                task_type,
                {**task_config, "input_data": current_data},
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    backoff_coefficient=2.0,
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                ),
            )

            # Check for failure
            if isinstance(result, dict):
                status = result.get("status", "completed")
                if status == "failed":
                    workflow.logger.error(f"Task {task_id} failed: {result.get('error_message')}")
                    return {
                        "status": "failed",
                        "failed_at": idx,
                        "failed_task": task_id,
                        "error": result.get("error_message"),
                        "task_results": task_results,
                    }

                # Update current data for next task
                if pass_output and result.get("output_data"):
                    current_data = {**current_data, **result.get("output_data", {})}

            task_results.append(
                {
                    "task_id": task_id,
                    "result": result,
                    "status": "completed",
                }
            )

            # Update workflow progress
            progress = int(((idx + 1) / len(tasks)) * 100)
            workflow.logger.info(f"Progress: {progress}%")

        workflow.logger.info("Sequential workflow completed")
        return {
            "status": "completed",
            "result": current_data,
            "task_results": task_results,
        }

    @workflow.signal
    async def cancel(self) -> None:
        """Signal to cancel the workflow."""
        workflow.logger.info("Received cancel signal")
        workflow.cancel()


@workflow.defn
class ParallelWorkflow:
    """Fan-out/fan-in pattern workflow.

    Executes multiple tasks in parallel and aggregates the results.

    Workflow Input:
        tasks: List of task definitions to execute in parallel
        aggregation_strategy: How to aggregate results (all, any, majority)
        fail_fast: Whether to fail on first error

    Workflow Output:
        dict: Aggregated results from all parallel tasks
    """

    @workflow.run
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the parallel workflow.

        Args:
            input_data: Workflow input data.

        Returns:
            dict: Workflow execution results.
        """
        workflow.logger.info(f"Starting parallel workflow: {workflow.info().workflow_id}")

        tasks = input_data.get("tasks", [])
        aggregation_strategy = input_data.get("aggregation_strategy", "all")
        fail_fast = input_data.get("fail_fast", False)

        if not tasks:
            return {"status": "completed", "result": [], "successful": 0, "failed": 0}

        # Create parallel task executions
        task_handles = []
        for idx, task in enumerate(tasks):
            task_id = task.get("id", f"task-{idx}")
            task_type = task.get("type", "agent_activity")
            task_config = task.get("config", {})

            workflow.logger.info(f"Starting parallel task: {task_id}")

            handle = workflow.execute_activity(
                task_type,
                {**task_config, "input_data": input_data.get("initial_data", {})},
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    backoff_coefficient=2.0,
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                ),
            )

            task_handles.append((task_id, handle))

        # Wait for all tasks to complete
        results = []
        errors = []

        for task_id, handle in task_handles:
            try:
                result = await handle
                results.append({"task_id": task_id, "result": result, "status": "completed"})
                workflow.logger.info(f"Task {task_id} completed")
            except Exception as e:
                error_msg = str(e)
                workflow.logger.error(f"Task {task_id} failed: {error_msg}")
                errors.append({"task_id": task_id, "error": error_msg})

                if fail_fast:
                    workflow.logger.info("Fail-fast enabled, cancelling remaining tasks")
                    return {
                        "status": "failed",
                        "failed_task": task_id,
                        "error": error_msg,
                        "results": results,
                        "errors": errors,
                    }

        # Aggregate results based on strategy
        aggregated = self._aggregate_results(results, errors, aggregation_strategy)

        workflow.logger.info(
            f"Parallel workflow completed: {len(results)} successful, {len(errors)} failed"
        )

        return {
            "status": "completed" if not errors else "partial",
            "result": aggregated,
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors,
        }

    def _aggregate_results(
        self,
        results: list[dict],
        errors: list[dict],
        strategy: str,
    ) -> Any:
        """Aggregate results based on strategy.

        Args:
            results: List of successful results.
            errors: List of errors.
            strategy: Aggregation strategy.

        Returns:
            Aggregated results.
        """
        if strategy == "all":
            return [r.get("result") for r in results]
        elif strategy == "first":
            return results[0].get("result") if results else None
        elif strategy == "merge":
            merged = {}
            for r in results:
                result_data = r.get("result", {})
                if isinstance(result_data, dict):
                    merged.update(result_data)
            return merged
        else:
            return [r.get("result") for r in results]

    @workflow.signal
    async def cancel(self) -> None:
        """Signal to cancel the workflow."""
        workflow.logger.info("Received cancel signal")
        workflow.cancel()


@workflow.defn
class ConditionalWorkflow:
    """Branching workflow based on conditions.

    Evaluates conditions and executes the appropriate branch.

    Workflow Input:
        conditions: List of condition definitions
        branches: Branch definitions for each condition
        default_branch: Default branch if no conditions match
        context: Context data for condition evaluation

    Workflow Output:
        dict: Result from the executed branch
    """

    @workflow.run
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the conditional workflow.

        Args:
            input_data: Workflow input data.

        Returns:
            dict: Workflow execution results.
        """
        workflow.logger.info(f"Starting conditional workflow: {workflow.info().workflow_id}")

        conditions = input_data.get("conditions", [])
        branches = input_data.get("branches", {})
        default_branch = input_data.get("default_branch")
        context = input_data.get("context", {})

        # Evaluate conditions
        matched_branch = None
        for condition in conditions:
            condition_name = condition.get("name", "")
            condition_expr = condition.get("expression", "")

            if self._evaluate_condition(condition_expr, context):
                matched_branch = branches.get(condition_name)
                workflow.logger.info(f"Condition {condition_name} matched")
                break

        if matched_branch is None and default_branch:
            matched_branch = default_branch
            workflow.logger.info("No conditions matched, executing default branch")

        if matched_branch is None:
            return {
                "status": "completed",
                "result": None,
                "matched_branch": None,
                "message": "No matching branch",
            }

        # Execute the matched branch
        branch_type = matched_branch.get("type", "sequential")
        branch_tasks = matched_branch.get("tasks", [])

        workflow.logger.info(f"Executing branch: {matched_branch.get('name', 'unknown')}")

        # Execute branch based on type
        if branch_type == "sequential":
            result = await self._execute_sequential_branch(branch_tasks, context)
        elif branch_type == "parallel":
            result = await self._execute_parallel_branch(branch_tasks, context)
        else:
            result = await self._execute_sequential_branch(branch_tasks, context)

        workflow.logger.info(f"Conditional workflow completed: {matched_branch.get('name')}")

        return {
            "status": "completed",
            "result": result,
            "matched_branch": matched_branch.get("name"),
        }

    def _evaluate_condition(self, expression: str, context: dict[str, Any]) -> bool:
        """Evaluate a condition expression.

        Args:
            expression: Condition expression.
            context: Context data.

        Returns:
            bool: Whether condition is true.
        """
        # Simple condition evaluation
        if not expression:
            return False

        try:
            for key, value in context.items():
                if f"{key} ==" in expression or f"{key}==" in expression:
                    parts = expression.split("==")
                    if len(parts) == 2:
                        expected = parts[1].strip().strip('"\'')
                        return str(value) == expected
                elif f"{key} >" in expression or f"{key}>" in expression:
                    parts = expression.split(">")
                    if len(parts) == 2:
                        threshold = float(parts[1].strip())
                        return float(value) > threshold
                elif f"{key} <" in expression or f"{key}<" in expression:
                    parts = expression.split("<")
                    if len(parts) == 2:
                        threshold = float(parts[1].strip())
                        return float(value) < threshold

            return False
        except Exception:
            return False

    async def _execute_sequential_branch(
        self, tasks: list[dict], context: dict[str, Any]
    ) -> Any:
        """Execute a sequential branch.

        Args:
            tasks: List of tasks.
            context: Context data.

        Returns:
            Branch execution result.
        """
        current_data = context
        for idx, task in enumerate(tasks):
            task_type = task.get("type", "agent_activity")
            task_config = task.get("config", {})

            result = await workflow.execute_activity(
                task_type,
                {**task_config, "input_data": current_data},
                start_to_close_timeout=timedelta(minutes=10),
            )

            if isinstance(result, dict) and result.get("output_data"):
                current_data = {**current_data, **result.get("output_data", {})}

        return current_data

    async def _execute_parallel_branch(
        self, tasks: list[dict], context: dict[str, Any]
    ) -> Any:
        """Execute a parallel branch.

        Args:
            tasks: List of tasks.
            context: Context data.

        Returns:
            Branch execution result.
        """
        task_handles = []
        for task in tasks:
            task_type = task.get("type", "agent_activity")
            task_config = task.get("config", {})

            handle = workflow.execute_activity(
                task_type,
                {**task_config, "input_data": context},
                start_to_close_timeout=timedelta(minutes=10),
            )
            task_handles.append(handle)

        results = await workflow.gather(*task_handles)
        return {"parallel_results": results}

    @workflow.signal
    async def cancel(self) -> None:
        """Signal to cancel the workflow."""
        workflow.logger.info("Received cancel signal")
        workflow.cancel()


@workflow.defn
class IterativeWorkflow:
    """Loop-based execution workflow.

    Executes tasks in a loop until a condition is met or max iterations reached.

    Workflow Input:
        task: Task definition to execute iteratively
        loop_condition: Condition to continue looping
        max_iterations: Maximum number of iterations
        initial_data: Initial data for first iteration

    Workflow Output:
        dict: Results from all iterations
    """

    @workflow.run
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the iterative workflow.

        Args:
            input_data: Workflow input data.

        Returns:
            dict: Workflow execution results.
        """
        workflow.logger.info(f"Starting iterative workflow: {workflow.info().workflow_id}")

        task = input_data.get("task", {})
        loop_condition = input_data.get("loop_condition", {})
        max_iterations = input_data.get("max_iterations", 10)
        current_data = input_data.get("initial_data", {})

        task_type = task.get("type", "agent_activity")
        task_config = task.get("config", {})

        iteration_results = []
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            workflow.logger.info(f"Executing iteration {iteration}/{max_iterations}")

            # Execute task
            result = await workflow.execute_activity(
                task_type,
                {**task_config, "input_data": current_data},
                start_to_close_timeout=timedelta(minutes=10),
            )

            iteration_results.append(
                {
                    "iteration": iteration,
                    "result": result,
                }
            )

            # Update current data
            if isinstance(result, dict) and result.get("output_data"):
                current_data = {**current_data, **result.get("output_data", {})}

            # Check loop condition
            if not self._check_loop_condition(loop_condition, current_data):
                workflow.logger.info(f"Loop condition not met, stopping at iteration {iteration}")
                break

        workflow.logger.info(f"Iterative workflow completed: {iteration} iterations")

        return {
            "status": "completed",
            "result": current_data,
            "iterations": iteration,
            "iteration_results": iteration_results,
        }

    def _check_loop_condition(
        self, condition: dict[str, Any], data: dict[str, Any]
    ) -> bool:
        """Check if loop should continue.

        Args:
            condition: Loop condition definition.
            data: Current data.

        Returns:
            bool: Whether to continue looping.
        """
        condition_type = condition.get("type", "always")

        if condition_type == "always":
            return True
        elif condition_type == "field_exists":
            field = condition.get("field", "")
            return field in data and data[field] is not None
        elif condition_type == "field_not_empty":
            field = condition.get("field", "")
            return field in data and bool(data[field])
        elif condition_type == "custom":
            # Custom condition logic
            return True

        return True

    @workflow.signal
    async def cancel(self) -> None:
        """Signal to cancel the workflow."""
        workflow.logger.info("Received cancel signal")
        workflow.cancel()


@workflow.defn
class PipelineWorkflow:
    """Data pipeline pattern workflow.

    Executes a series of data transformation stages.

    Workflow Input:
        stages: List of pipeline stages
        input_data: Initial data to process
        parallel_stages: Which stages can run in parallel

    Workflow Output:
        dict: Final transformed data
    """

    @workflow.run
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the pipeline workflow.

        Args:
            input_data: Workflow input data.

        Returns:
            dict: Workflow execution results.
        """
        workflow.logger.info(f"Starting pipeline workflow: {workflow.info().workflow_id}")

        stages = input_data.get("stages", [])
        current_data = input_data.get("input_data", {})
        parallel_stages = input_data.get("parallel_stages", [])

        if not stages:
            return {"status": "completed", "result": current_data}

        stage_results = []

        for idx, stage in enumerate(stages):
            stage_id = stage.get("id", f"stage-{idx}")
            stage_type = stage.get("type", "agent_activity")
            stage_config = stage.get("config", {})

            workflow.logger.info(f"Executing pipeline stage: {stage_id}")

            # Check if this stage can run in parallel with others
            if stage_id in parallel_stages:
                # Find other parallel stages
                parallel_group = [
                    s
                    for s in stages
                    if s.get("id") in parallel_stages and s.get("id") != stage_id
                ]

                if parallel_group:
                    # Execute parallel stages
                    results = await self._execute_parallel_stages(
                        [stage] + parallel_group, current_data
                    )
                    stage_results.extend(results)
                    continue

            # Execute stage sequentially
            result = await workflow.execute_activity(
                stage_type,
                {**stage_config, "input_data": current_data},
                start_to_close_timeout=timedelta(minutes=10),
            )

            if isinstance(result, dict) and result.get("output_data"):
                current_data = {**current_data, **result.get("output_data", {})}

            stage_results.append(
                {
                    "stage_id": stage_id,
                    "result": result,
                }
            )

        workflow.logger.info("Pipeline workflow completed")

        return {
            "status": "completed",
            "result": current_data,
            "stage_results": stage_results,
        }

    async def _execute_parallel_stages(
        self, stages: list[dict], data: dict[str, Any]
    ) -> list[dict]:
        """Execute stages in parallel.

        Args:
            stages: List of stages to execute.
            data: Input data.

        Returns:
            list: Results from all stages.
        """
        task_handles = []
        stage_ids = []

        for stage in stages:
            stage_type = stage.get("type", "agent_activity")
            stage_config = stage.get("config", {})

            handle = workflow.execute_activity(
                stage_type,
                {**stage_config, "input_data": data},
                start_to_close_timeout=timedelta(minutes=10),
            )
            task_handles.append(handle)
            stage_ids.append(stage.get("id", "unknown"))

        results = await workflow.gather(*task_handles)

        return [
            {"stage_id": stage_id, "result": result}
            for stage_id, result in zip(stage_ids, results)
        ]

    @workflow.signal
    async def cancel(self) -> None:
        """Signal to cancel the workflow."""
        workflow.logger.info("Received cancel signal")
        workflow.cancel()


@workflow.defn
class StatefulWorkflow:
    """Long-running stateful workflow.

    Maintains state across multiple execution steps and supports pausing/resuming.

    Workflow Input:
        initial_state: Initial workflow state
        state_transitions: State transition definitions
        max_duration: Maximum workflow duration in seconds

    Workflow Output:
        dict: Final state and execution history
    """

    def __init__(self) -> None:
        """Initialize the stateful workflow."""
        self.current_state: dict[str, Any] = {}
        self.execution_history: list[dict[str, Any]] = []

    @workflow.run
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the stateful workflow.

        Args:
            input_data: Workflow input data.

        Returns:
            dict: Workflow execution results.
        """
        workflow.logger.info(f"Starting stateful workflow: {workflow.info().workflow_id}")

        self.current_state = input_data.get("initial_state", {})
        state_transitions = input_data.get("state_transitions", [])
        max_duration = input_data.get("max_duration", 3600)

        start_time = workflow.now()

        for transition in state_transitions:
            # Check if we've exceeded max duration
            duration = (workflow.now() - start_time).total_seconds()
            if duration > max_duration:
                workflow.logger.warning("Max duration exceeded, stopping workflow")
                break

            # Check for pause signal
            await self._wait_if_paused()

            # Execute state transition
            from_state = transition.get("from_state")
            to_state = transition.get("to_state")
            action = transition.get("action", {})

            if from_state and self.current_state.get("current") != from_state:
                continue

            workflow.logger.info(f"Transitioning from {from_state} to {to_state}")

            # Execute action
            result = await self._execute_action(action)

            # Update state
            self.current_state["current"] = to_state
            self.current_state["last_updated"] = workflow.now().isoformat()
            self.current_state.update(result)

            # Record in history
            self.execution_history.append(
                {
                    "timestamp": workflow.now().isoformat(),
                    "from_state": from_state,
                    "to_state": to_state,
                    "result": result,
                }
            )

            # Emit state change event
            workflow.logger.info(f"State changed to: {to_state}")

        workflow.logger.info("Stateful workflow completed")

        return {
            "status": "completed",
            "final_state": self.current_state,
            "execution_history": self.execution_history,
        }

    @workflow.signal
    async def pause(self) -> None:
        """Signal to pause the workflow."""
        workflow.logger.info("Received pause signal")
        self.current_state["paused"] = True

    @workflow.signal
    async def resume(self) -> None:
        """Signal to resume the workflow."""
        workflow.logger.info("Received resume signal")
        self.current_state["paused"] = False

    @workflow.signal
    async def cancel(self) -> None:
        """Signal to cancel the workflow."""
        workflow.logger.info("Received cancel signal")
        workflow.cancel()

    @workflow.query
    async def get_state(self) -> dict[str, Any]:
        """Query the current state.

        Returns:
            dict: Current workflow state.
        """
        return self.current_state

    @workflow.query
    async def get_history(self) -> list[dict[str, Any]]:
        """Query the execution history.

        Returns:
            list: Execution history.
        """
        return self.execution_history

    async def _wait_if_paused(self) -> None:
        """Wait if workflow is paused."""
        while self.current_state.get("paused", False):
            await workflow.sleep(1)

    async def _execute_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """Execute a state transition action.

        Args:
            action: Action definition.

        Returns:
            dict: Action result.
        """
        action_type = action.get("type", "agent_activity")
        action_config = action.get("config", {})

        result = await workflow.execute_activity(
            action_type,
            action_config,
            start_to_close_timeout=timedelta(minutes=10),
        )

        if isinstance(result, dict):
            return result.get("output_data", {})

        return {}
