from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, List, Optional

from ..models import DeviceLogEntryRecord
from .context import DatabaseContext


class DeviceLogRepository:
    """Persists raw device log entries sourced from the Fritzbox."""

    def __init__(self, context: DatabaseContext) -> None:
        self._context = context

    def ingest_entries(self, entries: Iterable[dict[str, Any]]) -> int:
        rows: list[tuple[str, str, Optional[str], str]] = []
        for entry in entries:
            timestamp = entry.get("timestamp")
            message = entry.get("message")
            if not timestamp or not message:
                continue
            rows.append((timestamp, message, entry.get("raw"), entry.get("source", "tr064")))

        if not rows:
            return 0

        inserted = 0
        with self._context.connect() as conn:
            for timestamp, message, raw, source in rows:
                cursor = conn.execute(
                    """
                    INSERT OR IGNORE INTO device_log_entries (log_timestamp, message, raw, source)
                    VALUES (?, ?, ?, ?)
                    """,
                    (timestamp, message, raw, source),
                )
                inserted += cursor.rowcount
            conn.commit()
        return inserted

    def list_entries(
        self,
        *,
        limit: Optional[int] = None,
        ascending: bool = True,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[DeviceLogEntryRecord]:
        order_clause = "ASC" if ascending else "DESC"
        query = (
            "SELECT id, log_timestamp, message, raw, source"
            " FROM device_log_entries"
            " WHERE 1=1"
        )
        params: list[Any] = []
        if start is not None:
            query += " AND log_timestamp >= ?"
            params.append(start.isoformat())
        if end is not None:
            query += " AND log_timestamp <= ?"
            params.append(end.isoformat())

        query += f" ORDER BY log_timestamp {order_clause}"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        with self._context.connect() as conn:
            rows = conn.execute(query, params).fetchall()

        records: List[DeviceLogEntryRecord] = []
        for row in rows:
            try:
                timestamp = datetime.fromisoformat(row["log_timestamp"])
            except ValueError:
                continue
            records.append(
                DeviceLogEntryRecord(
                    id=row["id"],
                    timestamp=timestamp,
                    message=row["message"],
                    raw=row["raw"],
                    source=row["source"],
                )
            )
        return records
