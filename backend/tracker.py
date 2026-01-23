from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict

from .database import StatusRepository
from .device_log_sync import DeviceLogSync
from .fritzbox_client import FritzboxClient
from .periodic_runner import PeriodicRunner


class ConnectionTracker:
    """Coordinates TR-064 status polls and persistence."""

    def __init__(
        self,
        status_repository: StatusRepository,
        fritzbox_client: FritzboxClient,
        device_log_sync: DeviceLogSync,
        poll_interval_seconds: int,
        device_log_poll_interval_seconds: int,
    ) -> None:
        # Persistence & domain collaborators
        self._status_repository = status_repository
        self._fritzbox_client = fritzbox_client
        self._device_log_sync = device_log_sync
        self._status_poller = PeriodicRunner(
            interval_seconds=poll_interval_seconds,
            work=self.poll_now,
            on_error=self._handle_poll_error,
        )
        self._device_log_poller = PeriodicRunner(
            interval_seconds=device_log_poll_interval_seconds,
            work=self._device_log_sync.run_once,
            on_error=self._handle_device_log_error,
        )

    def poll_now(self) -> Dict[str, Any]:
        status = self._fritzbox_client.poll_status()
        connection_is_up = bool(status.get("connected"))
        details = status.get("details", {})
        timestamp = datetime.now(timezone.utc)
        status_value = "online" if connection_is_up else "offline"

        latest = self._status_repository.latest_event()
        if latest is None or latest.status != status_value:
            self._status_repository.record_event(
                status=status_value,
                timestamp=timestamp,
                details=json.dumps(details, default=str),
            )

        return {
            "timestamp": timestamp.isoformat(),
            "status": status_value,
            "details": details,
        }

    def check_connection(self) -> Dict[str, Any]:
        status = self._fritzbox_client.poll_status()
        details = status.get("details", {})
        return {
            "connected": bool(status.get("connected")),
            **details,
        }

    async def start(self) -> None:
        await self._status_poller.start()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._device_log_sync.run_once)
        await self._device_log_poller.start()

    async def stop(self) -> None:
        await self._status_poller.stop()
        await self._device_log_poller.stop()

    def _handle_poll_error(self, exc: Exception) -> None:
        error_timestamp = datetime.now(timezone.utc)
        self._status_repository.record_event(
            status="error",
            timestamp=error_timestamp,
            details=str(exc),
        )

    def _handle_device_log_error(self, exc: Exception) -> None:
        error_timestamp = datetime.now(timezone.utc)
        self._status_repository.record_event(
            status="error",
            timestamp=error_timestamp,
            details=f"device_log_poll: {exc}",
        )
