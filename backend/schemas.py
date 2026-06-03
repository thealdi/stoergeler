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


class OutageRecalculateResponse(BaseModel):
    outages: int = Field(description="Anzahl der neu berechneten Störungen")


class ConnectivityStatus(BaseModel):
    connected: bool = Field(description="Gibt an, ob laut TR-064 derzeit eine Verbindung besteht")
    external_ip: Optional[str] = Field(default=None, description="Vom Router gemeldete externe IPv4")
    external_ipv6: Optional[str] = Field(default=None, description="Vom Router gemeldete externe IPv6")
    connection_service: Optional[str] = Field(default=None, description="Verbindungstyp (z.B. WANPPPConnection)")
    is_linked: Optional[bool] = Field(default=None, description="Physische Verbindung zum Provider aktiv")
    max_bit_rate: Optional[str] = Field(default=None, description="Maximaler Up-/Downstream laut Fritzbox")
    transmission_rate: Optional[str] = Field(default=None, description="Aktuelle Übertragungsrate Up-/Downstream in Bytes/s")
    uptime: Optional[str] = Field(default=None, description="Online-Dauer formatiert (HH:MM:SS)")
