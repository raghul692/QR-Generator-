"""
QRMaster Pro — Data Retention & GDPR Erasure Service.

Implements automated 90-day scan log retention, IP anonymization,
and GDPR Article 17 ("Right to Erasure") workspace data cleanup.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    DynamicQR,
    LandingPage,
    DigitalMenu,
    QRBulkJob,
    QRCategory,
    QRExport,
    QRHistory,
    QRTemplate,
    ScanLog,
    Workspace,
    WorkspaceMember,
)
from app.utils.logger import logger


class CleanupService:
    """Enterprise Data Retention and GDPR Compliance Service."""

    @staticmethod
    def purge_expired_scan_logs(db: Session, retention_days: int = 90) -> Dict[str, Any]:
        """
        Delete ScanLog records older than `retention_days` days.
        Default retention period: 90 days.
        """
        start_time = time.perf_counter()
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        try:
            deleted_count = (
                db.query(ScanLog)
                .filter(ScanLog.scanned_at < cutoff_date)
                .delete(synchronize_session=False)
            )
            db.commit()
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info(
                f"[RETENTION] Purged {deleted_count} scan logs older than {retention_days} days (cutoff: {cutoff_date}) in {elapsed_ms}ms"
            )
            return {
                "status": "success",
                "retention_days": retention_days,
                "cutoff_date": cutoff_date.isoformat(),
                "deleted_count": deleted_count,
                "elapsed_ms": elapsed_ms,
            }
        except Exception as exc:
            db.rollback()
            logger.error(f"[RETENTION ERROR] Failed to purge scan logs: {exc}")
            raise

    @staticmethod
    def anonymize_stale_ips(db: Session, older_than_days: int = 30) -> int:
        """
        Anonymize or zero out IP addresses in ScanLog older than `older_than_days`
        to conform with GDPR storage limitation requirements.
        """
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        try:
            updated_count = (
                db.query(ScanLog)
                .filter(ScanLog.scanned_at < cutoff_date, ScanLog.ip_address != "0.0.0.0")
                .update({"ip_address": "0.0.0.0"}, synchronize_session=False)
            )
            db.commit()
            logger.info(f"[GDPR] Anonymized IP addresses for {updated_count} scan logs older than {older_than_days} days")
            return updated_count
        except Exception as exc:
            db.rollback()
            logger.error(f"[GDPR ERROR] Failed to anonymize IPs: {exc}")
            raise

    @staticmethod
    def purge_workspace_data(db: Session, workspace_id: str) -> Dict[str, Any]:
        """
        Execute full erasure for a specific tenant workspace (GDPR Right to be Forgotten).
        Cascades deletions across all tenant-scoped resources.
        """
        start_time = time.perf_counter()
        if workspace_id == "ws_legacy_default":
            raise ValueError("Cannot purge legacy default workspace")

        try:
            # 1. Fetch dynamic QR IDs to delete scan logs
            dyn_ids = [
                d.id for d in db.query(DynamicQR.id).filter(DynamicQR.workspace_id == workspace_id).all()
            ]
            scans_deleted = 0
            if dyn_ids:
                scans_deleted = (
                    db.query(ScanLog)
                    .filter(ScanLog.dynamic_qr_id.in_(dyn_ids))
                    .delete(synchronize_session=False)
                )

            # 2. Delete tenant tables
            dyn_deleted = (
                db.query(DynamicQR)
                .filter(DynamicQR.workspace_id == workspace_id)
                .delete(synchronize_session=False)
            )
            history_deleted = (
                db.query(QRHistory)
                .filter(QRHistory.workspace_id == workspace_id)
                .delete(synchronize_session=False)
            )
            pages_deleted = (
                db.query(LandingPage)
                .filter(LandingPage.workspace_id == workspace_id)
                .delete(synchronize_session=False)
            )
            menus_deleted = (
                db.query(DigitalMenu)
                .filter(DigitalMenu.workspace_id == workspace_id)
                .delete(synchronize_session=False)
            )
            jobs_deleted = (
                db.query(QRBulkJob)
                .filter(QRBulkJob.workspace_id == workspace_id)
                .delete(synchronize_session=False)
            )
            templates_deleted = (
                db.query(QRTemplate)
                .filter(QRTemplate.workspace_id == workspace_id)
                .delete(synchronize_session=False)
            )
            categories_deleted = (
                db.query(QRCategory)
                .filter(QRCategory.workspace_id == workspace_id)
                .delete(synchronize_session=False)
            )

            # 3. Delete members and workspace
            members_deleted = (
                db.query(WorkspaceMember)
                .filter(WorkspaceMember.workspace_id == workspace_id)
                .delete(synchronize_session=False)
            )
            ws_deleted = (
                db.query(Workspace)
                .filter(Workspace.id == workspace_id)
                .delete(synchronize_session=False)
            )

            db.commit()
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info(f"[GDPR PURGE] Fully purged workspace {workspace_id} in {elapsed_ms}ms")

            return {
                "status": "success",
                "workspace_id": workspace_id,
                "elapsed_ms": elapsed_ms,
                "deleted": {
                    "scan_logs": scans_deleted,
                    "dynamic_qrs": dyn_deleted,
                    "history_items": history_deleted,
                    "landing_pages": pages_deleted,
                    "digital_menus": menus_deleted,
                    "bulk_jobs": jobs_deleted,
                    "templates": templates_deleted,
                    "categories": categories_deleted,
                    "members": members_deleted,
                    "workspaces": ws_deleted,
                },
            }
        except Exception as exc:
            db.rollback()
            logger.error(f"[GDPR PURGE ERROR] Failed to purge workspace {workspace_id}: {exc}")
            raise

    @staticmethod
    def get_retention_summary(db: Session) -> Dict[str, Any]:
        """Return diagnostic metrics on scan log counts, oldest records, and retention status."""
        total_scans = db.query(func.count(ScanLog.id)).scalar() or 0
        oldest_scan = db.query(func.min(ScanLog.scanned_at)).scalar()
        newest_scan = db.query(func.max(ScanLog.scanned_at)).scalar()

        # Count scans older than 90 days
        cutoff_90 = datetime.now() - timedelta(days=90)
        expired_count = (
            db.query(func.count(ScanLog.id)).filter(ScanLog.scanned_at < cutoff_90).scalar() or 0
        )

        return {
            "total_scan_logs": total_scans,
            "expired_scan_logs_90d": expired_count,
            "oldest_scan_at": oldest_scan.isoformat() if oldest_scan else None,
            "newest_scan_at": newest_scan.isoformat() if newest_scan else None,
            "default_retention_days": 90,
            "gdpr_ip_anonymization_days": 30,
        }


cleanup_service = CleanupService()
