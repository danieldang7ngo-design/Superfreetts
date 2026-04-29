import asyncio
from types import TracebackType
from typing import Optional, Type


class Timeout:
    def __init__(self, deadline: Optional[float]) -> None:
        self._deadline = deadline
        self._task = None
        self._handle = None
        self._cancelled_by_timeout = False

    async def __aenter__(self):
        self._task = asyncio.current_task()
        if self._deadline is not None:
            loop = asyncio.get_running_loop()
            self._handle = loop.call_at(self._deadline, self._on_timeout)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        if self._handle is not None:
            self._handle.cancel()
            self._handle = None

        if exc_type is asyncio.CancelledError and self._cancelled_by_timeout:
            raise asyncio.TimeoutError from exc_val
        return None

    def _on_timeout(self) -> None:
        if self._task is not None:
            self._cancelled_by_timeout = True
            self._task.cancel()

    def expired(self) -> bool:
        return self._cancelled_by_timeout


def timeout(delay: Optional[float]) -> Timeout:
    if delay is None:
        return Timeout(None)
    loop = asyncio.get_running_loop()
    return Timeout(loop.time() + delay)


def timeout_at(deadline: Optional[float]) -> Timeout:
    return Timeout(deadline)
