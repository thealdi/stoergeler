from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from backend.reporting import ReportingService, get_current_week_range, get_last_week_range


class TestFormatDuration:
    """Tests for ReportingService._format_duration (accessed via instance)."""

    @pytest.fixture()
    def service(self):
        return ReportingService(
            outage_repository=MagicMock(),
            device_log_repository=MagicMock(),
        )

    def test_zero_seconds(self, service):
        assert service._format_duration(0) == "0s"

    def test_seconds_only(self, service):
        assert service._format_duration(45) == "45s"

    def test_minutes_and_seconds(self, service):
        assert service._format_duration(125) == "2m 5s"

    def test_hours_minutes_seconds(self, service):
        assert service._format_duration(3661) == "1h 1m 1s"

    def test_days(self, service):
        assert service._format_duration(90061) == "1d 1h 1m 1s"

    def test_none_returns_unbekannt(self, service):
        assert service._format_duration(None) == "unbekannt"

    def test_nan_returns_unbekannt(self, service):
        assert service._format_duration(float("nan")) == "unbekannt"


class TestGetLastWeekRange:
    def test_returns_previous_monday_to_sunday(self):
        start, end = get_last_week_range()
        assert start.weekday() == 0  # Monday
        assert end.weekday() == 6  # Sunday
        assert start.hour == 0 and start.minute == 0 and start.second == 0
        assert end.hour == 23 and end.minute == 59 and end.second == 59
        assert (end - start).days == 6

    def test_is_in_the_past(self):
        start, end = get_last_week_range()
        now = datetime.now(timezone.utc)
        assert end < now


class TestGetCurrentWeekRange:
    def test_returns_current_monday_to_sunday(self):
        start, end = get_current_week_range()
        assert start.weekday() == 0
        assert end.weekday() == 6
        assert (end - start).days == 6

    def test_contains_now(self):
        start, end = get_current_week_range()
        now = datetime.now(timezone.utc)
        assert start <= now <= end


class TestGetReportData:
    @pytest.fixture()
    def repos(self):
        outage_repo = MagicMock()
        log_repo = MagicMock()
        return outage_repo, log_repo

    def test_empty_outages_100_percent_availability(self, repos):
        outage_repo, log_repo = repos
        outage_repo.list_outages.return_value = []
        log_repo.list_entries.return_value = []

        service = ReportingService(outage_repo, log_repo)
        start = datetime(2024, 1, 15, 0, 0, 0)
        end = datetime(2024, 1, 21, 23, 59, 59)
        data = service.get_report_data(start, end)

        assert data["availability"] == 100.0
        assert data["incident_count"] == 0
        assert data["total_downtime"] == 0

    def test_with_unplanned_outages(self, repos):
        from backend.models import OutageRecord

        outage_repo, log_repo = repos
        start = datetime(2024, 1, 15, 0, 0, 0)
        end = datetime(2024, 1, 21, 23, 59, 59)

        outage_repo.list_outages.return_value = [
            OutageRecord(
                start_time=datetime(2024, 1, 16, 10, 0, 0),
                end_time=datetime(2024, 1, 16, 10, 5, 0),
                duration_seconds=300,
                status="closed",
            ),
        ]
        log_repo.list_entries.return_value = []

        service = ReportingService(outage_repo, log_repo)
        data = service.get_report_data(start, end)

        assert data["incident_count"] == 1
        assert data["total_downtime"] == 300
        assert data["availability"] < 100.0
        assert data["mttr"] == 300.0

    def test_planned_outages_not_counted_as_incidents(self, repos):
        from backend.models import OutageRecord

        outage_repo, log_repo = repos
        start = datetime(2024, 1, 15, 0, 0, 0)
        end = datetime(2024, 1, 21, 23, 59, 59)

        outage_repo.list_outages.return_value = [
            OutageRecord(
                start_time=datetime(2024, 1, 16, 3, 0, 0),
                end_time=datetime(2024, 1, 16, 3, 2, 0),
                duration_seconds=120,
                status="planned",
            ),
        ]
        log_repo.list_entries.return_value = []

        service = ReportingService(outage_repo, log_repo)
        data = service.get_report_data(start, end)

        assert data["incident_count"] == 0
        assert data["planned_count"] == 1
        assert data["planned_downtime"] == 120
        assert data["availability"] == 100.0  # planned doesn't affect availability
