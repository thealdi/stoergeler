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

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # SMTP Settings
    smtp_server: str = os.getenv("SMTP_SERVER", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "noreply@stoergeler.local")
    smtp_tls: bool = os.getenv("SMTP_TLS", "True").lower() == "true"
    smtp_ssl: bool = os.getenv("SMTP_SSL", "False").lower() == "true"

    # Reporting Settings
    report_recipients: tuple[str, ...] = _parse_csv_env("REPORT_RECIPIENTS", ())
    report_email_body: str = os.getenv(
        "REPORT_EMAIL_BODY", 
        "Hallo,\n\nanbei erhalten Sie den Verbindungs-Report für die Kalenderwoche {week_number} ({start_date} bis {end_date}).\n\nIhre StoerGeler Instanz"
    )
    report_schedule_check_interval_seconds: int = int(
        os.getenv("REPORT_SCHEDULE_CHECK_INTERVAL_SECONDS", "3600")
    )


settings = Settings()
