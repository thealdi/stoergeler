from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

logger = logging.getLogger(__name__)


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
        logger.info("Initializing database schema at %s", self._database_path)
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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            # Indexes for common ORDER BY / WHERE columns
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_device_log_entries_timestamp ON device_log_entries(log_timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_outages_start_time ON outages(start_time)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_status_events_timestamp ON status_events(timestamp)"
            )

            # Migration: add source column to existing databases
            try:
                conn.execute("ALTER TABLE outages ADD COLUMN source TEXT NOT NULL DEFAULT 'calculated'")
            except sqlite3.OperationalError:
                pass  # Column already exists
            conn.commit()
