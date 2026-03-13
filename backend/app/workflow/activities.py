"""Workflow Activities - Activity definitions for agent operations."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional, Union

from temporalio import activity

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ActivityStatus(str, Enum):
    """Activity execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class ActivityInput:
    """Input data for an activity.

    Attributes:
        activity_id: Unique activity ID.
        activity_type: Type of activity.
        input_data: Input data for the activity.
        context: Activity context metadata.
        retry_count: Current retry count.
        max_retries: Maximum retry attempts.
        timeout: Timeout in seconds.
    """

    activity_id: str
    activity_type: str
    input_data: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    timeout: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "activity_id": self.activity_id,
            "activity_type": self.activity_type,
            "input_data": self.input_data,
            "context": self.context,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
        }


@dataclass
class ActivityOutput:
    """Output data from an activity.

    Attributes:
        activity_id: Activity ID.
        status: Execution status.
        output_data: Output data from the activity.
        error_message: Error message if failed.
        started_at: Start timestamp.
        completed_at: Completion timestamp.
        duration_ms: Execution duration in milliseconds.
        metadata: Additional metadata.
    """

    activity_id: str
    status: ActivityStatus
    output_data: dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "activity_id": self.activity_id,
            "status": self.status.value,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }

    @classmethod
    def success(
        cls,
        activity_id: str,
        output_data: dict[str, Any],
        started_at: datetime,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ActivityOutput:
        """Create a success output."""
        completed_at = datetime.now(timezone.utc)
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)
        return cls(
            activity_id=activity_id,
            status=ActivityStatus.COMPLETED,
            output_data=output_data,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )

    @classmethod
    def failure(
        cls,
        activity_id: str,
        error_message: str,
        started_at: datetime,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ActivityOutput:
        """Create a failure output."""
        completed_at = datetime.now(timezone.utc)
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)
        return cls(
            activity_id=activity_id,
            status=ActivityStatus.FAILED,
            error_message=error_message,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )


