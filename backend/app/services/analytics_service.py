"""
QRMaster Pro — Analytics & Dashboard Service.

Computes dashboard statistics, chart distributions, and scan analytics from
the QR history, dynamic QR, scan logs, categories, and export tables.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func, distinct, or_
from sqlalchemy.orm import Session

from app.models import (
    QRCategory,
    QRBulkJob,
    QRExport,
    QRHistory,
    DynamicQR,
    ScanLog,
)


class AnalyticsService:
    """Service for dashboard stats and platform analytics."""

    # ------------------------------------------------------------------ #
    #  Dashboard stats
    # ------------------------------------------------------------------ #
    def get_dashboard_stats(self, db: Session) -> Dict[str, Any]:
        today_start = datetime.combine(date.today(), datetime.min.time())

        total_qr = db.query(func.count(QRHistory.id)).scalar() or 0
        today_qr = (
            db.query(func.count(QRHistory.id))
            .filter(QRHistory.created_at >= today_start)
            .scalar() or 0
        )
        total_downloads = db.query(func.sum(QRHistory.download_count)).scalar() or 0
        total_categories = db.query(func.count(QRCategory.id)).scalar() or 0
        total_bulk_jobs = db.query(func.count(QRBulkJob.id)).scalar() or 0
        favorites = (
            db.query(func.count(QRHistory.id))
            .filter(QRHistory.is_favorite == True)  # noqa: E712
            .scalar() or 0
        )

        # Dynamic QR & scan metrics
        total_dynamic = db.query(func.count(DynamicQR.id)).scalar() or 0
        now = datetime.now()
        active_dynamic = (
            db.query(func.count(DynamicQR.id))
            .filter(
                DynamicQR.is_active == True,  # noqa: E712
                or_(DynamicQR.expires_at == None, DynamicQR.expires_at > now),
            )
            .scalar() or 0
        )
        expired_dynamic = (
            db.query(func.count(DynamicQR.id))
            .filter(
                or_(
                    DynamicQR.is_active == False,  # noqa: E712
                    (DynamicQR.expires_at != None) & (DynamicQR.expires_at <= now),
                )
            )
            .scalar() or 0
        )
        total_scans = db.query(func.count(ScanLog.id)).scalar() or 0
        today_scans = (
            db.query(func.count(ScanLog.id))
            .filter(ScanLog.scanned_at >= today_start)
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
        }

    # ------------------------------------------------------------------ #
    #  Dashboard charts
    # ------------------------------------------------------------------ #
    def get_dashboard_charts(self, db: Session) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "qr_type_distribution": self._qr_type_distribution(db),
            "daily_generation": self._daily_generation(db, days=7),
            "category_distribution": self._category_distribution(db),
            "download_trends": self._download_trends(db, days=7),
            "scan_trends": self._scan_trends(db, days=7),
            "device_distribution": self._device_distribution(db),
        }

    def _qr_type_distribution(self, db: Session) -> List[Dict[str, Any]]:
        rows = (
            db.query(QRHistory.qr_type, func.count(QRHistory.id))
            .group_by(QRHistory.qr_type)
            .order_by(func.count(QRHistory.id).desc())
            .limit(10)
            .all()
        )
        return [{"label": r[0], "value": r[1]} for r in rows]

    def _daily_generation(self, db: Session, days: int = 7) -> List[Dict[str, Any]]:
        start = datetime.combine(date.today() - timedelta(days=days - 1), datetime.min.time())
        rows = (
            db.query(
                func.date(QRHistory.created_at).label("d"),
                func.count(QRHistory.id).label("c"),
            )
            .filter(QRHistory.created_at >= start)
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

    def _category_distribution(self, db: Session) -> List[Dict[str, Any]]:
        rows = (
            db.query(QRCategory.name, func.count(QRHistory.id))
            .join(QRHistory, QRHistory.category_id == QRCategory.id, isouter=True)
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

    def _scan_trends(self, db: Session, days: int = 7) -> List[Dict[str, Any]]:
        start = datetime.combine(date.today() - timedelta(days=days - 1), datetime.min.time())
        rows = (
            db.query(
                func.date(ScanLog.scanned_at).label("d"),
                func.count(ScanLog.id).label("c"),
            )
            .filter(ScanLog.scanned_at >= start)
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

    def _device_distribution(self, db: Session) -> List[Dict[str, Any]]:
        rows = (
            db.query(ScanLog.device_type, func.count(ScanLog.id))
            .group_by(ScanLog.device_type)
            .all()
        )
        return [{"label": r[0] or "Unknown", "value": r[1]} for r in rows]

    # ------------------------------------------------------------------ #
    #  Full analytics
    # ------------------------------------------------------------------ #
    def get_analytics(self, db: Session) -> Dict[str, Any]:
        most_type_row = (
            db.query(QRHistory.qr_type, func.count(QRHistory.id))
            .group_by(QRHistory.qr_type)
            .order_by(func.count(QRHistory.id).desc())
            .first()
        )
        most_generated_type = (
            {"type": most_type_row[0], "count": most_type_row[1]} if most_type_row else None
        )

        most_dl_row = (
            db.query(QRHistory.id, QRHistory.title, QRHistory.download_count)
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
            .order_by(DynamicQR.scan_count.desc())
            .limit(5)
            .all()
        )
        top_scanned = [
            {"id": r[0], "title": r[1], "short_code": r[2], "scans": r[3]}
            for r in top_scanned_rows if r[3] > 0
        ]

        return {
            "most_generated_type": most_generated_type,
            "most_downloaded": most_downloaded,
            "top_scanned_qrs": top_scanned,
            "category_usage": self._category_distribution(db),
            "daily_activity": self._daily_generation(db, days=7),
            "weekly_activity": self._daily_generation(db, days=14),
            "monthly_activity": self._daily_generation(db, days=30),
            "scan_trends_7d": self._scan_trends(db, days=7),
            "scan_trends_30d": self._scan_trends(db, days=30),
            "device_stats": self._device_distribution(db),
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
