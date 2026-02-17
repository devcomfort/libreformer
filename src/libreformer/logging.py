from __future__ import annotations

import time
from functools import wraps
from typing import Callable, TypeVar, ParamSpec, Awaitable
from loguru import logger

P = ParamSpec("P")
R = TypeVar("R")


def log_elapsed_time(operation_name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """함수의 시작/완료와 소요 시간(ms)을 로깅합니다."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            logger.info("{} 시작", operation_name)
            start_time = time.perf_counter()

            result = func(*args, **kwargs)

            end_time = time.perf_counter()
            elapsed_time_ms = (end_time - start_time) * 1000.0
            logger.info("{} 완료: 소요시간={:.1f}ms", operation_name, elapsed_time_ms)

            return result

        return wrapper

    return decorator


def async_log_elapsed_time(
    operation_name: str,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """비동기 함수의 시작/완료와 소요 시간(ms)을 로깅합니다."""

    def decorator(
        func: Callable[P, Awaitable[R]],
    ) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            logger.info("{} 시작", operation_name)
            start_time = time.perf_counter()

            result = await func(*args, **kwargs)

            end_time = time.perf_counter()
            elapsed_time_ms = (end_time - start_time) * 1000.0
            logger.info("{} 완료: 소요시간={:.1f}ms", operation_name, elapsed_time_ms)

            return result

        return wrapper  # type: ignore[return-value]

    return decorator  # type: ignore[return-value]
