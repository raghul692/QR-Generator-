"""
QRMaster Pro — Health & Liveness/Readiness API Endpoints.

Provides health checks for Render, load balancers, and container orchestrators.
GET /health       - Root service health
GET /health/live  - Liveness probe (process is running)
GET /health/ready - Readiness probe (database is reachable)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Response, status

from app.config import settings
from app.database.session import check_db_connection

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=Dict[str, Any], summary="Service Health")
def health_check():
    """Basic health check indicating process is responding."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@router.get("/health/live", response_model=Dict[str, Any], summary="Liveness Probe")
def liveness_probe():
    """Liveness probe: verifies web server process is alive."""
    return {
        "status": "live",
        "app": settings.APP_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/ready", response_model=Dict[str, Any], summary="Readiness Probe")
def readiness_probe(response: Response):
    """
    Readiness probe: verifies database connectivity without leaking credentials.
    Returns 200 OK if database is healthy, 503 Service Unavailable otherwise.
    """
    is_db_ready = check_db_connection()
    if not is_db_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not_ready",
            "database": "unreachable",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return {
        "status": "ready",
        "database": "connected",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
