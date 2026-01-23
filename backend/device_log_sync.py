from __future__ import annotations

from typing import Any, Dict, Iterable

from .database import DeviceLogRepository, OutageRepository
from .fritzbox_client import FritzboxClient
from .outage_calculator import OutageCalculator


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
        entries: Iterable[Dict[str, Any]] = self._fritzbox_client.fetch_device_log()
        self._device_log_repository.ingest_entries(entries)
        stored_entries = self._device_log_repository.list_entries()
        outages = self._outage_calculator.calculate(stored_entries)
        self._outage_repository.replace_outages(outages)