@activity.defn
async def agent_activity(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a single agent task.

    This activity executes an agent with the provided input data.

    Args:
        input_data: Activity input data containing:
            - agent_id: Agent ID to execute
            - task_type: Type of task
            - payload: Task payload

    Returns:
        dict: Activity output with execution results.

    Raises:
        Exception: If agent execution fails.
    """
    activity_info = activity.info()
    logger.info(
        f"Executing agent activity: {activity_info.workflow_id} - {input_data.get('agent_id')}"
    )

    started_at = datetime.now(timezone.utc)

    try:
        # Extract agent execution parameters
        agent_id = input_data.get("agent_id", "")
        task_type = input_data.get("task_type", "")
        payload = input_data.get("payload", {})

        if not agent_id:
            raise ValueError("agent_id is required")

        # TODO: Integrate with actual agent execution
        # This is a placeholder for agent execution logic
        # In production, this would call the AgentOrchestrator or AgentService

        logger.info(f"Executing agent {agent_id} with task type {task_type}")

        # Simulate agent execution (replace with actual agent call)
        await asyncio.sleep(0.1)

        result = {
            "agent_id": agent_id,
            "task_type": task_type,
            "success": True,
            "result": f"Agent {agent_id} completed task {task_type}",
            "data": payload,
        }

        output = ActivityOutput.success(
            activity_id=activity_info.activity_id,
            output_data=result,
            started_at=started_at,
        )

        logger.info(f"Agent activity completed: {activity_info.activity_id}")
        return output.to_dict()

    except Exception as e:
        logger.error(f"Agent activity failed: {e}", exc_info=True)
        output = ActivityOutput.failure(
            activity_id=activity_info.activity_id,
            error_message=str(e),
            started_at=started_at,
        )
        return output.to_dict()


@activity.defn
async def parallel_activity(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute multiple activities in parallel.

    This activity spawns multiple sub-activities and waits for all to complete.

    Args:
        input_data: Activity input data containing:
            - activities: List of activity definitions to execute
            - fail_fast: Whether to fail on first error (default: False)

    Returns:
        dict: Activity output with results from all sub-activities.
    """
    activity_info = activity.info()
    logger.info(f"Executing parallel activity: {activity_info.workflow_id}")

    started_at = datetime.now(timezone.utc)

    try:
        activities = input_data.get("activities", [])
        fail_fast = input_data.get("fail_fast", False)

        if not activities:
            return ActivityOutput.success(
                activity_id=activity_info.activity_id,
                output_data={"results": []},
                started_at=started_at,
            ).to_dict()

        # Execute activities in parallel
        # Note: In Temporal, we use workflow logic for parallel execution
        # This activity is a placeholder for workflow-level parallel logic

        results = []
        errors = []

        for idx, act in enumerate(activities):
            try:
                # Execute each sub-activity
                # In production, this would use workflow parallel execution
                logger.info(f"Executing parallel sub-activity {idx + 1}/{len(activities)}")
                await asyncio.sleep(0.05)  # Simulate execution

                results.append(
                    {
                        "index": idx,
                        "success": True,
                        "result": f"Activity {idx} completed",
                    }
                )
            except Exception as e:
                error_msg = f"Activity {idx} failed: {e}"
                logger.error(error_msg)
                errors.append({"index": idx, "error": str(e)})

                if fail_fast:
                    raise

        output_data = {
            "results": results,
            "errors": errors,
            "total": len(activities),
            "successful": len(results),
            "failed": len(errors),
        }

        output = ActivityOutput.success(
            activity_id=activity_info.activity_id,
            output_data=output_data,
            started_at=started_at,
        )

        logger.info(f"Parallel activity completed: {len(results)}/{len(activities)} successful")
        return output.to_dict()

    except Exception as e:
        logger.error(f"Parallel activity failed: {e}", exc_info=True)
        output = ActivityOutput.failure(
            activity_id=activity_info.activity_id,
            error_message=str(e),
            started_at=started_at,
        )
        return output.to_dict()


@activity.defn
async def sequential_activity(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute activities in sequence.

    This activity executes sub-activities one after another, passing output to input.

    Args:
        input_data: Activity input data containing:
            - activities: List of activity definitions to execute
            - pass_output: Whether to pass output between activities (default: True)

    Returns:
        dict: Activity output with final result.
    """
    activity_info = activity.info()
    logger.info(f"Executing sequential activity: {activity_info.workflow_id}")

    started_at = datetime.now(timezone.utc)

    try:
        activities = input_data.get("activities", [])
        pass_output = input_data.get("pass_output", True)

        if not activities:
            return ActivityOutput.success(
                activity_id=activity_info.activity_id,
                output_data={"result": None},
                started_at=started_at,
            ).to_dict()

        current_data = input_data.get("initial_data", {})
        results = []

        for idx, act in enumerate(activities):
            try:
                logger.info(f"Executing sequential sub-activity {idx + 1}/{len(activities)}")
                await asyncio.sleep(0.05)  # Simulate execution

                result = {
                    "index": idx,
                    "success": True,
                    "result": f"Activity {idx} completed",
                }

                if pass_output:
                    current_data = {**current_data, **result}

                results.append(result)

            except Exception as e:
                logger.error(f"Sequential activity {idx} failed: {e}")
                raise

        output_data = {
            "final_result": current_data,
            "results": results,
            "total": len(activities),
        }

        output = ActivityOutput.success(
            activity_id=activity_info.activity_id,
            output_data=output_data,
            started_at=started_at,
        )

        logger.info(f"Sequential activity completed: {len(activities)} steps")
        return output.to_dict()

    except Exception as e:
        logger.error(f"Sequential activity failed: {e}", exc_info=True)
        output = ActivityOutput.failure(
            activity_id=activity_info.activity_id,
            error_message=str(e),
            started_at=started_at,
        )
        return output.to_dict()


@activity.defn
async def conditional_activity(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute based on conditions.

    This activity evaluates conditions and executes the appropriate branch.

    Args:
        input_data: Activity input data containing:
            - conditions: List of condition definitions
            - branches: Branch definitions for each condition
            - default_branch: Default branch if no conditions match

    Returns:
        dict: Activity output from the executed branch.
    """
    activity_info = activity.info()
    logger.info(f"Executing conditional activity: {activity_info.workflow_id}")

    started_at = datetime.now(timezone.utc)

    try:
        conditions = input_data.get("conditions", [])
        branches = input_data.get("branches", {})
        default_branch = input_data.get("default_branch")
        context_data = input_data.get("context", {})

        # Evaluate conditions
        matched_branch = None
        for condition in conditions:
            condition_name = condition.get("name", "")
            condition_expr = condition.get("expression", "")

            # Simple condition evaluation (in production, use a proper expression engine)
            if _evaluate_condition(condition_expr, context_data):
                matched_branch = branches.get(condition_name)
                logger.info(f"Condition {condition_name} matched, executing branch")
                break

        if matched_branch is None and default_branch:
            matched_branch = default_branch
            logger.info("No conditions matched, executing default branch")

        if matched_branch is None:
            return ActivityOutput.success(
                activity_id=activity_info.activity_id,
                output_data={"result": None, "matched_branch": None},
                started_at=started_at,
            ).to_dict()

        # Execute the matched branch
        logger.info(f"Executing branch: {matched_branch.get('name', 'unknown')}")
        await asyncio.sleep(0.05)  # Simulate execution

        output_data = {
            "result": matched_branch.get("result", {}),
            "matched_branch": matched_branch.get("name"),
        }

        output = ActivityOutput.success(
            activity_id=activity_info.activity_id,
            output_data=output_data,
            started_at=started_at,
        )

        logger.info(f"Conditional activity completed: branch {matched_branch.get('name')}")
        return output.to_dict()

    except Exception as e:
        logger.error(f"Conditional activity failed: {e}", exc_info=True)
        output = ActivityOutput.failure(
            activity_id=activity_info.activity_id,
            error_message=str(e),
            started_at=started_at,
        )
        return output.to_dict()


def _evaluate_condition(expression: str, context: dict[str, Any]) -> bool:
    """Evaluate a condition expression.

    Args:
        expression: Condition expression string.
        context: Context data for evaluation.

    Returns:
        bool: Whether the condition is true.
    """
    # Simple condition evaluation (in production, use a proper expression engine)
    # Supports basic comparisons: field == value, field > value, etc.

    if not expression:
        return False

    try:
        # Safe evaluation using context variables
        # This is a simplified implementation
        for key, value in context.items():
            if f"{key} ==" in expression or f"{key}==" in expression:
                # Extract the value to compare
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


@activity.defn
async def retry_activity(input_data: dict[str, Any]) -> dict[str, Any]:
    """Activity with retry logic.

    This activity implements retry logic with exponential backoff.

    Args:
        input_data: Activity input data containing:
            - activity: Activity definition to execute
            - retry_policy: Retry policy configuration
            - initial_data: Initial input data

    Returns:
        dict: Activity output with retry metadata.
    """
    activity_info = activity.info()
    logger.info(f"Executing retry activity: {activity_info.workflow_id}")

    started_at = datetime.now(timezone.utc)

    try:
        activity_def = input_data.get("activity", {})
        retry_policy = input_data.get("retry_policy", {})
        initial_data = input_data.get("initial_data", {})

        max_retries = retry_policy.get("max_retries", 3)
        initial_delay = retry_policy.get("initial_delay", 1.0)
        max_delay = retry_policy.get("max_delay", 60.0)
        exponential_base = retry_policy.get("exponential_base", 2.0)

        last_error: Optional[str] = None

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Retry activity attempt {attempt + 1}/{max_retries + 1}")

                # Execute the activity
                await asyncio.sleep(0.05)  # Simulate execution

                # Success
                output_data = {
                    "result": "Activity completed successfully",
                    "attempts": attempt + 1,
                    "retries": attempt,
                }

                output = ActivityOutput.success(
                    activity_id=activity_info.activity_id,
                    output_data=output_data,
                    started_at=started_at,
                    metadata={"attempts": attempt + 1},
                )

                logger.info(
                    f"Retry activity succeeded on attempt {attempt + 1}"
                )
                return output.to_dict()

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} failed: {e}")

                if attempt < max_retries:
                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (exponential_base**attempt), max_delay)
                    logger.info(f"Retrying in {delay:.2f} seconds")
                    await asyncio.sleep(delay)

        # All retries exhausted
        raise Exception(f"All retries exhausted. Last error: {last_error}")

    except Exception as e:
        logger.error(f"Retry activity failed after all retries: {e}", exc_info=True)
        output = ActivityOutput.failure(
            activity_id=activity_info.activity_id,
            error_message=str(e),
            started_at=started_at,
        )
        return output.to_dict()


