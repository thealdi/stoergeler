from __future__ import annotations

import logging
from email.mime.application import MIMEApplication
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
        body_text: str = "Anbei finden Sie den aktuellen Verbindungs-Report.",
        filename: str = "report.html",
        recipients: List[str] | None = None,
    ) -> None:
        """Sends an email with the HTML report as an attachment."""
        target_recipients = recipients if recipients is not None else self._recipients
        
        if not target_recipients:
            logger.warning("No email recipients configured. Skipping email send.")
            return

        # Create message
        message = MIMEMultipart()
        message["From"] = self._settings.smtp_from
        message["To"] = ", ".join(target_recipients)
        message["Subject"] = subject
        
        # Attach body text
        message.attach(MIMEText(body_text, "plain"))

        # Attach HTML report
        attachment = MIMEText(html_content, "html")
        attachment.add_header("Content-Disposition", "attachment", filename=filename)
        message.attach(attachment)

        try:
            async with aiosmtplib.SMTP(
                hostname=self._settings.smtp_server,
                port=self._settings.smtp_port,
                use_tls=self._settings.smtp_ssl,
                timeout=30,
            ) as smtp:
                if not self._settings.smtp_ssl and self._settings.smtp_tls:
                    await smtp.starttls()
                if self._settings.smtp_username and self._settings.smtp_password:
                    await smtp.login(
                        self._settings.smtp_username,
                        self._settings.smtp_password,
                    )
                await smtp.send_message(message)
                
            logger.info(
                "Report email sent to %d recipients, subject=%r, body_preview=%r",
                len(target_recipients), subject, body_text[:80],
            )
        except Exception as exc:
            logger.error(f"Failed to send report email: {exc}")
            raise
