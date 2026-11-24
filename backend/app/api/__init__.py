"""
QRMaster Pro — API Package.

Exposes all API routers for inclusion in the FastAPI application.
"""
from __future__ import annotations

from app.api.api_key_router import router as api_key_router
from app.api.auth_router import router as auth_router
from app.api.backup_router import router as backup_router
from app.api.bulk_router import router as bulk_router
from app.api.category_router import router as category_router
from app.api.dashboard_router import router as dashboard_router
from app.api.domains_router import router as domains_router
from app.api.dynamic_router import router as dynamic_router
from app.api.export_router import router as export_router
from app.api.history_router import router as history_router
from app.api.landing_page_router import router as landing_page_router
from app.api.menu_router import router as menu_router
from app.api.qr_router import router as qr_router
from app.api.retention_router import router as retention_router
from app.api.scanner_router import router as scanner_router
from app.api.settings_router import router as settings_router
from app.api.template_router import router as template_router
from app.api.vcard_router import router as vcard_router
from app.api.webhook_router import router as webhook_router
from app.api.workspace_router import router as workspace_router

all_routers = [
    auth_router,
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
    template_router,
    landing_page_router,
    menu_router,
    vcard_router,
    workspace_router,
    domains_router,
    retention_router,
    webhook_router,
]

__all__ = ["all_routers"]
