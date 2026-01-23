from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from .models import DeviceLogEntryRecord
from .outage_classifier import categorize_log_entry
from .outage_config import DEFAULT_OUTAGE_KEYWORDS, OutageKeywords


@dataclass
class OutageInterval:
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[int]
    status: str
    start_log_entry_id: Optional[int]
    end_log_entry_id: Optional[int]


class OutageCalculator:
    """Derives outage intervals from device log entries."""

    def __init__(self, cfg: OutageKeywords = DEFAULT_OUTAGE_KEYWORDS) -> None:
        self._cfg = cfg

    def calculate(self, entries: Sequence[DeviceLogEntryRecord]) -> List[Dict[str, Any]]:
        outages: List[Dict[str, Any]] = []

        state: Dict[str, Dict[str, Any]] = {
            "ipv4": {"start": None, "start_entry_id": None, "planned": False},
            "ipv6": {"start": None, "start_entry_id": None, "planned": False},
        }
        pending_planned = {"ipv4": False, "ipv6": False}

        for entry in entries:
            protocol, action = categorize_log_entry(entry, self._cfg)

            if action == "planned_hint":
                if protocol in ("ipv4", "both"):
                    pending_planned["ipv4"] = True
                if protocol in ("ipv6", "both"):
                    pending_planned["ipv6"] = True
                continue

            if protocol not in ("ipv4", "ipv6"):
                continue

            if action == "disconnect":
                current = state[protocol]
                if current["start"] is None:
                    current["start"] = entry.timestamp
                    current["start_entry_id"] = entry.id
                    current["planned"] = pending_planned[protocol]
                else:
                    current["planned"] = current["planned"] or pending_planned[protocol]
                pending_planned[protocol] = False
                continue

            if action == "connect":
                current = state[protocol]
                if current["start"] is None:
                    continue

                duration_seconds = int((entry.timestamp - current["start"]).total_seconds())
                if duration_seconds <= 0:
                    duration_seconds = 1

                outages.append(
                    {
                        "start_time": current["start"],
                        "end_time": entry.timestamp,
                        "duration_seconds": duration_seconds,
                        "status": "planned" if current["planned"] else "closed",
                        "start_log_entry_id": current["start_entry_id"],
                        "end_log_entry_id": entry.id,
                    }
                )

                state[protocol] = {"start": None, "start_entry_id": None, "planned": False}
                pending_planned[protocol] = False

        for protocol, current in state.items():
            if current["start"] is not None:
                outages.append(
                    {
                        "start_time": current["start"],
                        "end_time": None,
                        "duration_seconds": None,
                        "status": "planned-open" if current["planned"] else "open",
                        "start_log_entry_id": current["start_entry_id"],
                        "end_log_entry_id": None,
                    }
                )

        return outages
