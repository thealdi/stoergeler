from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from .config import Settings
from .database import MetadataRepository
from .email_service import EmailService
from .periodic_runner import PeriodicRunner
from .reporting import ReportingService, get_last_week_range

logger = logging.getLogger(__name__)


class ReportScheduler:
    """Orchestrates periodic report generation and email delivery."""

    def __init__(
        self,
        settings: Settings,
        metadata_repository: MetadataRepository,
        reporting_service: ReportingService,
        email_service: EmailService,
    ) -> None:
        self._settings = settings
        self._metadata_repo = metadata_repository
        self._reporting_service = reporting_service
        self._email_service = email_service
        
        self._runner = PeriodicRunner(
            interval_seconds=settings.report_schedule_check_interval_seconds,
            work=self.check_and_send,
            on_error=self._handle_error,
        )

    async def start(self) -> None:
        await self._runner.start()

    async def stop(self) -> None:
        await self._runner.stop()

    async def check_and_send(self) -> None:
        """Periodic check if it's time to send the weekly report."""
        now = datetime.now(timezone.utc)
        
        # We send reports on Mondays between 00:00 and 23:59 (checked every interval)
        if now.weekday() != 0:  # 0 is Monday
            return

        last_sent_iso = self._metadata_repo.get("last_weekly_report_sent_at")
        current_week_key = f"{now.year}-W{now.isocalendar()[1]}"
        
        if last_sent_iso == current_week_key:
            logger.debug(f"Weekly report for {current_week_key} already sent.")
            return

        logger.info(f"It's Monday! Preparing weekly report for {current_week_key}...")
        
        # Generate report for LAST week
        start, end = get_last_week_range()
        data = self._reporting_service.get_report_data(start, end)
        html_content = self._reporting_service.render_weekly_report(data)
        
        subject = f"StoerGeler Wochen-Report (KW {data['week_number']})"
        body_template = self._settings.report_email_body.replace("\\n", "\n")
        body_text = body_template.format(
            week_number=data["week_number"],
            start_date=data["start"].strftime("%d.%m.%Y"),
            end_date=data["end"].strftime("%d.%m.%Y"),
        )
        filename = f"verbindungs_report_kw{data['week_number']}.html"
        
        await self._email_service.send_report(
            subject=subject, 
            html_content=html_content,
            body_text=body_text,
            filename=filename
        )
        
        self._metadata_repo.set("last_weekly_report_sent_at", current_week_key)
        logger.info(f"Weekly report for {current_week_key} sent successfully.")

    def _handle_error(self, exc: Exception) -> None:
        logger.error(f"Error in ReportScheduler: {exc}")
