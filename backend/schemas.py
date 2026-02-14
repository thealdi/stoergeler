from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    timestamp: datetime = Field(description="Zeitpunkt der Messung im ISO-Format")
    status: str = Field(description="online|offline|error")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Metadaten der Fritzbox-Antwort"
    )


class DeviceLogEntry(BaseModel):
    timestamp: Optional[datetime] = Field(
        default=None, description="Zeitstempel des Logeintrags als ISO-Zeit"
    )
    message: Optional[str] = Field(
        default=None, description="Vom Router gemeldete Nachricht"
    )
    raw: str = Field(description="Unverarbeitete Logzeile")


class DeviceLogResponse(BaseModel):
    entries: List[DeviceLogEntry] = Field(
        description="Zeilen aus dem Fritzbox-Ereignisprotokoll"
    )


class OutageWindow(BaseModel):
    start: datetime = Field(description="Beginn der Störung (offline erkannt)")
    end: Optional[datetime] = Field(
        default=None, description="Ende der Störung (online erkannt)"
    )
    duration_seconds: Optional[int] = Field(
        default=None,
        description="Dauer in Sekunden; None wenn die Störung noch läuft",
    )
    status: Optional[str] = Field(
        default=None, description="open|closed je nach aktuellem Zustand"
    )


class OutageListResponse(BaseModel):
    outages: List[OutageWindow]


class OutageCreate(BaseModel):
    start: datetime = Field(description="Beginn der Störung")
    end: Optional[datetime] = Field(default=None, description="Ende der Störung (leer = noch offen)")
    status: str = Field(default="manual", description="Status der Störung (z.B. manual, closed, open)")


class OutageCreateResponse(BaseModel):
    id: int = Field(description="ID des neu erstellten Outage-Eintrags")
    outage: OutageWindow


class ConnectivityStatus(BaseModel):
    connected: bool = Field(description="Gibt an, ob laut TR-064 derzeit eine Verbindung besteht")
    external_ip: Optional[str] = Field(default=None, description="Vom Router gemeldete externe IP")
    wan_access_type: Optional[str] = Field(default=None, description="Verbindungstyp laut FritzStatus")
    wan_link_status: Optional[str] = Field(default=None, description="WAN-Link-Status laut Fritzbox")
    max_bit_rate: Optional[str] = Field(default=None, description="Maximaler Up-/Downstream laut Fritzbox")
    uptime: Optional[Union[int, str]] = Field(
        default=None, description="Online-Dauer laut Fritzbox (Sekunden oder formatiert)"
    )
