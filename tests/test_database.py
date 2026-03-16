from __future__ import annotations

from datetime import datetime, timedelta


class TestInitSchema:
    def test_idempotent(self, db_context):
        """Calling init_schema twice does not raise."""
        db_context.init_schema()
        db_context.init_schema()


class TestDeviceLogRepository:
    def test_ingest_returns_count(self, device_log_repo):
        entries = [
            {"timestamp": "2024-01-15T10:00:00", "message": "msg1"},
            {"timestamp": "2024-01-15T10:01:00", "message": "msg2"},
        ]
        assert device_log_repo.ingest_entries(entries) == 2

    def test_duplicates_return_zero(self, device_log_repo):
        entries = [{"timestamp": "2024-01-15T10:00:00", "message": "msg1"}]
        device_log_repo.ingest_entries(entries)
        assert device_log_repo.ingest_entries(entries) == 0

    def test_missing_fields_skipped(self, device_log_repo):
        entries = [
            {"timestamp": "2024-01-15T10:00:00"},  # no message
            {"message": "no timestamp"},  # no timestamp
            {},  # empty
        ]
        assert device_log_repo.ingest_entries(entries) == 0

    def test_list_entries_round_trip(self, device_log_repo):
        entries = [
            {"timestamp": "2024-01-15T10:00:00", "message": "msg1"},
            {"timestamp": "2024-01-15T10:01:00", "message": "msg2"},
        ]
        device_log_repo.ingest_entries(entries)
        records = device_log_repo.list_entries()
        assert len(records) == 2
        assert records[0].message == "msg1"
        assert records[1].message == "msg2"


class TestStatusRepository:
    def test_record_and_latest(self, status_repo):
        dt = datetime(2024, 1, 15, 10, 0, 0)
        status_repo.record_event("online", dt, details="test")
        event = status_repo.latest_event()
        assert event is not None
        assert event.status == "online"
        assert event.timestamp == dt
        assert event.details == "test"

    def test_latest_returns_most_recent(self, status_repo):
        dt1 = datetime(2024, 1, 15, 10, 0, 0)
        dt2 = datetime(2024, 1, 15, 11, 0, 0)
        status_repo.record_event("online", dt1)
        status_repo.record_event("offline", dt2)
        event = status_repo.latest_event()
        assert event.status == "offline"

    def test_empty_table_returns_none(self, status_repo):
        assert status_repo.latest_event() is None


class TestOutageRepository:
    def test_replace_preserves_manual_outages(self, outage_repo):
        dt = datetime(2024, 1, 15, 10, 0, 0)
        # Insert a manual outage
        outage_repo.create_outage(
            start_time=dt,
            end_time=dt + timedelta(minutes=5),
            status="manual",
        )
        # Replace calculated outages (should not touch manual)
        outage_repo.replace_outages([
            {
                "start_time": dt + timedelta(hours=1),
                "end_time": dt + timedelta(hours=1, minutes=3),
                "duration_seconds": 180,
                "status": "closed",
                "start_log_entry_id": None,
                "end_log_entry_id": None,
            }
        ])
        outages = outage_repo.list_outages()
        assert len(outages) == 2
        statuses = {o.status for o in outages}
        assert "manual" in statuses
        assert "closed" in statuses

    def test_replace_clears_previous_calculated(self, outage_repo):
        dt = datetime(2024, 1, 15, 10, 0, 0)
        outage_repo.replace_outages([
            {
                "start_time": dt,
                "end_time": dt + timedelta(minutes=5),
                "duration_seconds": 300,
                "status": "closed",
                "start_log_entry_id": None,
                "end_log_entry_id": None,
            }
        ])
        # Replace with empty list
        outage_repo.replace_outages([])
        assert outage_repo.list_outages() == []

    def test_create_outage_auto_duration(self, outage_repo):
        dt = datetime(2024, 1, 15, 10, 0, 0)
        row_id = outage_repo.create_outage(
            start_time=dt,
            end_time=dt + timedelta(minutes=10),
        )
        assert row_id is not None
        outages = outage_repo.list_outages()
        assert len(outages) == 1
        assert outages[0].duration_seconds == 600

    def test_create_outage_returns_row_id(self, outage_repo):
        dt = datetime(2024, 1, 15, 10, 0, 0)
        row_id = outage_repo.create_outage(start_time=dt, status="manual")
        assert isinstance(row_id, int)
        assert row_id > 0


class TestMetadataRepository:
    def test_get_set_round_trip(self, metadata_repo):
        metadata_repo.set("test_key", "test_value")
        assert metadata_repo.get("test_key") == "test_value"

    def test_get_missing_returns_none(self, metadata_repo):
        assert metadata_repo.get("nonexistent") is None

    def test_overwrite_existing_key(self, metadata_repo):
        metadata_repo.set("key", "value1")
        metadata_repo.set("key", "value2")
        assert metadata_repo.get("key") == "value2"
