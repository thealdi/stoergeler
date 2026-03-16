from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, PropertyMock

import pytest

from backend.device_log_sync import DeviceLogSync
from backend.models import DeviceLogEntryRecord


@pytest.fixture()
def mocks():
    fritzbox = MagicMock()
    log_repo = MagicMock()
    outage_repo = MagicMock()
    calculator = MagicMock()
    return fritzbox, log_repo, outage_repo, calculator


@pytest.fixture()
def sync(mocks):
    fritzbox, log_repo, outage_repo, calculator = mocks
    return DeviceLogSync(fritzbox, log_repo, outage_repo, calculator)


class TestDeviceLogSync:
    def test_calls_pipeline_in_order(self, mocks, sync):
        fritzbox, log_repo, outage_repo, calculator = mocks
        fritzbox.fetch_device_log.return_value = [
            {"timestamp": "2024-01-15T10:00:00", "message": "msg1"},
        ]
        log_repo.ingest_entries.return_value = 1
        stored = [
            DeviceLogEntryRecord(1, datetime(2024, 1, 15, 10), "msg1", None, "tr064"),
        ]
        log_repo.list_entries.return_value = stored
        calculator.calculate.return_value = [{"outage": "data"}]

        sync.run_once()

        fritzbox.fetch_device_log.assert_called_once()
        log_repo.ingest_entries.assert_called_once()
        log_repo.list_entries.assert_called_once()
        calculator.calculate.assert_called_once_with(stored)
        outage_repo.replace_outages.assert_called_once_with([{"outage": "data"}])

    def test_passes_fritzbox_entries_to_ingest(self, mocks, sync):
        fritzbox, log_repo, outage_repo, calculator = mocks
        raw_entries = [
            {"timestamp": "2024-01-15T10:00:00", "message": "a"},
            {"timestamp": "2024-01-15T10:01:00", "message": "b"},
        ]
        fritzbox.fetch_device_log.return_value = raw_entries
        log_repo.ingest_entries.return_value = 2
        log_repo.list_entries.return_value = []
        calculator.calculate.return_value = []

        sync.run_once()

        log_repo.ingest_entries.assert_called_once_with(raw_entries)

    def test_empty_fritzbox_still_recalculates(self, mocks, sync):
        fritzbox, log_repo, outage_repo, calculator = mocks
        fritzbox.fetch_device_log.return_value = []
        log_repo.ingest_entries.return_value = 0
        log_repo.list_entries.return_value = []
        calculator.calculate.return_value = []

        sync.run_once()

        calculator.calculate.assert_called_once_with([])
        outage_repo.replace_outages.assert_called_once_with([])

    def test_fritzbox_error_propagates(self, mocks, sync):
        fritzbox, log_repo, outage_repo, calculator = mocks
        fritzbox.fetch_device_log.side_effect = ConnectionError("network down")

        with pytest.raises(ConnectionError, match="network down"):
            sync.run_once()
