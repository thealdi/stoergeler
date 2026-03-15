from __future__ import annotations

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

import aiosmtplib

from .config import Settings

logger = logging.getLogger(__name__)


class EmailService:
    """Sends reports via email using SMTP (via aiosmtplib)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
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

        # Create message
        message = MIMEMultipart()
        message["From"] = self._settings.smtp_from
        message["To"] = ", ".join(target_recipients)
        message["Subject"] = subject
        message.attach(MIMEText(html_content, "html"))

        try:
            async with aiosmtplib.SMTP(
                hostname=self._settings.smtp_server,
                port=self._settings.smtp_port,
                use_tls=self._settings.smtp_tls,
                start_tls=False if self._settings.smtp_tls else False, # Handled by aiosmtplib logic
            ) as smtp:
                if self._settings.smtp_username and self._settings.smtp_password:
                    await smtp.login(
                        self._settings.smtp_username, 
                        self._settings.smtp_password
                    )
                await smtp.send_message(message)
                
            logger.info(f"Report email sent to {len(target_recipients)} recipients.")
        except Exception as exc:
            logger.error(f"Failed to send report email: {exc}")
            raise
