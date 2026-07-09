"""Retry utilities with exponential backoff for handling transient failures"""

import asyncio
import functools
import logging
import time
from typing import Callable, Type, Tuple, Optional


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and request is rejected"""

    pass


logger = logging.getLogger(__name__)


async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> any:
    """
    Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exception types to catch

    Returns:
        Result of the function call

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e

            if attempt == max_retries:
                logger.error(
                    f"All {max_retries} retries exhausted for {func.__name__}",
                    extra={"error": str(e)},
                )
                raise

            delay = min(base_delay * (exponential_base**attempt), max_delay)
            logger.warning(
                f"Retry {attempt + 1}/{max_retries} for {func.__name__} " f"after {delay:.2f}s delay",
                extra={"error": str(e)},
            )
            await asyncio.sleep(delay)

    raise last_exception


def retry_sync_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator for retrying synchronous functions with exponential backoff.

    Usage:
        @retry_sync_with_backoff(max_retries=3)
        def my_function():
            # ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"All {max_retries} retries exhausted for {func.__name__}",
                            extra={"error": str(e)},
                        )
                        raise

                    delay = base_delay * (exponential_base**attempt)
                    logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__}")
                    time.sleep(delay)

            raise last_exception

        return wrapper

    return decorator


# Circuit breaker pattern for preventing cascading failures
class CircuitBreaker:
    """Circuit breaker to prevent cascading failures"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Tuple[Type[Exception], ...] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            # Check if we should try half-open
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)

            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0

            return result

        except self.expected_exception:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker OPENED after {self.failure_count} failures")

            raise
