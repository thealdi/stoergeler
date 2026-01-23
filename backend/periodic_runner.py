from __future__ import annotations

import asyncio
from typing import Callable, Optional


class PeriodicRunner:
    """Runs a blocking callable on a fixed interval in a background task."""

    def __init__(
        self,
        interval_seconds: int,
        work: Callable[[], None],
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> None:
        self._interval = interval_seconds
        self._work = work
        self._on_error = on_error
        self._task: Optional[asyncio.Task[None]] = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        if self._task is not None:
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._stop_event.set()
        await self._task
        self._task = None

    async def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, self._work)
            except Exception as exc:  # noqa: BLE001
                if self._on_error is not None:
                    self._on_error(exc)

            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self._interval)
            except asyncio.TimeoutError:
                continue
