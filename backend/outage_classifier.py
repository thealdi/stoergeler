from __future__ import annotations

from typing import Tuple

from .models import DeviceLogEntryRecord
from .outage_config import OutageKeywords


def _contains_any(message: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in message for keyword in keywords)


def categorize_log_entry(
    entry: DeviceLogEntryRecord,
    cfg: OutageKeywords,
) -> Tuple[str, str]:
    message = (entry.message or "").lower()

    if _contains_any(message, cfg.planned_keywords):
        return "both", "planned_hint"

    if _contains_any(message, cfg.ipv6_disconnect_keywords):
        return "ipv6", "disconnect"
    if _contains_any(message, cfg.ipv6_connect_keywords):
        return "ipv6", "connect"

    if _contains_any(message, cfg.ipv4_disconnect_keywords):
        return "ipv4", "disconnect"
    if _contains_any(message, cfg.ipv4_connect_keywords):
        return "ipv4", "connect"

    return "unknown", "ignore"
