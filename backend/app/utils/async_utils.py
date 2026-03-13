"""Async utility functions."""

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar
from concurrent.futures import ThreadPoolExecutor

P = ParamSpec("P")
R = TypeVar("R")

# Thread pool for blocking operations
_executor: ThreadPoolExecutor | None = None


def get_executor() -> ThreadPoolExecutor:
    """Get or create the global thread pool executor.

    Returns:
        ThreadPoolExecutor: Thread pool executor instance.
    """
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=10)
    return _executor


def run_sync_in_async(
    func: Callable[P, R],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Awaitable[R]:
    """Run a synchronous function in an async context.

    Args:
        func: The synchronous function to run.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        Awaitable: Awaitable result of the function.
    """
    loop = asyncio.get_event_loop()
    executor = get_executor()
    bound_func = functools.partial(func, *args, **kwargs)
    return loop.run_in_executor(executor, bound_func)


async def gather_with_concurrency(
    n: int,
    *coros: Awaitable[Any],
) -> list[Any]:
    """Run coroutines with limited concurrency.

    Args:
        n: Maximum number of concurrent coroutines.
        *coros: Coroutines to run.

    Returns:
        list: Results from all coroutines.
    """
    semaphore = asyncio.Semaphore(n)

    async def sem_coro(coro: Awaitable[Any]) -> Any:
        async with semaphore:
            return await coro

    return await asyncio.gather(*(sem_coro(c) for c in coros))


async def retry_async(
    func: Callable[[], Awaitable[R]],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> R:
    """Retry an async function with exponential backoff.

    Args:
        func: The async function to retry.
        max_retries: Maximum number of retry attempts.
        delay: Initial delay between retries in seconds.
        backoff: Multiplier for delay after each retry.
        exceptions: Exception types to catch and retry.

    Returns:
        R: Result from the function.

    Raises:
        Exception: The last exception if all retries fail.
    """
    current_delay = delay
    last_exception: Exception | None = None

    for attempt in range(max_retries):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                await asyncio.sleep(current_delay)
                current_delay *= backoff

    if last_exception:
        raise last_exception
    raise RuntimeError("Unexpected retry failure")


class AsyncContextManager:
    """Base class for async context managers."""

    async def __aenter__(self) -> "AsyncContextManager":
        """Enter async context.

        Returns:
            AsyncContextManager: Self.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit async context.

        Args:
            exc_type: Exception type if raised.
            exc_val: Exception value if raised.
            exc_tb: Exception traceback if raised.
        """
        pass
