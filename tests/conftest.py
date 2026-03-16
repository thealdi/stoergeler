from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from backend.database import (
    DatabaseContext,
    DeviceLogRepository,
    MetadataRepository,
    OutageRepository,
    StatusRepository,
)
from backend.models import DeviceLogEntryRecord
from backend.outage_config import DEFAULT_OUTAGE_KEYWORDS


@pytest.fixture()
def db_context(tmp_path):
    ctx = DatabaseContext(tmp_path / "test.db")
    ctx.init_schema()
    return ctx


@pytest.fixture()
def status_repo(db_context):
    return StatusRepository(db_context)


@pytest.fixture()
def device_log_repo(db_context):
    return DeviceLogRepository(db_context)


@pytest.fixture()
def outage_repo(db_context):
    return OutageRepository(db_context)


@pytest.fixture()
def metadata_repo(db_context):
    return MetadataRepository(db_context)


def make_log_entry(
    id: int,
    timestamp: datetime,
    message: str,
    raw: Optional[str] = None,
    source: Optional[str] = "tr064",
) -> DeviceLogEntryRecord:
    return DeviceLogEntryRecord(
        id=id, timestamp=timestamp, message=message, raw=raw, source=source
    )


default_keywords = DEFAULT_OUTAGE_KEYWORDS
