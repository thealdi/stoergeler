from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.app_factory import Dependencies, create_app
from backend.models import DeviceLogEntryRecord, OutageRecord


@pytest.fixture()
def mock_deps():
    """Create a Dependencies object with all mocks."""
    tracker = MagicMock()
    device_log_repo = MagicMock()
    outage_repo = MagicMock()
    reporting_service = MagicMock()
    email_service = MagicMock()
    email_service.send_report = AsyncMock()
    report_scheduler = MagicMock()
    report_scheduler.start = AsyncMock()
    report_scheduler.stop = AsyncMock()
    tracker.start = AsyncMock()
    tracker.stop = AsyncMock()

    return Dependencies(
        tracker=tracker,
        device_log_repository=device_log_repo,
        outage_repository=outage_repo,
        reporting_service=reporting_service,
        email_service=email_service,
        report_scheduler=report_scheduler,
    )


@pytest.fixture()
def client(mock_deps):
    app = create_app(deps=mock_deps)
    return TestClient(app, root_path="")


class TestHealthEndpoint:
    def test_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestVersionEndpoint:
    def test_returns_version(self, client):
        resp = client.get("/version")
        assert resp.status_code == 200
        data = resp.json()
        assert "version" in data
        assert "commit" in data


class TestStatusEndpoint:
    def test_returns_status(self, client, mock_deps):
        now = datetime.now(timezone.utc)
        mock_deps.tracker.poll_now.return_value = {
            "timestamp": now.isoformat(),
            "status": "online",
            "details": {"external_ip": "1.2.3.4"},
        }
        resp = client.get("/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "online"

    def test_returns_503_on_connection_error(self, client, mock_deps):
        mock_deps.tracker.poll_now.side_effect = ConnectionError("network down")
        resp = client.get("/status")
        assert resp.status_code == 503


class TestDeviceLogEndpoint:
    def test_returns_entries(self, client, mock_deps):
        dt = datetime(2024, 1, 15, 10, 0, 0)
        mock_deps.device_log_repository.list_entries.return_value = [
            DeviceLogEntryRecord(id=1, timestamp=dt, message="test msg", raw="raw line", source="tr064"),
        ]
        resp = client.get("/device-log")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["entries"]) == 1
        assert data["entries"][0]["message"] == "test msg"

    def test_passes_limit_param(self, client, mock_deps):
        mock_deps.device_log_repository.list_entries.return_value = []
        resp = client.get("/device-log?limit=10")
        assert resp.status_code == 200
        mock_deps.device_log_repository.list_entries.assert_called_once_with(
            limit=10, ascending=False, start=None, end=None,
        )

    def test_passes_start_end_params(self, client, mock_deps):
        mock_deps.device_log_repository.list_entries.return_value = []
        resp = client.get("/device-log?start=2024-01-15T00:00:00Z&end=2024-01-15T23:59:59Z")
        assert resp.status_code == 200
        call_kwargs = mock_deps.device_log_repository.list_entries.call_args
        assert call_kwargs.kwargs["start"] is not None
        assert call_kwargs.kwargs["end"] is not None

    def test_rejects_invalid_limit(self, client):
        resp = client.get("/device-log?limit=0")
        assert resp.status_code == 422


class TestOutagesEndpoint:
    def test_returns_outage_list(self, client, mock_deps):
        dt = datetime(2024, 1, 15, 10, 0, 0)
        mock_deps.outage_repository.list_outages.return_value = [
            OutageRecord(
                start_time=dt,
                end_time=dt + timedelta(minutes=5),
                duration_seconds=300,
                status="closed",
            ),
        ]
        resp = client.get("/outages")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["outages"]) == 1
        assert data["outages"][0]["duration_seconds"] == 300

    def test_returns_empty_list(self, client, mock_deps):
        mock_deps.outage_repository.list_outages.return_value = []
        resp = client.get("/outages")
        assert resp.status_code == 200
        assert resp.json()["outages"] == []


class TestCreateOutageEndpoint:
    def test_creates_outage(self, client, mock_deps):
        mock_deps.outage_repository.create_outage.return_value = 42
        body = {
            "start": "2024-01-15T10:00:00",
            "end": "2024-01-15T10:05:00",
            "status": "manual",
        }
        resp = client.post("/outages", json=body)
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == 42
        assert data["outage"]["duration_seconds"] == 300

    def test_creates_open_outage(self, client, mock_deps):
        mock_deps.outage_repository.create_outage.return_value = 43
        body = {"start": "2024-01-15T10:00:00"}
        resp = client.post("/outages", json=body)
        assert resp.status_code == 201
        data = resp.json()
        assert data["outage"]["duration_seconds"] is None


class TestRecalculateEndpoint:
    def test_recalculates_and_returns_count(self, client, mock_deps):
        mock_deps.outage_calculator = MagicMock()
        mock_deps.outage_repository.list_outages.return_value = []
        mock_deps.device_log_repository.list_entries.return_value = []
        mock_deps.outage_calculator.calculate.return_value = [{}, {}, {}]
        resp = client.post("/outages/recalculate")
        assert resp.status_code == 200
        assert resp.json()["outages"] == 3
        mock_deps.outage_repository.replace_outages.assert_called_once()

    def test_returns_503_without_calculator(self, client, mock_deps):
        # mock_deps leaves outage_calculator as its default (None)
        resp = client.post("/outages/recalculate")
        assert resp.status_code == 503


class TestConnectionCheckEndpoint:
    def test_returns_connectivity(self, client, mock_deps):
        mock_deps.tracker.check_connection.return_value = {
            "connected": True,
            "external_ip": "1.2.3.4",
        }
        resp = client.get("/connection-check")
        assert resp.status_code == 200
        assert resp.json()["connected"] is True

    def test_returns_503_on_error(self, client, mock_deps):
        mock_deps.tracker.check_connection.side_effect = OSError("timeout")
        resp = client.get("/connection-check")
        assert resp.status_code == 503


class TestWeeklyReportEndpoint:
    def test_returns_html(self, client, mock_deps):
        mock_deps.reporting_service.get_report_data.return_value = {"week_number": 3}
        mock_deps.reporting_service.render_weekly_report.return_value = "<html>report</html>"
        resp = client.get("/report/weekly")
        assert resp.status_code == 200
        assert "report" in resp.text


class TestSendTestEmailEndpoint:
    def test_sends_email(self, client, mock_deps):
        mock_deps.reporting_service.get_report_data.return_value = {
            "week_number": 3,
            "start": datetime(2024, 1, 8),
            "end": datetime(2024, 1, 14),
        }
        mock_deps.reporting_service.render_weekly_report.return_value = "<html>report</html>"
        resp = client.post("/report/send-test-email")
        assert resp.status_code == 200
        assert resp.json() == {"status": "sent"}
        mock_deps.email_service.send_report.assert_called_once()
