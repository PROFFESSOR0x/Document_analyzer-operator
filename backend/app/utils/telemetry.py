"""Telemetry and logging utilities."""

import secrets
import time
from collections.abc import Callable
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import wraps
from typing import Any, ParamSpec, TypeVar, Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


class Timer:
    """Context manager for timing code execution."""

    def __init__(self, name: str = "Operation") -> None:
        """Initialize timer.

        Args:
            name: Name of the timed operation.
        """
        self.name = name
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.elapsed: float | None = None

    def __enter__(self) -> "Timer":
        """Start timing.

        Returns:
            Timer: Self.
        """
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        """Stop timing and log result.

        Args:
            *args: Exception arguments if raised.
        """
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        logger.debug(f"{self.name} completed in {self.elapsed:.4f} seconds")


def timed(name: Optional[str] = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to time function execution.

    Args:
        name: Optional name for the timed operation.

    Returns:
        Callable: Decorated function.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            func_name = name or func.__name__
            with Timer(func_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


async def timed_async(
    name: Optional[str] = None,
) -> Callable[[Callable[P, Any]], Callable[P, Any]]:
    """Async decorator to time function execution.

    Args:
        name: Optional name for the timed operation.

    Returns:
        Callable: Decorated async function.
    """

    def decorator(func: Callable[P, Any]) -> Callable[P, Any]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            func_name = name or func.__name__
            with Timer(func_name):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def log_context(operation: str, **extra: Any):
    """Context manager for logging operation context.

    Args:
        operation: Name of the operation.
        **extra: Extra context to log.

    Yields:
        None
    """
    context_id = secrets.token_hex(8)
    start_time = datetime.now(timezone.utc)

    logger.info(
        f"Starting {operation}",
        extra={
            "operation": operation,
            "context_id": context_id,
            "start_time": start_time.isoformat(),
            **extra,
        },
    )

    try:
        yield {"context_id": context_id}
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        logger.info(
            f"Completed {operation}",
            extra={
                "operation": operation,
                "context_id": context_id,
                "duration_seconds": duration,
                "status": "success",
            },
        )
    except Exception as e:
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        logger.error(
            f"Failed {operation}: {str(e)}",
            extra={
                "operation": operation,
                "context_id": context_id,
                "duration_seconds": duration,
                "status": "error",
                "error": str(e),
            },
            exc_info=True,
        )
        raise


def log_function_call(
    log_level: str = "debug",
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to log function calls.

    Args:
        log_level: Logging level (debug, info, warning, error).

    Returns:
        Callable: Decorated function.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            log_func = getattr(logger, log_level)
            log_func(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")

            try:
                result = func(*args, **kwargs)
                log_func(f"{func.__name__} returned {result}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {type(e).__name__}: {e}")
                raise

        return wrapper

    return decorator
