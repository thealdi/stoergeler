from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from .models import DeviceLogEntryRecord


@dataclass
class OutageInterval:
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[int]
    status: str
    start_log_entry_id: Optional[int]
    end_log_entry_id: Optional[int]


class OutageService:
    """Derives outage intervals from device log entries.

    The Fritzbox protokolliert mehrere getrennte Eventserien (IPv4/IPv6) und
    streut planmäßige Zwangstrennungen ein. Diese Klasse lässt die Einträge über
    eine kleine Zustandsmaschine laufen und produziert daraus abgeschlossene
    oder offene Störungsintervalle, inklusive Kennzeichnung geplanter Ereignisse.
    """

    def calculate(self, entries: Sequence[DeviceLogEntryRecord]) -> List[Dict[str, Any]]:
        outages: List[Dict[str, Any]] = []

        state: Dict[str, Dict[str, Any]] = {
            "ipv4": {"start": None, "start_entry_id": None, "planned": False},
            "ipv6": {"start": None, "start_entry_id": None, "planned": False},
        }
        pending_planned = {"ipv4": False, "ipv6": False}

        for entry in entries:
            protocol, action = self._categorise_log_entry(entry)

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

    @staticmethod
    def _categorise_log_entry(entry: DeviceLogEntryRecord) -> tuple[str, str]:
        message = (entry.message or "").lower()

        planned_keywords = (
            "zwangstrennung",
            "wird kurz unterbrochen",
            "trennung durch den anbieter",
        )
        if any(keyword in message for keyword in planned_keywords):
            return "both", "planned_hint"

        if "internetverbindung ipv6" in message:
            if "wurde getrennt" in message or ("präfix" in message and "nicht mehr gültig" in message):
                return "ipv6", "disconnect"
            if "wurde erfolgreich hergestellt" in message or "wurde erfolgreich bezogen" in message:
                return "ipv6", "connect"

        if "internetverbindung" in message and "wurde getrennt" in message:
            return "ipv4", "disconnect"

        if "internetverbindung" in message and "wurde erfolgreich hergestellt" in message:
            return "ipv4", "connect"

        if "ipv6-präfix" in message and "erfolgreich bezogen" in message:
            return "ipv6", "connect"

        if "ipv6-präfix" in message and "nicht mehr gültig" in message:
            return "ipv6", "disconnect"

        return "unknown", "ignore"
