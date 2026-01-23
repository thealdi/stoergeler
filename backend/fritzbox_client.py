from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from fritzconnection import FritzConnection
from fritzconnection.lib.fritzstatus import FritzStatus


@dataclass(frozen=True)
class FritzBoxCredentials:
    address: str
    username: Optional[str]
    password: Optional[str]


class FritzboxClient:
    """Lightweight wrapper around FritzConnection / FritzStatus."""

    _LOG_LINE_PATTERN = re.compile(
        r"^(?P<date>\d{2}\.\d{2}\.\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<message>.+)$"
    )

    def __init__(self, credentials: FritzBoxCredentials) -> None:
        self._credentials = credentials

    def _create_status_client(self) -> FritzStatus:
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

    def poll_status(self) -> Dict[str, Any]:
        client = self._create_status_client()
        return {
            "connected": bool(getattr(client, "is_connected", False)),
            "details": self._collect_details(client),
        }

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
