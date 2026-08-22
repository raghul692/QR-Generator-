"""
QRMaster Pro — API Package.

Exposes all API routers for inclusion in the FastAPI application.
"""
from __future__ import annotations

from app.api.api_key_router import router as api_key_router
from app.api.backup_router import router as backup_router
from app.api.bulk_router import router as bulk_router
from app.api.category_router import router as category_router
from app.api.dashboard_router import router as dashboard_router
from app.api.dynamic_router import router as dynamic_router
from app.api.export_router import router as export_router
from app.api.history_router import router as history_router
from app.api.qr_router import router as qr_router
from app.api.scanner_router import router as scanner_router
from app.api.settings_router import router as settings_router

all_routers = [
    qr_router,
    history_router,
    category_router,
    scanner_router,
    dashboard_router,
    bulk_router,
    export_router,
    backup_router,
    settings_router,
    dynamic_router,
    api_key_router,
]

__all__ = ["all_routers"]