from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os

from dotenv import load_dotenv

from .outage_config import DEFAULT_OUTAGE_KEYWORDS

def _parse_csv_env(name: str, fallback: tuple[str, ...]) -> tuple[str, ...]:
    raw = os.getenv(name, "")
    if not raw:
        return fallback
    parts = [part.strip() for part in raw.split(",")]
    return tuple(part for part in parts if part)


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
    outage_planned_keywords: tuple[str, ...] = _parse_csv_env(
        "OUTAGE_PLANNED_KEYWORDS", DEFAULT_OUTAGE_KEYWORDS.planned_keywords
    )
    outage_ipv4_disconnect_keywords: tuple[str, ...] = _parse_csv_env(
        "OUTAGE_IPV4_DISCONNECT_KEYWORDS", DEFAULT_OUTAGE_KEYWORDS.ipv4_disconnect_keywords
    )
    outage_ipv4_connect_keywords: tuple[str, ...] = _parse_csv_env(
        "OUTAGE_IPV4_CONNECT_KEYWORDS", DEFAULT_OUTAGE_KEYWORDS.ipv4_connect_keywords
    )
    outage_ipv6_disconnect_keywords: tuple[str, ...] = _parse_csv_env(
        "OUTAGE_IPV6_DISCONNECT_KEYWORDS", DEFAULT_OUTAGE_KEYWORDS.ipv6_disconnect_keywords
    )
    outage_ipv6_connect_keywords: tuple[str, ...] = _parse_csv_env(
        "OUTAGE_IPV6_CONNECT_KEYWORDS", DEFAULT_OUTAGE_KEYWORDS.ipv6_connect_keywords
    )


settings = Settings()
