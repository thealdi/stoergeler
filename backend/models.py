from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class StatusEvent:
    id: int
    timestamp: datetime
    status: str
    details: Optional[str]


@dataclass
class DeviceLogEntryRecord:
    id: int
    timestamp: datetime
    message: str
    raw: Optional[str]
    source: Optional[str]


@dataclass
class OutageRecord:
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[int]
    status: str
