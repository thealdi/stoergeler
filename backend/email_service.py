from __future__ import annotations

import logging
from typing import List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from .config import Settings

logger = logging.getLogger(__name__)


class EmailService:
    """Sends reports via email using SMTP."""

    def __init__(self, settings: Settings) -> None:
        self._conf = ConnectionConfig(
            MAIL_USERNAME=settings.smtp_username,
            MAIL_PASSWORD=settings.smtp_password,
            MAIL_FROM=settings.smtp_from,
            MAIL_PORT=settings.smtp_port,
            MAIL_SERVER=settings.smtp_server,
            MAIL_STARTTLS=settings.smtp_tls,
            MAIL_SSL_TLS=settings.smtp_ssl,
            USE_CREDENTIALS=bool(settings.smtp_username),
            VALIDATE_CERTS=True,
        )
        self._recipients = list(settings.report_recipients)

    async def send_report(
        self,
        subject: str,
        html_content: str,
        recipients: List[str] | None = None,
    ) -> None:
        """Sends an HTML email to the configured recipients."""
        target_recipients = recipients if recipients is not None else self._recipients
        
        if not target_recipients:
            logger.warning("No email recipients configured. Skipping email send.")
            return

        message = MessageSchema(
            subject=subject,
            recipients=target_recipients,
            body=html_content,
            subtype=MessageType.html,
        )

        fm = FastMail(self._conf)
        try:
            await fm.send_message(message)
            logger.info(f"Report email sent to {len(target_recipients)} recipients.")
        except Exception as exc:
            logger.error(f"Failed to send report email: {exc}")
            raise
