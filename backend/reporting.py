from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .database import DeviceLogRepository, OutageRepository
from .models import DeviceLogEntryRecord, OutageRecord


class ReportingService:
    """Calculates KPIs and renders HTML reports."""

    def __init__(
        self,
        outage_repository: OutageRepository,
        device_log_repository: DeviceLogRepository,
        template_dir: str = "backend/templates",
    ) -> None:
        self._outage_repo = outage_repository
        self._device_log_repo = device_log_repository
        self._jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )
        # Register custom filters for formatting
        self._jinja_env.filters["format_date"] = self._format_date
        self._jinja_env.filters["format_duration"] = self._format_duration

    def get_report_data(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Aggregates data and calculates KPIs for a given range."""
        outages = self._outage_repo.list_outages(start=start, end=end)
        logs = self._device_log_repo.list_entries(start=start, end=end)

        unplanned = [o for o in outages if not o.status.startswith("planned")]
        planned = [o for o in outages if o.status.startswith("planned")]

        total_downtime = sum(o.duration_seconds or 0 for o in unplanned)
        planned_downtime = sum(o.duration_seconds or 0 for o in planned)
        max_downtime = max((o.duration_seconds or 0 for o in unplanned), default=0)

        total_seconds = (end - start).total_seconds()
        uptime_seconds = max(0, total_seconds - total_downtime)
        availability = (uptime_seconds / total_seconds) * 100 if total_seconds > 0 else 100

        # MTTR (Mean Time To Repair)
        mttr = total_downtime / len(unplanned) if unplanned else 0

        # MTBF (Mean Time Between Failures)
        mtbf = (total_seconds - total_downtime) / len(unplanned) if unplanned else total_seconds

        # Weekly Overview Data
        weekly_overview = []
        for day in range(7):
            current_day = start + timedelta(days=day)
            day_name = current_day.strftime("%a")
            day_outages = [o for o in outages if o.start_time.date() == current_day.date()]
            weekly_overview.append((day_name, day_outages))

        return {
            "start": start,
            "end": end,
            "availability": availability,
            "total_downtime": total_downtime,
            "planned_downtime": planned_downtime,
            "max_downtime": max_downtime,
            "incident_count": len(unplanned),
            "planned_count": len(planned),
            "mttr": mttr,
            "mtbf": mtbf,
            "outages": outages,
            "logs": logs,
            "week_number": self._get_week_number(start),
            "weekly_overview": weekly_overview,
        }

    def render_weekly_report(self, data: Dict[str, Any]) -> str:
        """Renders the HTML report using Jinja2."""
        template = self._jinja_env.get_template("weekly_report.html")
        return template.render(**data)

    def _get_week_number(self, dt: datetime) -> int:
        return dt.isocalendar()[1]

    def _format_date(self, value: datetime) -> str:
        return value.strftime("%d.%m.%Y %H:%M:%S")

    def _format_duration(self, duration_seconds: Optional[float]) -> str:
        if duration_seconds is None or math.isnan(duration_seconds):
            return "unbekannt"
        
        total_seconds = max(0, int(duration_seconds))
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        parts = []
        if days: parts.append(f"{days}d")
        if hours: parts.append(f"{hours}h")
        if minutes: parts.append(f"{minutes}m")
        if seconds or not parts: parts.append(f"{seconds}s")
        
        return " ".join(parts)


def get_last_week_range() -> tuple[datetime, datetime]:
    """Returns (monday_start, sunday_end) for the previous full week."""
    now = datetime.now(timezone.utc)
    # Get last Monday
    last_monday = now - timedelta(days=now.weekday() + 7)
    last_monday = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    last_sunday = last_monday + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    return last_monday, last_sunday

def get_current_week_range() -> tuple[datetime, datetime]:
    """Returns (monday_start, sunday_end) for the current week."""
    now = datetime.now(timezone.utc)
    monday = now - timedelta(days=now.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    sunday = monday + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    return monday, sunday
