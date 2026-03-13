"""Health check endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.db.session import get_db, get_redis

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict:
    """Perform basic health check.

    Returns:
        dict: Health status with timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Perform readiness check including database connectivity.

    Args:
        db: Database session dependency.

    Returns:
        dict: Readiness status with component health.
    """
    checks = {
        "status": "ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {},
    }

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["components"]["database"] = "healthy"
    except Exception as e:
        checks["components"]["database"] = f"unhealthy: {str(e)}"
        checks["status"] = "degraded"

    return checks


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> dict:
    """Perform liveness check.

    Returns:
        dict: Liveness status.
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
