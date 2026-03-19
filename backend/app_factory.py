from __future__ import annotations

import logging
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fritzconnection.core.exceptions import FritzConnectionException
from starlette.status import HTTP_201_CREATED

from .database import (
    DatabaseContext,
    DeviceLogRepository,
    MetadataRepository,
    OutageRepository,
    StatusRepository,
)
from .device_log_sync import DeviceLogSync
from .email_service import EmailService
from .fritzbox_client import FritzBoxCredentials, FritzboxClient
from .outage_calculator import OutageCalculator
from .outage_config import OutageKeywords
from .report_scheduler import ReportScheduler
from .reporting import ReportingService, get_current_week_range, get_last_week_range
from .schemas import (
    ConnectivityStatus,
    DeviceLogEntry,
    DeviceLogResponse,
    OutageCreate,
    OutageCreateResponse,
    OutageListResponse,
    OutageWindow,
    StatusResponse,
)
from .tracker import ConnectionTracker

logger = logging.getLogger(__name__)


@dataclass
class Dependencies:
    """Container for all wired-up dependencies needed by the API."""

    tracker: ConnectionTracker
    device_log_repository: DeviceLogRepository
    outage_repository: OutageRepository
    reporting_service: ReportingService
    email_service: EmailService
    report_scheduler: ReportScheduler


def _build_default_dependencies(settings: Any) -> Dependencies:
    """Wire up real dependencies from application settings."""
    db_context = DatabaseContext(settings.database_path)
    db_context.init_schema()
    status_repository = StatusRepository(db_context)
    device_log_repository = DeviceLogRepository(db_context)
    outage_repository = OutageRepository(db_context)
    metadata_repository = MetadataRepository(db_context)

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

    reporting_service = ReportingService(
        outage_repository=outage_repository,
        device_log_repository=device_log_repository,
    )
    email_service = EmailService(settings)
    report_scheduler = ReportScheduler(
        settings=settings,
        metadata_repository=metadata_repository,
        reporting_service=reporting_service,
        email_service=email_service,
    )

    return Dependencies(
        tracker=tracker,
        device_log_repository=device_log_repository,
        outage_repository=outage_repository,
        reporting_service=reporting_service,
        email_service=email_service,
        report_scheduler=report_scheduler,
    )


def create_app(deps: Optional[Dependencies] = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Pass *deps* to override the default dependency wiring (useful for tests).
    When *deps* is ``None``, real dependencies are built from ``settings``.
    """
    if deps is None:
        from .config import settings

        deps = _build_default_dependencies(settings)

    app = FastAPI(title="StoerGeler Backend", root_path="/api")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store deps on app.state so lifecycle handlers can access them
    app.state.deps = deps

    @app.on_event("startup")
    async def _startup() -> None:
        logger.info("StoerGeler backend starting up")
        await deps.tracker.start()
        await deps.report_scheduler.start()
        logger.info("StoerGeler backend started")

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        logger.info("StoerGeler backend shutting down")
        await deps.tracker.stop()
        await deps.report_scheduler.stop()

    # ---- Routes ----

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.get("/status", response_model=StatusResponse)
    def current_status() -> StatusResponse:
        try:
            result = deps.tracker.poll_now()
        except (FritzConnectionException, ConnectionError, OSError, sqlite3.Error) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return StatusResponse(**result)

    @app.get("/device-log", response_model=DeviceLogResponse)
    def device_log(
        limit: Optional[int] = Query(
            default=None,
            ge=1,
            le=500,
            description="Optional: Anzahl der Logzeilen beschränken (1-500)",
        ),
        start: Optional[datetime] = Query(
            default=None,
            description="Nur Einträge ab diesem Zeitpunkt (ISO-8601)",
        ),
        end: Optional[datetime] = Query(
            default=None,
            description="Nur Einträge bis zu diesem Zeitpunkt (ISO-8601)",
        ),
    ) -> DeviceLogResponse:
        # DB stores naive (no-tz) timestamps — strip tzinfo to match
        naive_start = start.replace(tzinfo=None) if start else None
        naive_end = end.replace(tzinfo=None) if end else None
        try:
            records = deps.device_log_repository.list_entries(
                limit=limit, ascending=False, start=naive_start, end=naive_end,
            )
        except sqlite3.Error as exc:
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
    def outage_windows() -> OutageListResponse:
        try:
            stored_outages = deps.outage_repository.list_outages()
        except sqlite3.Error as exc:
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

    @app.post("/outages", response_model=OutageCreateResponse, status_code=HTTP_201_CREATED)
    def create_outage(body: OutageCreate) -> OutageCreateResponse:
        try:
            outage_id = deps.outage_repository.create_outage(
                start_time=body.start,
                end_time=body.end,
                status=body.status,
            )
        except sqlite3.Error as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        duration = None
        if body.end:
            duration = max(1, int((body.end - body.start).total_seconds()))

        return OutageCreateResponse(
            id=outage_id,
            outage=OutageWindow(
                start=body.start,
                end=body.end,
                duration_seconds=duration,
                status=body.status,
            ),
        )

    @app.get("/connection-check", response_model=ConnectivityStatus)
    def connection_check() -> ConnectivityStatus:
        try:
            status = deps.tracker.check_connection()
        except (FritzConnectionException, ConnectionError, OSError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return ConnectivityStatus(**status)

    @app.get("/report/weekly", response_class=HTMLResponse)
    def get_weekly_report(
        scope: str = Query(default="last", enum=["last", "current"], description="Woche auswählen")
    ) -> HTMLResponse:
        """Gibt den Wochen-Report als HTML zurück."""
        try:
            start, end = get_last_week_range() if scope == "last" else get_current_week_range()
            data = deps.reporting_service.get_report_data(start, end)
            html = deps.reporting_service.render_weekly_report(data)
            return HTMLResponse(content=html)
        except (sqlite3.Error, OSError) as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/report/send-test-email")
    async def send_test_report_email() -> Dict[str, str]:
        """Sendet einen Test-Report per E-Mail."""
        try:
            start, end = get_last_week_range()
            data = deps.reporting_service.get_report_data(start, end)
            html = deps.reporting_service.render_weekly_report(data)
            subject = f"StoerGeler Test-Report (KW {data['week_number']})"
            await deps.email_service.send_report(subject, html)
            return {"status": "sent"}
        except (sqlite3.Error, OSError) as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/version")
    def version() -> Dict[str, str]:
        return {
            "version": os.getenv("APP_VERSION", "dev"),
            "commit": os.getenv("GIT_SHA", "unknown"),
        }

    return app
