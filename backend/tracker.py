from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fritzconnection import FritzConnection
from fritzconnection.lib.fritzstatus import FritzStatus

from .database import DeviceLogRepository, OutageRepository, StatusRepository
from .outage_service import OutageService


@dataclass
class FritzBoxCredentials:
    address: str
    username: Optional[str]
    password: Optional[str]


class ConnectionTracker:
    """Coordinates TR-064 status polls and persistence."""

    def __init__(
        self,
        status_repository: StatusRepository,
        device_log_repository: DeviceLogRepository,
        outage_repository: OutageRepository,
        outage_service: OutageService,
        credentials: FritzBoxCredentials,
        poll_interval_seconds: int,
        device_log_poll_interval_seconds: int,
    ) -> None:
        # Persistence & domain collaborators
        self._status_repository = status_repository
        self._device_log_repository = device_log_repository
        self._outage_repository = outage_repository
        self._outage_service = outage_service
        self._credentials = credentials
        self._poll_interval = poll_interval_seconds
        self._task: Optional[asyncio.Task[None]] = None
        self._device_log_interval = device_log_poll_interval_seconds
        self._device_log_task: Optional[asyncio.Task[None]] = None
        self._stop_event = asyncio.Event()
        self._device_log_stop_event = asyncio.Event()

    def _create_client(self) -> FritzStatus:
        return FritzStatus(
            address=self._credentials.address,
            user=self._credentials.username,
            password=self._credentials.password,
        )

    def _create_connection(self) -> FritzConnection:
        return FritzConnection(
            address=self._credentials.address,
            user=self._credentials.username,
            password=self._credentials.password,
        )

    def _collect_details(self, client: FritzStatus) -> Dict[str, Any]:
        def _safe_attr(attribute: str) -> Any:
            try:
                return getattr(client, attribute)
            except Exception:  # noqa: BLE001
                return None

        def _safe_value(value: Any) -> Any:
            if isinstance(value, (str, int, float, bool)) or value is None:
                return value
            return str(value)

        wan_access_type = _safe_attr("connection") or _safe_attr("connection_type")
        wan_link_status = _safe_attr("wan_link_status")
        uptime = _safe_attr("uptime") or _safe_attr("connection_uptime")

        return {
            "external_ip": _safe_value(_safe_attr("external_ip")),
            "wan_access_type": _safe_value(wan_access_type),
            "wan_link_status": _safe_value(wan_link_status),
            "max_bit_rate": _safe_value(_safe_attr("max_bit_rate")),
            "uptime": _safe_value(uptime),
        }

    def poll_now(self) -> Dict[str, Any]:
        client = self._create_client()
        connection_is_up = bool(getattr(client, "is_connected", False))
        details = self._collect_details(client)
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

    _LOG_LINE_PATTERN = re.compile(
        r"^(?P<date>\d{2}\.\d{2}\.\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<message>.+)$"
    )

    def fetch_device_log(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        connection = self._create_connection()
        result = connection.call_action("DeviceInfo:1", "GetDeviceLog")
        log_blob = result.get("NewDeviceLog", "") if isinstance(result, dict) else ""
        entries: List[Dict[str, Any]] = []
        for line in log_blob.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            parsed = self._parse_log_line(cleaned)
            entries.append(parsed)
        if limit is not None:
            return entries[:limit]
        return entries

    def _parse_log_line(self, line: str) -> Dict[str, Any]:
        match = self._LOG_LINE_PATTERN.match(line)
        if not match:
            return {"raw": line}

        date_part = match.group("date")
        time_part = match.group("time")
        message = match.group("message")

        try:
            naive_dt = datetime.strptime(f"{date_part} {time_part}", "%d.%m.%y %H:%M:%S")
            timestamp = naive_dt.isoformat()
        except ValueError:
            timestamp = None

        return {
            "timestamp": timestamp,
            "message": message,
            "raw": line,
        }

    def check_connection(self) -> Dict[str, Any]:
        client = self._create_client()
        details = self._collect_details(client)
        return {
            "connected": bool(getattr(client, "is_connected", False)),
            **details,
        }

    async def start(self) -> None:
        if self._task is None:
            self._stop_event.clear()
            self._task = asyncio.create_task(self._run())
        if self._device_log_task is None:
            self._device_log_stop_event.clear()
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._sync_device_log_once)
            self._device_log_task = asyncio.create_task(self._run_device_log())

    async def stop(self) -> None:
        if self._task is not None:
            self._stop_event.set()
            await self._task
            self._task = None
        if self._device_log_task is not None:
            self._device_log_stop_event.set()
            await self._device_log_task
            self._device_log_task = None

    async def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, self.poll_now)
            except Exception as exc:  # noqa: BLE001
                error_timestamp = datetime.now(timezone.utc)
                self._status_repository.record_event(
                    status="error",
                    timestamp=error_timestamp,
                    details=str(exc),
                )

            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self._poll_interval)
            except asyncio.TimeoutError:
                continue

    def _sync_device_log_once(self) -> None:
        # Pull aktuelle Roh-Logs von der Fritzbox, persistieren und Outages neu berechnen.
        entries = self.fetch_device_log()
        self._device_log_repository.ingest_entries(entries)
        stored_entries = self._device_log_repository.list_entries()
        outages = self._outage_service.calculate(stored_entries)
        self._outage_repository.replace_outages(outages)

    async def _run_device_log(self) -> None:
        while not self._device_log_stop_event.is_set():
            try:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, self._sync_device_log_once)
            except Exception as exc:  # noqa: BLE001
                error_timestamp = datetime.now(timezone.utc)
                self._status_repository.record_event(
                    status="error",
                    timestamp=error_timestamp,
                    details=f"device_log_poll: {exc}",
                )

            try:
                await asyncio.wait_for(
                    self._device_log_stop_event.wait(),
                    timeout=self._device_log_interval,
                )
            except asyncio.TimeoutError:
                continue
