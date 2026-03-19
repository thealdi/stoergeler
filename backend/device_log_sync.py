from __future__ import annotations

import logging
from typing import Any, Dict, Iterable

from .database import DeviceLogRepository, OutageRepository
from .fritzbox_client import FritzboxClient
from .outage_calculator import OutageCalculator

logger = logging.getLogger(__name__)


class DeviceLogSync:
    """Fetches device logs, persists them, and recalculates outages."""

    def __init__(
        self,
        fritzbox_client: FritzboxClient,
        device_log_repository: DeviceLogRepository,
        outage_repository: OutageRepository,
        outage_calculator: OutageCalculator,
    ) -> None:
        self._fritzbox_client = fritzbox_client
        self._device_log_repository = device_log_repository
        self._outage_repository = outage_repository
        self._outage_calculator = outage_calculator

    def run_once(self) -> None:
        entries = list(self._fritzbox_client.fetch_device_log())
        new_count = self._device_log_repository.ingest_entries(entries)
        if new_count == 0:
            logger.debug("Device log sync: no new entries, skipping recalculation")
            return
        stored_entries = self._device_log_repository.list_entries()
        outages = self._outage_calculator.calculate(stored_entries)
        self._outage_repository.replace_outages(outages)
        logger.info(
            "Device log sync: %d new entries ingested, %d outages calculated",
            new_count,
            len(outages),
        )
