from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Iterable, List, Optional, Sequence

from .models import DeviceLogEntryRecord, OutageRecord, StatusEvent


class DatabaseContext:
    """Encapsulates the SQLite connection handling and schema initialisation."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._database_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self._database_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_schema(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS status_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS device_log_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_timestamp TEXT NOT NULL,
                    message TEXT NOT NULL,
                    raw TEXT,
                    source TEXT DEFAULT 'tr064',
                    ingested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (log_timestamp, message)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS outages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_seconds INTEGER,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'calculated',
                    start_log_entry_id INTEGER,
                    end_log_entry_id INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (start_log_entry_id) REFERENCES device_log_entries(id) ON DELETE SET NULL,
                    FOREIGN KEY (end_log_entry_id) REFERENCES device_log_entries(id) ON DELETE SET NULL
                )
                """
            )
            # Migration: add source column to existing databases
            try:
                conn.execute("ALTER TABLE outages ADD COLUMN source TEXT NOT NULL DEFAULT 'calculated'")
            except sqlite3.OperationalError:
                pass  # Column already exists
            conn.commit()


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
    ) -> List[DeviceLogEntryRecord]:
        order_clause = "ASC" if ascending else "DESC"
        query = (
            "SELECT id, log_timestamp, message, raw, source"
            " FROM device_log_entries"
            f" ORDER BY log_timestamp {order_clause}"
        )
        params: Sequence[Any] = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)

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

    def list_outages(self) -> List[OutageRecord]:
        with self._context.connect() as conn:
            rows = conn.execute(
                "SELECT start_time, end_time, duration_seconds, status FROM outages ORDER BY start_time ASC"
            ).fetchall()

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
