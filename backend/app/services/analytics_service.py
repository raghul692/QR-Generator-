"""
QRMaster Pro — Analytics & Dashboard Service.

Computes dashboard statistics, chart distributions, and scan analytics from
the QR history, dynamic QR, scan logs, categories, and export tables,
with complete multi-tenant workspace isolation.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func, distinct, or_
from sqlalchemy.orm import Session

from app.models import (
    ActivityLog,
    QRCategory,
    QRBulkJob,
    QRExport,
    QRHistory,
    DynamicQR,
    ScanLog,
)


class AnalyticsService:
    """Service for dashboard stats and platform analytics with tenant isolation."""

    def _qr_filter(self, workspace_id: Optional[str]):
        if not workspace_id or workspace_id == "ws_legacy_default":
            return or_(QRHistory.workspace_id == "ws_legacy_default", QRHistory.workspace_id.is_(None))
        return QRHistory.workspace_id == workspace_id

    def _dyn_filter(self, workspace_id: Optional[str]):
        if not workspace_id or workspace_id == "ws_legacy_default":
            return or_(DynamicQR.workspace_id == "ws_legacy_default", DynamicQR.workspace_id.is_(None))
        return DynamicQR.workspace_id == workspace_id

    def _bulk_filter(self, workspace_id: Optional[str]):
        if not workspace_id or workspace_id == "ws_legacy_default":
            return or_(QRBulkJob.workspace_id == "ws_legacy_default", QRBulkJob.workspace_id.is_(None))
        return QRBulkJob.workspace_id == workspace_id

    # ------------------------------------------------------------------ #
    #  Dashboard stats
    # ------------------------------------------------------------------ #
    def get_dashboard_stats(self, db: Session, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        today_start = datetime.combine(date.today(), datetime.min.time())
        q_filter = self._qr_filter(workspace_id)
        d_filter = self._dyn_filter(workspace_id)
        b_filter = self._bulk_filter(workspace_id)

        total_qr = db.query(func.count(QRHistory.id)).filter(q_filter).scalar() or 0
        today_qr = (
            db.query(func.count(QRHistory.id))
            .filter(q_filter, QRHistory.created_at >= today_start)
            .scalar() or 0
        )
        total_downloads = (
            db.query(func.sum(QRHistory.download_count))
            .filter(q_filter)
            .scalar() or 0
        )
        total_categories = db.query(func.count(QRCategory.id)).scalar() or 0
        total_bulk_jobs = db.query(func.count(QRBulkJob.id)).filter(b_filter).scalar() or 0
        favorites = (
            db.query(func.count(QRHistory.id))
            .filter(q_filter, QRHistory.is_favorite == True)  # noqa: E712
            .scalar() or 0
        )

        # Dynamic QR & scan metrics
        total_dynamic = db.query(func.count(DynamicQR.id)).filter(d_filter).scalar() or 0
        now = datetime.now()
        active_dynamic = (
            db.query(func.count(DynamicQR.id))
            .filter(
                d_filter,
                DynamicQR.is_active == True,  # noqa: E712
                or_(DynamicQR.expires_at.is_(None), DynamicQR.expires_at > now),
            )
            .scalar() or 0
        )
        expired_dynamic = (
            db.query(func.count(DynamicQR.id))
            .filter(
                d_filter,
                or_(
                    DynamicQR.is_active == False,  # noqa: E712
                    (DynamicQR.expires_at.is_not(None)) & (DynamicQR.expires_at <= now),
                ),
            )
            .scalar() or 0
        )

        # Scans linked to workspace dynamic QRs
        scan_query = db.query(func.count(ScanLog.id)).join(DynamicQR, ScanLog.dynamic_qr_id == DynamicQR.id).filter(d_filter)
        total_scans = scan_query.scalar() or 0

        today_scans = (
            db.query(func.count(ScanLog.id))
            .join(DynamicQR, ScanLog.dynamic_qr_id == DynamicQR.id)
            .filter(d_filter, ScanLog.scanned_at >= today_start)
            .scalar() or 0
        )
        unique_scans = (
            db.query(func.count(distinct(ScanLog.ip_address)))
            .join(DynamicQR, ScanLog.dynamic_qr_id == DynamicQR.id)
            .filter(d_filter, ScanLog.ip_address.is_not(None))
            .scalar() or 0
        )
        failed_password_attempts = (
            db.query(func.count(ActivityLog.id))
            .filter(ActivityLog.action == "failed_password_attempt")
            .scalar() or 0
        )

        return {
            "total_qr": total_qr,
            "today_qr": today_qr,
            "total_downloads": int(total_downloads),
            "total_categories": total_categories,
            "total_bulk_jobs": total_bulk_jobs,
            "favorites": favorites,
            "total_dynamic_qr": total_dynamic,
            "active_dynamic_qr": active_dynamic,
            "expired_dynamic_qr": expired_dynamic,
            "total_scans": total_scans,
            "today_scans": today_scans,
            "unique_scans": unique_scans,
            "failed_password_attempts": failed_password_attempts,
        }

    # ------------------------------------------------------------------ #
    #  Dashboard charts
    # ------------------------------------------------------------------ #
    def get_dashboard_charts(self, db: Session, workspace_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "qr_type_distribution": self._qr_type_distribution(db, workspace_id),
            "daily_generation": self._daily_generation(db, days=7, workspace_id=workspace_id),
            "category_distribution": self._category_distribution(db, workspace_id),
            "download_trends": self._download_trends(db, days=7),
            "scan_trends": self._scan_trends(db, days=7, workspace_id=workspace_id),
            "device_distribution": self._device_distribution(db, workspace_id),
            "browser_distribution": self._browser_distribution(db, workspace_id),
            "os_distribution": self._os_distribution(db, workspace_id),
        }

    def _qr_type_distribution(self, db: Session, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = (
            db.query(QRHistory.qr_type, func.count(QRHistory.id))
            .filter(self._qr_filter(workspace_id))
            .group_by(QRHistory.qr_type)
            .order_by(func.count(QRHistory.id).desc())
            .limit(10)
            .all()
        )
        return [{"label": r[0], "value": r[1]} for r in rows]

    def _daily_generation(self, db: Session, days: int = 7, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        start = datetime.combine(date.today() - timedelta(days=days - 1), datetime.min.time())
        rows = (
            db.query(
                func.date(QRHistory.created_at).label("d"),
                func.count(QRHistory.id).label("c"),
            )
            .filter(self._qr_filter(workspace_id), QRHistory.created_at >= start)
            .group_by("d")
            .order_by("d")
            .all()
        )
        result = []
        date_map = {str(r[0]): r[1] for r in rows}
        for i in range(days):
            d = (date.today() - timedelta(days=days - 1 - i)).isoformat()
            result.append({"label": d, "value": date_map.get(d, 0)})
        return result

    def _category_distribution(self, db: Session, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = (
            db.query(QRCategory.name, func.count(QRHistory.id))
            .join(QRHistory, QRHistory.category_id == QRCategory.id, isouter=True)
            .filter(self._qr_filter(workspace_id))
            .group_by(QRCategory.id, QRCategory.name)
            .all()
        )
        return [{"label": r[0], "value": r[1]} for r in rows]

    def _download_trends(self, db: Session, days: int = 7) -> List[Dict[str, Any]]:
        start = datetime.combine(date.today() - timedelta(days=days - 1), datetime.min.time())
        rows = (
            db.query(
                func.date(QRExport.created_at).label("d"),
                func.count(QRExport.id).label("c"),
            )
            .filter(QRExport.created_at >= start)
            .group_by("d")
            .order_by("d")
            .all()
        )
        date_map = {str(r[0]): r[1] for r in rows}
        result = []
        for i in range(days):
            d = (date.today() - timedelta(days=days - 1 - i)).isoformat()
            result.append({"label": d, "value": date_map.get(d, 0)})
        return result

    def _scan_trends(self, db: Session, days: int = 7, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        start = datetime.combine(date.today() - timedelta(days=days - 1), datetime.min.time())
        rows = (
            db.query(
                func.date(ScanLog.scanned_at).label("d"),
                func.count(ScanLog.id).label("c"),
            )
            .join(DynamicQR, ScanLog.dynamic_qr_id == DynamicQR.id)
            .filter(self._dyn_filter(workspace_id), ScanLog.scanned_at >= start)
            .group_by("d")
            .order_by("d")
            .all()
        )
        date_map = {str(r[0]): r[1] for r in rows}
        result = []
        for i in range(days):
            d = (date.today() - timedelta(days=days - 1 - i)).isoformat()
            result.append({"label": d, "value": date_map.get(d, 0)})
        return result

    def _device_distribution(self, db: Session, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = (
            db.query(ScanLog.device_type, func.count(ScanLog.id))
            .join(DynamicQR, ScanLog.dynamic_qr_id == DynamicQR.id)
            .filter(self._dyn_filter(workspace_id))
            .group_by(ScanLog.device_type)
            .all()
        )
        return [{"label": r[0] or "Unknown", "value": r[1]} for r in rows]

    def _browser_distribution(self, db: Session, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = (
            db.query(ScanLog.browser)
            .join(DynamicQR, ScanLog.dynamic_qr_id == DynamicQR.id)
            .filter(self._dyn_filter(workspace_id), ScanLog.browser.is_not(None))
            .all()
        )
        counts: Dict[str, int] = {}
        for (raw,) in rows:
            if not raw:
                continue
            family = raw.split(" (")[0].strip() or "Unknown"
            counts[family] = counts.get(family, 0) + 1
        return [{"label": k, "value": v} for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:8]]

    def _os_distribution(self, db: Session, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = (
            db.query(ScanLog.browser)
            .join(DynamicQR, ScanLog.dynamic_qr_id == DynamicQR.id)
            .filter(self._dyn_filter(workspace_id), ScanLog.browser.is_not(None))
            .all()
        )
        counts: Dict[str, int] = {}
        for (raw,) in rows:
            if not raw:
                continue
            if " (" in raw and raw.endswith(")"):
                os_family = raw.split(" (", 1)[1].rstrip(")").strip() or "Unknown"
            else:
                os_family = "Unknown"
            counts[os_family] = counts.get(os_family, 0) + 1
        return [{"label": k, "value": v} for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:8]]

    # ------------------------------------------------------------------ #
    #  Full analytics
    # ------------------------------------------------------------------ #
    def get_analytics(self, db: Session, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        q_filter = self._qr_filter(workspace_id)
        d_filter = self._dyn_filter(workspace_id)

        most_type_row = (
            db.query(QRHistory.qr_type, func.count(QRHistory.id))
            .filter(q_filter)
            .group_by(QRHistory.qr_type)
            .order_by(func.count(QRHistory.id).desc())
            .first()
        )
        most_generated_type = (
            {"type": most_type_row[0], "count": most_type_row[1]} if most_type_row else None
        )

        most_dl_row = (
            db.query(QRHistory.id, QRHistory.title, QRHistory.download_count)
            .filter(q_filter)
            .order_by(QRHistory.download_count.desc())
            .first()
        )
        most_downloaded = (
            {"id": most_dl_row[0], "title": most_dl_row[1], "downloads": most_dl_row[2]}
            if most_dl_row and most_dl_row[2] > 0
            else None
        )

        # Top dynamic QR codes by scan
        top_scanned_rows = (
            db.query(DynamicQR.id, DynamicQR.title, DynamicQR.short_code, DynamicQR.scan_count)
            .filter(d_filter)
            .order_by(DynamicQR.scan_count.desc())
            .limit(5)
            .all()
        )
        top_scanned = [
            {"id": r[0], "title": r[1], "short_code": r[2], "scans": r[3]}
            for r in top_scanned_rows if r[3] > 0
        ]

        unique_scans = (
            db.query(func.count(distinct(ScanLog.ip_address)))
            .join(DynamicQR, ScanLog.dynamic_qr_id == DynamicQR.id)
            .filter(d_filter, ScanLog.ip_address.is_not(None))
            .scalar() or 0
        )
        failed_password_attempts = (
            db.query(func.count(ActivityLog.id))
            .filter(ActivityLog.action == "failed_password_attempt")
            .scalar() or 0
        )

        return {
            "most_generated_type": most_generated_type,
            "most_downloaded": most_downloaded,
            "top_scanned_qrs": top_scanned,
            "unique_scans": unique_scans,
            "failed_password_attempts": failed_password_attempts,
            "category_usage": self._category_distribution(db, workspace_id),
            "daily_activity": self._daily_generation(db, days=7, workspace_id=workspace_id),
            "weekly_activity": self._daily_generation(db, days=14, workspace_id=workspace_id),
            "monthly_activity": self._daily_generation(db, days=30, workspace_id=workspace_id),
            "scan_trends_7d": self._scan_trends(db, days=7, workspace_id=workspace_id),
            "scan_trends_30d": self._scan_trends(db, days=30, workspace_id=workspace_id),
            "device_stats": self._device_distribution(db, workspace_id),
            "browser_stats": self._browser_distribution(db, workspace_id),
            "os_stats": self._os_distribution(db, workspace_id),
            "export_stats": self._export_stats(db),
        }

    def _export_stats(self, db: Session) -> List[Dict[str, Any]]:
        rows = (
            db.query(QRExport.format, func.count(QRExport.id))
            .group_by(QRExport.format)
            .all()
        )
        return [{"label": r[0], "value": r[1]} for r in rows]


# Singleton
analytics_service = AnalyticsService()
