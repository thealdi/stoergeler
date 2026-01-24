from __future__ import annotations

from typing import Dict, Optional
import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import DatabaseContext, DeviceLogRepository, OutageRepository, StatusRepository
from .device_log_sync import DeviceLogSync
from .schemas import (
    ConnectivityStatus,
    DeviceLogEntry,
    DeviceLogResponse,
    OutageListResponse,
    OutageWindow,
    StatusResponse,
)
from .outage_calculator import OutageCalculator
from .outage_config import OutageKeywords
from .fritzbox_client import FritzBoxCredentials, FritzboxClient
from .tracker import ConnectionTracker

app = FastAPI(title="StoerGeler Backend", root_path="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db_context = DatabaseContext(settings.database_path)
db_context.init_schema()
status_repository = StatusRepository(db_context)
device_log_repository = DeviceLogRepository(db_context)
outage_repository = OutageRepository(db_context)
outage_calculator = OutageCalculator(
    cfg=OutageKeywords(
        planned_keywords=settings.outage_planned_keywords,
        ipv4_disconnect_keywords=settings.outage_ipv4_disconnect_keywords,
        ipv4_connect_keywords=settings.outage_ipv4_connect_keywords,
        ipv6_disconnect_keywords=settings.outage_ipv6_disconnect_keywords,
        ipv6_connect_keywords=settings.outage_ipv6_connect_keywords,
    )
)

fritzbox_client = FritzboxClient(
    FritzBoxCredentials(
        address=settings.fritzbox_address,
        username=settings.fritzbox_username,
        password=settings.fritzbox_password,
    )
)
device_log_sync = DeviceLogSync(
    fritzbox_client=fritzbox_client,
    device_log_repository=device_log_repository,
    outage_repository=outage_repository,
    outage_calculator=outage_calculator,
)
tracker = ConnectionTracker(
    status_repository=status_repository,
    fritzbox_client=fritzbox_client,
    device_log_sync=device_log_sync,
    poll_interval_seconds=settings.poll_interval_seconds,
    device_log_poll_interval_seconds=settings.device_log_poll_interval_seconds,
)


@app.on_event("startup")
async def _startup() -> None:
    await tracker.start()


@app.on_event("shutdown")
async def _shutdown() -> None:
    await tracker.stop()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/status", response_model=StatusResponse)
def current_status() -> StatusResponse:
    try:
        result = tracker.poll_now()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return StatusResponse(**result)


@app.get("/device-log", response_model=DeviceLogResponse)
def device_log(
    limit: Optional[int] = Query(
        default=None,
        ge=1,
        le=500,
        description="Optional: Anzahl der Logzeilen beschränken (1-500)",
    )
) -> DeviceLogResponse:
    try:
        records = device_log_repository.list_entries(limit=limit, ascending=False)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return DeviceLogResponse(
        entries=[
            DeviceLogEntry(
                timestamp=record.timestamp,
                message=record.message,
                raw=record.raw or record.message,
            )
            for record in records
        ]
    )


@app.get("/outages", response_model=OutageListResponse)
def outage_windows(
    limit: Optional[int] = Query(
        default=300,
        ge=1,
        le=1000,
        description="Optional: Anzahl der Logzeilen, die ausgewertet werden sollen",
    ),
) -> OutageListResponse:
    try:
        stored_outages = outage_repository.list_outages()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    windows = [
        OutageWindow(
            start=record.start_time,
            end=record.end_time,
            duration_seconds=record.duration_seconds,
            status=record.status,
        )
        for record in stored_outages
    ]
    return OutageListResponse(outages=windows)


@app.get("/connection-check", response_model=ConnectivityStatus)
def connection_check() -> ConnectivityStatus:
    try:
        status = tracker.check_connection()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ConnectivityStatus(**status)


@app.get("/version")
def version() -> Dict[str, str]:
    return {
        "version": os.getenv("APP_VERSION", "dev"),
        "commit": os.getenv("GIT_SHA", "unknown"),
    }


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
