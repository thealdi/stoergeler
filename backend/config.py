from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application configuration loaded from environment variables."""

    fritzbox_address: str = os.getenv("FRITZBOX_ADDRESS", "fritz.box")
    fritzbox_username: Optional[str] = os.getenv("FRITZBOX_USERNAME")
    fritzbox_password: Optional[str] = os.getenv("FRITZBOX_PASSWORD")
    database_path: Path = Path(os.getenv("DATABASE_PATH", "data/stoergeler.db"))
    poll_interval_seconds: int = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    device_log_poll_interval_seconds: int = int(
        os.getenv("DEVICE_LOG_POLL_INTERVAL_SECONDS", "60")
    )


settings = Settings()
