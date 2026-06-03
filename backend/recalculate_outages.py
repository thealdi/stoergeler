"""One-off maintenance script: recompute the outages table from stored logs.

The ``outages`` table is normally rebuilt on every device-log sync, so it
self-heals after a calculator change once the next new log entry arrives. This
script forces that recalculation immediately — useful right after a deployment
that changes outage logic (e.g. merging coinciding IPv4/IPv6 outages) so the
correction does not depend on Fritzbox connectivity or a fresh log entry.

It is idempotent and only touches calculated outages: ``replace_outages``
deletes ``source = 'calculated'`` rows and re-inserts them, leaving any
manually-created outages intact.

Run during deployment with:

    python -m backend.recalculate_outages
"""

from __future__ import annotations

import logging

from .config import settings
from .database import DatabaseContext, DeviceLogRepository, OutageRepository
from .outage_calculator import OutageCalculator
from .outage_config import OutageKeywords

logger = logging.getLogger(__name__)


def recalculate_outages(
    device_log_repository: DeviceLogRepository,
    outage_repository: OutageRepository,
    outage_calculator: OutageCalculator,
) -> int:
    """Rebuild the calculated outages from all stored device log entries.

    Idempotent and only touches calculated outages: ``replace_outages`` deletes
    ``source = 'calculated'`` rows and re-inserts them, leaving manually-created
    outages intact. Returns the number of outages written.
    """
    before = len(outage_repository.list_outages())
    entries = device_log_repository.list_entries()
    outages = outage_calculator.calculate(entries)
    outage_repository.replace_outages(outages)
    after = len(outage_repository.list_outages())

    logger.info(
        "Recalculated outages from %d log entries: %d calculated, "
        "table went from %d to %d total rows",
        len(entries),
        len(outages),
        before,
        after,
    )
    return len(outages)


def main() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    db_context = DatabaseContext(settings.database_path)
    db_context.init_schema()
    outage_calculator = OutageCalculator(
        cfg=OutageKeywords(
            planned_keywords=settings.outage_planned_keywords,
            ipv4_disconnect_keywords=settings.outage_ipv4_disconnect_keywords,
            ipv4_connect_keywords=settings.outage_ipv4_connect_keywords,
            ipv6_disconnect_keywords=settings.outage_ipv6_disconnect_keywords,
            ipv6_connect_keywords=settings.outage_ipv6_connect_keywords,
        )
    )
    recalculate_outages(
        device_log_repository=DeviceLogRepository(db_context),
        outage_repository=OutageRepository(db_context),
        outage_calculator=outage_calculator,
    )


if __name__ == "__main__":
    main()
