from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional

from ..models import StatusEvent
from .context import DatabaseContext


class StatusRepository:
    """Access to connection status change events."""

    def __init__(self, context: DatabaseContext) -> None:
        self._context = context

    def record_event(self, status: str, timestamp: datetime, details: Optional[str] = None) -> None:
        with self._context.connect() as conn:
            conn.execute(
                "INSERT INTO status_events (timestamp, status, details) VALUES (?, ?, ?)",
                (timestamp.isoformat(), status, details),
            )
            conn.commit()

    def latest_event(self) -> Optional[StatusEvent]:
        with self._context.connect() as conn:
            row = conn.execute(
                "SELECT id, timestamp, status, details FROM status_events ORDER BY timestamp DESC LIMIT 1"
            ).fetchone()
        if row is None:
            return None
        return StatusEvent(
            id=row["id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            status=row["status"],
            details=row["details"],
        )

    def iterate_events(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> Iterable[StatusEvent]:
        query = "SELECT id, timestamp, status, details FROM status_events WHERE 1=1"
        params: list[str] = []
        if start is not None:
            query += " AND timestamp >= ?"
            params.append(start.isoformat())
        if end is not None:
            query += " AND timestamp <= ?"
            params.append(end.isoformat())
        query += " ORDER BY timestamp ASC"

        with self._context.connect() as conn:
            for row in conn.execute(query, params):
                yield StatusEvent(
                    id=row["id"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    status=row["status"],
                    details=row["details"],
                )
