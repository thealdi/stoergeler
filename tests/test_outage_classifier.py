from __future__ import annotations

from datetime import datetime

import pytest

from backend.outage_classifier import categorize_log_entry
from tests.conftest import default_keywords, make_log_entry

DT = datetime(2024, 1, 1)


def _categorize(message: str):
    entry = make_log_entry(1, DT, message)
    return categorize_log_entry(entry, default_keywords)


class TestCategorizeLogEntry:
    def test_planned_keyword(self):
        assert _categorize("Zwangstrennung durch Provider") == ("both", "planned_hint")

    def test_planned_keyword_wird_kurz_unterbrochen(self):
        assert _categorize("Verbindung wird kurz unterbrochen") == ("both", "planned_hint")

    def test_ipv4_disconnect(self):
        assert _categorize("Internetverbindung wurde getrennt") == ("ipv4", "disconnect")

    def test_ipv4_connect(self):
        assert _categorize("Internetverbindung wurde erfolgreich hergestellt") == ("ipv4", "connect")

    def test_ipv6_disconnect(self):
        assert _categorize("Internetverbindung IPv6 wurde getrennt") == ("ipv6", "disconnect")

    def test_ipv6_connect(self):
        assert _categorize("Internetverbindung IPv6 wurde erfolgreich hergestellt") == ("ipv6", "connect")

    def test_ipv6_prefix_disconnect(self):
        assert _categorize("IPv6-Präfix ist nicht mehr gültig") == ("ipv6", "disconnect")

    def test_ipv6_prefix_connect(self):
        assert _categorize("IPv6-Präfix wurde erfolgreich bezogen") == ("ipv6", "connect")

    def test_unknown_message(self):
        assert _categorize("WLAN wurde aktiviert") == ("unknown", "ignore")

    def test_empty_message(self):
        assert _categorize("") == ("unknown", "ignore")

    def test_none_message(self):
        entry = make_log_entry(1, DT, "placeholder")
        # Simulate None by patching message attribute
        object.__setattr__(entry, "message", None)
        assert categorize_log_entry(entry, default_keywords) == ("unknown", "ignore")

    def test_case_insensitivity_uppercase(self):
        assert _categorize("ZWANGSTRENNUNG DURCH PROVIDER") == ("both", "planned_hint")

    def test_case_insensitivity_mixed(self):
        assert _categorize("InternetVerbindung Wurde Getrennt") == ("ipv4", "disconnect")

    def test_planned_takes_priority_over_disconnect(self):
        """If a message matches both planned and disconnect, planned wins."""
        from backend.outage_config import OutageKeywords

        cfg = OutageKeywords(
            planned_keywords=("test keyword",),
            ipv4_disconnect_keywords=("test keyword",),
            ipv4_connect_keywords=(),
            ipv6_disconnect_keywords=(),
            ipv6_connect_keywords=(),
        )
        entry = make_log_entry(1, DT, "test keyword")
        assert categorize_log_entry(entry, cfg) == ("both", "planned_hint")

    def test_ipv6_checked_before_ipv4(self):
        """If a message matches both IPv6 and IPv4 keywords, IPv6 wins."""
        from backend.outage_config import OutageKeywords

        cfg = OutageKeywords(
            planned_keywords=(),
            ipv4_disconnect_keywords=("shared keyword",),
            ipv4_connect_keywords=(),
            ipv6_disconnect_keywords=("shared keyword",),
            ipv6_connect_keywords=(),
        )
        entry = make_log_entry(1, DT, "shared keyword")
        assert categorize_log_entry(entry, cfg) == ("ipv6", "disconnect")
