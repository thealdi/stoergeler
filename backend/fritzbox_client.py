from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar

from fritzconnection import FritzConnection
from fritzconnection.lib.fritzstatus import FritzStatus

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _retry(fn: Callable[[], T], attempts: int = 3, backoff: float = 2.0) -> T:
    """Call *fn* up to *attempts* times with exponential backoff on failure."""
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception:
            if attempt == attempts:
                raise
            delay = backoff ** attempt
            logger.warning(
                "Attempt %d/%d failed, retrying in %.0fs …",
                attempt,
                attempts,
                delay,
                exc_info=True,
            )
            time.sleep(delay)
    raise RuntimeError("unreachable")  # pragma: no cover


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

        return {
            "external_ip": _safe_value(_safe_attr("external_ip")),
            "external_ipv6": _safe_value(_safe_attr("external_ipv6")),
            "connection_service": _safe_value(_safe_attr("connection_service")),
            "is_linked": _safe_value(_safe_attr("is_linked")),
            "max_bit_rate": _safe_value(_safe_attr("max_bit_rate")),
            "transmission_rate": _safe_value(_safe_attr("transmission_rate")),
            "uptime": _safe_value(_safe_attr("str_uptime")),
        }

    def poll_status(self) -> Dict[str, Any]:
        def _do_poll() -> Dict[str, Any]:
            client = self._create_status_client()
            return {
                "connected": bool(getattr(client, "is_connected", False)),
                "details": self._collect_details(client),
            }

        try:
            return _retry(_do_poll)
        except Exception:
            logger.error("TR-064 connection error during status poll", exc_info=True)
            raise

    def fetch_device_log(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        def _do_fetch() -> dict:
            connection = self._create_connection()
            return connection.call_action("DeviceInfo:1", "GetDeviceLog")

        try:
            result = _retry(_do_fetch)
        except Exception:
            logger.error("TR-064 connection error during device log fetch", exc_info=True)
            raise
        log_blob = result.get("NewDeviceLog", "") if isinstance(result, dict) else ""
        entries: List[Dict[str, Any]] = []
        for line in log_blob.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            parsed = self._parse_log_line(cleaned)
            entries.append(parsed)
        if limit is not None:
            entries = entries[:limit]
        logger.debug("Fetched %d device log entries", len(entries))
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