@activity.defn
async def validation_activity(input_data: dict[str, Any]) -> dict[str, Any]:
    """Validate activity outputs.

    This activity validates output data against a schema or rules.

    Args:
        input_data: Activity input data containing:
            - data: Data to validate
            - schema: Validation schema
            - rules: Validation rules

    Returns:
        dict: Activity output with validation results.
    """
    activity_info = activity.info()
    logger.info(f"Executing validation activity: {activity_info.workflow_id}")

    started_at = datetime.now(timezone.utc)

    try:
        data = input_data.get("data", {})
        schema = input_data.get("schema", {})
        rules = input_data.get("rules", [])

        errors = []
        warnings = []

        # Validate against schema
        if schema:
            schema_errors = _validate_schema(data, schema)
            errors.extend(schema_errors)

        # Validate against rules
        for rule in rules:
            rule_result = _validate_rule(data, rule)
            if not rule_result.get("valid", True):
                if rule.get("severity", "error") == "warning":
                    warnings.append(rule_result.get("message", "Rule violation"))
                else:
                    errors.append(rule_result.get("message", "Rule violation"))

        output_data = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings),
        }

        if errors:
            logger.warning(f"Validation failed with {len(errors)} errors")
            # Return success but with validation errors
            output = ActivityOutput.success(
                activity_id=activity_info.activity_id,
                output_data=output_data,
                started_at=started_at,
            )
        else:
            logger.info("Validation passed")
            output = ActivityOutput.success(
                activity_id=activity_info.activity_id,
                output_data=output_data,
                started_at=started_at,
            )

        return output.to_dict()

    except Exception as e:
        logger.error(f"Validation activity failed: {e}", exc_info=True)
        output = ActivityOutput.failure(
            activity_id=activity_info.activity_id,
            error_message=str(e),
            started_at=started_at,
        )
        return output.to_dict()


