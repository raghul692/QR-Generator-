"""
QRMaster Pro — Services Package.

Exposes all business-logic service singletons.
"""
from __future__ import annotations

from app.services.analytics_service import analytics_service
from app.services.backup_service import backup_service
from app.services.bulk_service import bulk_service
from app.services.category_service import category_service
from app.services.export_service import export_service
from app.services.history_service import history_service
from app.services.qr_service import qr_service
from app.services.settings_service import settings_service

__all__ = [
    "qr_service",
    "history_service",
    "category_service",
    "analytics_service",
    "settings_service",
    "bulk_service",
    "export_service",
    "backup_service",
]