"""Workflow API routes."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ActiveUser
from app.db.session import get_db
from app.models.workflow import Workflow
from app.core.logging_config import get_logger
from app.workflow.engine import (
    WorkflowEngine,
    WorkflowStatus,
    get_workflow_engine,
)
from app.workflow.management import (
    WorkflowManager,
    WorkflowScheduler,
    WorkflowMonitor,
    WorkflowHistory,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


# Global instances (in production, use dependency injection container)
_workflow_manager: Optional[WorkflowManager] = None
_workflow_scheduler: Optional[WorkflowScheduler] = None
_workflow_monitor: Optional[WorkflowMonitor] = None
_workflow_history: Optional[WorkflowHistory] = None


def get_workflow_manager() -> WorkflowManager:
    """Get workflow manager instance."""
    global _workflow_manager
    if _workflow_manager is None:
        engine = get_workflow_engine()
        _workflow_manager = WorkflowManager(engine)
    return _workflow_manager


def get_workflow_scheduler() -> WorkflowScheduler:
    """Get workflow scheduler instance."""
    global _workflow_scheduler
    if _workflow_scheduler is None:
        _workflow_scheduler = WorkflowScheduler(get_workflow_manager())
    return _workflow_scheduler


def get_workflow_monitor() -> WorkflowMonitor:
    """Get workflow monitor instance."""
    global _workflow_monitor
    if _workflow_monitor is None:
        _workflow_monitor = WorkflowMonitor(get_workflow_manager())
    return _workflow_monitor


def get_workflow_history() -> WorkflowHistory:
    """Get workflow history instance."""
    global _workflow_history
    if _workflow_history is None:
        _workflow_history = WorkflowHistory()
    return _workflow_history


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_type: str,
    input_data: dict,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    workflow_manager: Annotated[WorkflowManager, Depends(get_workflow_manager)],
    scheduled_at: Optional[str] = None,
    cron_expression: Optional[str] = None,
) -> dict:
    """Create a new workflow execution.

    Args:
        workflow_type: Type of workflow to create.
        input_data: Input data for the workflow.
        current_user: Current authenticated user.
        db: Database session.
        workflow_manager: Workflow manager.
        scheduled_at: Optional scheduled execution time (ISO format).
        cron_expression: Optional cron expression for recurring workflows.

    Returns:
        dict: Created workflow execution details.

    Raises:
        HTTPException: If workflow type not found or creation fails.
    """
    try:
        from datetime import datetime

        scheduled_datetime = None
        if scheduled_at:
            scheduled_datetime = datetime.fromisoformat(scheduled_at)

        execution = await workflow_manager.create_workflow(
            workflow_type=workflow_type,
            input_data=input_data,
            context={"user_id": current_user.id},
            scheduled_at=scheduled_datetime,
            cron_expression=cron_expression,
            metadata={"owner": current_user.email},
        )

        logger.info(
            f"Created workflow execution: {execution.execution_id} "
            f"(type: {workflow_type}, user: {current_user.id})"
        )

        return {
            "execution_id": execution.execution_id,
            "workflow_type": workflow_type,
            "status": execution.state.status.value,
            "created_at": execution.created_at.isoformat(),
            "scheduled_at": execution.scheduled_at.isoformat()
            if execution.scheduled_at
            else None,
            "cron_expression": execution.cron_expression,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workflow",
        )


@router.get("")
async def list_workflows(
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    workflow_manager: Annotated[WorkflowManager, Depends(get_workflow_manager)],
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    workflow_type_filter: Optional[str] = Query(
        None, description="Filter by workflow type"
    ),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[dict]:
    """List workflow executions.

    Args:
        current_user: Current authenticated user.
        db: Database session.
        workflow_manager: Workflow manager.
        status_filter: Optional status filter.
        workflow_type_filter: Optional workflow type filter.
        limit: Maximum number of results.
        offset: Number of results to skip.

    Returns:
        list: List of workflow executions.
    """
    try:
        status_enum = WorkflowStatus(status_filter) if status_filter else None

        executions = workflow_manager.list_executions(
            status_filter=status_enum,
            workflow_type_filter=workflow_type_filter,
        )

        # Apply pagination
        paginated = executions[offset : offset + limit]

        return [
            {
                "execution_id": e.execution_id,
                "workflow_type": e.workflow_type,
                "status": e.state.status.value,
                "progress": e.state.progress,
                "created_at": e.created_at.isoformat(),
                "started_at": e.started_at.isoformat() if e.started_at else None,
            }
            for e in paginated
        ]

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list workflows",
        )


@router.get("/{execution_id}")
async def get_workflow(
    execution_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    workflow_manager: Annotated[WorkflowManager, Depends(get_workflow_manager)],
) -> dict:
    """Get workflow execution details.

    Args:
        execution_id: Workflow execution ID.
        current_user: Current authenticated user.
        db: Database session.
        workflow_manager: Workflow manager.

    Returns:
        dict: Workflow execution details.

    Raises:
        HTTPException: If workflow not found.
    """
    try:
        state = await workflow_manager.get_workflow_status(execution_id)

        return {
            "execution_id": execution_id,
            "status": state.status.value,
            "progress": state.progress,
            "input_data": state.input_data,
            "output_data": state.output_data,
            "current_task": state.current_task,
            "completed_tasks": state.completed_tasks,
            "failed_tasks": state.failed_tasks,
            "error_message": state.error_message,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to get workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflow",
        )


@router.post("/{execution_id}/execute")
async def execute_workflow(
    execution_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    workflow_manager: Annotated[WorkflowManager, Depends(get_workflow_manager)],
) -> dict:
    """Start workflow execution.

    Args:
        execution_id: Workflow execution ID.
        current_user: Current authenticated user.
        db: Database session.
        workflow_manager: Workflow manager.

    Returns:
        dict: Execution result.

    Raises:
        HTTPException: If workflow not found or cannot be started.
    """
    try:
        run_id = await workflow_manager.start_workflow(execution_id)

        logger.info(
            f"Started workflow execution: {execution_id} (run_id: {run_id})"
        )

        return {
            "execution_id": execution_id,
            "status": "started",
            "run_id": run_id,
            "message": "Workflow execution started",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to start workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start workflow",
        )


@router.post("/{execution_id}/pause")
async def pause_workflow(
    execution_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    workflow_manager: Annotated[WorkflowManager, Depends(get_workflow_manager)],
) -> dict:
    """Pause workflow execution.

    Args:
        execution_id: Workflow execution ID.
        current_user: Current authenticated user.
        db: Database session.
        workflow_manager: Workflow manager.

    Returns:
        dict: Pause result.

    Raises:
        HTTPException: If workflow not found or cannot be paused.
    """
    try:
        await workflow_manager.pause_workflow(execution_id)

        logger.info(f"Paused workflow execution: {execution_id}")

        return {
            "execution_id": execution_id,
            "status": "paused",
            "message": "Workflow execution paused",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to pause workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause workflow",
        )


@router.post("/{execution_id}/resume")
async def resume_workflow(
    execution_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    workflow_manager: Annotated[WorkflowManager, Depends(get_workflow_manager)],
) -> dict:
    """Resume paused workflow execution.

    Args:
        execution_id: Workflow execution ID.
        current_user: Current authenticated user.
        db: Database session.
        workflow_manager: Workflow manager.

    Returns:
        dict: Resume result.

    Raises:
        HTTPException: If workflow not found or cannot be resumed.
    """
    try:
        await workflow_manager.resume_workflow(execution_id)

        logger.info(f"Resumed workflow execution: {execution_id}")

        return {
            "execution_id": execution_id,
            "status": "resumed",
            "message": "Workflow execution resumed",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to resume workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume workflow",
        )


@router.post("/{execution_id}/cancel")
async def cancel_workflow(
    execution_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    workflow_manager: Annotated[WorkflowManager, Depends(get_workflow_manager)],
) -> dict:
    """Cancel workflow execution.

    Args:
        execution_id: Workflow execution ID.
        current_user: Current authenticated user.
        db: Database session.
        workflow_manager: Workflow manager.

    Returns:
        dict: Cancel result.

    Raises:
        HTTPException: If workflow not found.
    """
    try:
        await workflow_manager.cancel_workflow(execution_id)

        logger.info(f"Cancelled workflow execution: {execution_id}")

        return {
            "execution_id": execution_id,
            "status": "cancelled",
            "message": "Workflow execution cancelled",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel workflow",
        )


@router.get("/{execution_id}/history")
async def get_workflow_history(
    execution_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    workflow_manager: Annotated[WorkflowManager, Depends(get_workflow_manager)],
) -> dict:
    """Get workflow execution history.

    Args:
        execution_id: Workflow execution ID.
        current_user: Current authenticated user.
        db: Database session.
        workflow_manager: Workflow manager.

    Returns:
        dict: Workflow execution history.

    Raises:
        HTTPException: If workflow not found.
    """
    try:
        history = await workflow_manager.get_execution_history(execution_id)

        return history

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to get workflow history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflow history",
        )


@router.get("/{execution_id}/progress")
async def get_workflow_progress(
    execution_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    workflow_monitor: Annotated[WorkflowMonitor, Depends(get_workflow_monitor)],
) -> dict:
    """Get real-time workflow progress.

    Args:
        execution_id: Workflow execution ID.
        current_user: Current authenticated user.
        db: Database session.
        workflow_monitor: Workflow monitor.

    Returns:
        dict: Workflow progress.

    Raises:
        HTTPException: If workflow not found.
    """
    try:
        progress = await workflow_monitor.get_workflow_progress(execution_id)

        return progress

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to get workflow progress: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflow progress",
        )


@router.get("/monitor/health")
async def get_workflow_health(
    workflow_monitor: Annotated[WorkflowMonitor, Depends(get_workflow_monitor)],
) -> dict:
    """Get workflow system health status.

    Args:
        workflow_monitor: Workflow monitor.

    Returns:
        dict: Health check results.
    """
    try:
        health = await workflow_monitor.check_health()

        return health

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "healthy": False,
            "error": str(e),
        }


@router.get("/monitor/metrics")
async def get_workflow_metrics(
    workflow_monitor: Annotated[WorkflowMonitor, Depends(get_workflow_monitor)],
) -> dict:
    """Get workflow metrics.

    Args:
        workflow_monitor: Workflow monitor.

    Returns:
        dict: Workflow metrics.
    """
    return workflow_monitor.metrics


@router.post("/schedule")
async def schedule_workflow(
    workflow_type: str,
    cron_expression: str,
    input_data: dict,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    workflow_scheduler: Annotated[
        WorkflowScheduler, Depends(get_workflow_scheduler)
    ],
) -> dict:
    """Schedule a recurring workflow.

    Args:
        workflow_type: Type of workflow to schedule.
        cron_expression: Cron expression for scheduling.
        input_data: Input data for the workflow.
        current_user: Current authenticated user.
        db: Database session.
        workflow_scheduler: Workflow scheduler.

    Returns:
        dict: Schedule details.

    Raises:
        HTTPException: If scheduling fails.
    """
    try:
        schedule_id = workflow_scheduler.schedule_workflow(
            workflow_type=workflow_type,
            cron_expression=cron_expression,
            input_data=input_data,
            context={"user_id": current_user.id},
            metadata={"owner": current_user.email},
        )

        logger.info(
            f"Scheduled workflow: {workflow_type} (schedule_id: {schedule_id})"
        )

        return {
            "schedule_id": schedule_id,
            "workflow_type": workflow_type,
            "cron_expression": cron_expression,
            "status": "scheduled",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to schedule workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule workflow",
        )


@router.delete("/schedule/{schedule_id}")
async def unschedule_workflow(
    schedule_id: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    workflow_scheduler: Annotated[
        WorkflowScheduler, Depends(get_workflow_scheduler)
    ],
) -> dict:
    """Remove a scheduled workflow.

    Args:
        schedule_id: Schedule ID.
        current_user: Current authenticated user.
        db: Database session.
        workflow_scheduler: Workflow scheduler.

    Returns:
        dict: Unscheduling result.

    Raises:
        HTTPException: If schedule not found.
    """
    try:
        workflow_scheduler.unschedule_workflow(schedule_id)

        logger.info(f"Removed scheduled workflow: {schedule_id}")

        return {
            "schedule_id": schedule_id,
            "status": "unscheduled",
            "message": "Workflow schedule removed",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to unschedule workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unschedule workflow",
        )
