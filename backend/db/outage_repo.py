from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, List, Optional

from ..models import OutageRecord
from .context import DatabaseContext


class OutageRepository:
    """Stores calculated outage intervals for quick retrieval."""

    def __init__(self, context: DatabaseContext) -> None:
        self._context = context

    def replace_outages(self, outages: Iterable[dict[str, Any]]) -> None:
        timestamp = datetime.utcnow().isoformat()
        with self._context.connect() as conn:
            conn.execute("DELETE FROM outages WHERE source = 'calculated'")
            for outage in outages:
                conn.execute(
                    """
                    INSERT INTO outages (
                        start_time,
                        end_time,
                        duration_seconds,
                        status,
                        start_log_entry_id,
                        end_log_entry_id,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        outage["start_time"].isoformat(),
                        outage["end_time"].isoformat() if outage.get("end_time") else None,
                        outage.get("duration_seconds"),
                        outage.get("status", "closed"),
                        outage.get("start_log_entry_id"),
                        outage.get("end_log_entry_id"),
                        timestamp,
                        timestamp,
                    ),
                )
            conn.commit()

    def list_outages(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[OutageRecord]:
        query = "SELECT start_time, end_time, duration_seconds, status FROM outages WHERE 1=1"
        params: list[str] = []
        if start is not None:
            query += " AND start_time >= ?"
            params.append(start.isoformat())
        if end is not None:
            query += " AND start_time <= ?"
            params.append(end.isoformat())

        query += " ORDER BY start_time ASC"

        with self._context.connect() as conn:
            rows = conn.execute(query, params).fetchall()

        records: List[OutageRecord] = []
        for row in rows:
            try:
                start_dt = datetime.fromisoformat(row["start_time"])
            except ValueError:
                continue
            end_value = row["end_time"]
            if end_value:
                try:
                    end_dt = datetime.fromisoformat(end_value)
                except ValueError:
                    end_dt = None
            else:
                end_dt = None
            records.append(
                OutageRecord(
                    start_time=start_dt,
                    end_time=end_dt,
                    duration_seconds=row["duration_seconds"],
                    status=row["status"],
                )
            )
        return records

    def create_outage(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        duration_seconds: Optional[int] = None,
        status: str = "manual",
    ) -> int:
        """Insert a single manually-created outage and return its row ID."""
        if end_time and duration_seconds is None:
            duration_seconds = max(1, int((end_time - start_time).total_seconds()))

        now = datetime.utcnow().isoformat()
        with self._context.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO outages (
                    start_time, end_time, duration_seconds,
                    status, source,
                    start_log_entry_id, end_log_entry_id,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, 'manual', NULL, NULL, ?, ?)
                """,
                (
                    start_time.isoformat(),
                    end_time.isoformat() if end_time else None,
                    duration_seconds,
                    status,
                    now,
                    now,
                ),
            )
            conn.commit()
            return cursor.lastrowid  # type: ignore[return-value]