def _validate_schema(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Validate data against a schema.

    Args:
        data: Data to validate.
        schema: Schema definition.

    Returns:
        list[str]: List of validation errors.
    """
    errors = []

    # Simple schema validation (in production, use jsonschema or similar)
    required_fields = schema.get("required", [])
    properties = schema.get("properties", {})

    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    for field, field_schema in properties.items():
        if field in data:
            field_type = field_schema.get("type")
            if field_type:
                actual_type = type(data[field]).__name__
                if field_type == "string" and not isinstance(data[field], str):
                    errors.append(f"Field {field} must be a string")
                elif field_type == "number" and not isinstance(
                    data[field], (int, float)
                ):
                    errors.append(f"Field {field} must be a number")
                elif field_type == "boolean" and not isinstance(data[field], bool):
                    errors.append(f"Field {field} must be a boolean")
                elif field_type == "array" and not isinstance(data[field], list):
                    errors.append(f"Field {field} must be an array")
                elif field_type == "object" and not isinstance(data[field], dict):
                    errors.append(f"Field {field} must be an object")

    return errors


def _validate_rule(
    data: dict[str, Any], rule: dict[str, Any]
) -> dict[str, Any]:
    """Validate data against a rule.

    Args:
        data: Data to validate.
        rule: Rule definition.

    Returns:
        dict: Validation result with 'valid' and 'message' keys.
    """
    rule_type = rule.get("type", "")
    message = rule.get("message", "Rule violation")

    if rule_type == "custom":
        # Custom validation function (in production, use registered validators)
        field = rule.get("field", "")
        condition = rule.get("condition", "")

        if field in data:
            value = data[field]
            # Simple condition evaluation
            if condition.startswith(">"):
                threshold = float(condition[1:])
                if not value > threshold:
                    return {"valid": False, "message": message}
            elif condition.startswith("<"):
                threshold = float(condition[1:])
                if not value < threshold:
                    return {"valid": False, "message": message}
            elif condition.startswith("=="):
                expected = condition[2:].strip().strip('"\'')
                if not str(value) == expected:
                    return {"valid": False, "message": message}

    return {"valid": True, "message": message}
