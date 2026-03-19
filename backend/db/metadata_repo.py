from __future__ import annotations

from typing import Optional

from .context import DatabaseContext


class MetadataRepository:
    """Stores general application metadata."""

    def __init__(self, context: DatabaseContext) -> None:
        self._context = context

    def get(self, key: str) -> Optional[str]:
        with self._context.connect() as conn:
            row = conn.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def set(self, key: str, value: str) -> None:
        with self._context.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                (key, value),
            )
            conn.commit()
