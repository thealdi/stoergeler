from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OutageKeywords:
    planned_keywords: tuple[str, ...]
    ipv4_disconnect_keywords: tuple[str, ...]
    ipv4_connect_keywords: tuple[str, ...]
    ipv6_disconnect_keywords: tuple[str, ...]
    ipv6_connect_keywords: tuple[str, ...]


DEFAULT_OUTAGE_KEYWORDS = OutageKeywords(
    planned_keywords=(
        "zwangstrennung",
        "wird kurz unterbrochen",
        "trennung durch den anbieter",
    ),
    ipv4_disconnect_keywords=("internetverbindung wurde getrennt",),
    ipv4_connect_keywords=("internetverbindung wurde erfolgreich hergestellt",),
    ipv6_disconnect_keywords=(
        "internetverbindung ipv6 wurde getrennt",
        "ipv6-präfix ist nicht mehr gültig",
        "ipv6-präfix nicht mehr gültig",
    ),
    ipv6_connect_keywords=(
        "internetverbindung ipv6 wurde erfolgreich hergestellt",
        "internetverbindung ipv6 wurde erfolgreich bezogen",
        "ipv6-präfix wurde erfolgreich bezogen",
    ),
)
