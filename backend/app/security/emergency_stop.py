"""Cooperative emergency stop and task cancellation registry."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator


class EmergencyStop:
    def __init__(self) -> None:
        self._stopped = asyncio.Event()
        self._tasks: dict[str, set[asyncio.Task[object]]] = {}
        self._lock = asyncio.Lock()

    @property
    def is_stopped(self) -> bool:
        return self._stopped.is_set()

    async def check(self) -> None:
        if self._stopped.is_set():
            raise asyncio.CancelledError("Arya emergency stop is active.")

    @asynccontextmanager
    async def register_current_task(self, task_id: str) -> AsyncIterator[None]:
        task = asyncio.current_task()
        if task is None:
            raise RuntimeError("Task registration requires an active asyncio task.")
        async with self._lock:
            if self._stopped.is_set():
                raise asyncio.CancelledError("Arya emergency stop is active.")
            self._tasks.setdefault(task_id, set()).add(task)
        try:
            yield
        finally:
            async with self._lock:
                active = self._tasks.get(task_id)
                if active is not None:
                    active.discard(task)
                    if not active:
                        self._tasks.pop(task_id, None)

    async def stop(self) -> int:
        self._stopped.set()
        current = asyncio.current_task()
        async with self._lock:
            tasks = {task for group in self._tasks.values() for task in group if task is not current and not task.done()}
            for task in tasks:
                task.cancel("Arya emergency stop")
            return len(tasks)

    async def reset(self) -> None:
        """Reset only from an explicit trusted UI control after the user acknowledges stop."""
        async with self._lock:
            if any(not task.done() for group in self._tasks.values() for task in group):
                raise RuntimeError("Cannot reset while registered tasks are still running.")
            self._stopped.clear()
