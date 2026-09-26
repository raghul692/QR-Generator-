"""
QRMaster Pro — Dynamic QR Service.

Manages Dynamic QR codes, short code generation, target URL updates,
password protection, expiration checks, and scan tracking analytics.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional
from user_agents import parse

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import DynamicQR, QRHistory, ScanLog
from app.utils.logger import logger


class DynamicQRService:
    """Service for handling Dynamic QR codes and Scan Analytics."""

    def generate_short_code(self, db: Session, length: int = 6) -> str:
        """Generate a unique URL-safe short code."""
        for _ in range(10):
            code = secrets.token_urlsafe(length)[:length].replace("-", "a").replace("_", "b")
            existing = db.query(DynamicQR).filter(DynamicQR.short_code == code).first()
            if not existing:
                return code
        return secrets.token_hex(4)

    def create_dynamic_qr(
        self,
        db: Session,
        title: str,
        target_url: str,
        qr_history_id: Optional[int] = None,
        password: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        ios_target_url: Optional[str] = None,
        android_target_url: Optional[str] = None,
    ) -> DynamicQR:
        """Create a new Dynamic QR record."""
        short_code = self.generate_short_code(db)
        password_hash = (
            hashlib.sha256(password.encode("utf-8")).hexdigest() if password else None
        )

        dyn_qr = DynamicQR(
            short_code=short_code,
            target_url=target_url,
            title=title,
            qr_history_id=qr_history_id,
            password_hash=password_hash,
            expires_at=expires_at,
            is_active=True,
            scan_count=0,
            ios_target_url=ios_target_url,
            android_target_url=android_target_url,
        )
        db.add(dyn_qr)
        db.commit()
        db.refresh(dyn_qr)
        logger.info(f"Created Dynamic QR code '{short_code}' for target '{target_url}'")
        return dyn_qr

    def get_by_code(self, db: Session, short_code: str) -> Optional[DynamicQR]:
        """Fetch Dynamic QR by short code."""
        return db.query(DynamicQR).filter(DynamicQR.short_code == short_code).first()

    def update_dynamic_qr(
        self,
        db: Session,
        dynamic_id: int,
        target_url: Optional[str] = None,
        title: Optional[str] = None,
        is_active: Optional[bool] = None,
        password: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        ios_target_url: Optional[str] = None,
        android_target_url: Optional[str] = None,
    ) -> DynamicQR:
        """Update Dynamic QR code attributes (e.g. target URL after print)."""
        dyn = db.query(DynamicQR).filter(DynamicQR.id == dynamic_id).first()
        if not dyn:
            raise ValueError(f"Dynamic QR with ID {dynamic_id} not found")

        if target_url is not None:
            dyn.target_url = target_url
        if title is not None:
            dyn.title = title
        if is_active is not None:
            dyn.is_active = is_active
        if password is not None:
            dyn.password_hash = (
                hashlib.sha256(password.encode("utf-8")).hexdigest() if password else None
            )
        if expires_at is not None:
            dyn.expires_at = expires_at
        if ios_target_url is not None:
            dyn.ios_target_url = ios_target_url
        if android_target_url is not None:
            dyn.android_target_url = android_target_url

        db.commit()
        db.refresh(dyn)
        logger.info(f"Updated Dynamic QR ID {dynamic_id} target to '{dyn.target_url}'")
        return dyn

    def verify_password(self, dyn: DynamicQR, password: str) -> bool:
        """Verify entered password against stored hash."""
        if not dyn.password_hash:
            return True
        check_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return check_hash == dyn.password_hash

    def is_expired(self, dyn: DynamicQR) -> bool:
        """Check if Dynamic QR is expired."""
        if not dyn.expires_at:
            return False
        return datetime.now() > dyn.expires_at

    def log_scan(
        self,
        db: Session,
        dynamic_qr: DynamicQR,
        ip_address: Optional[str] = None,
        user_agent_str: Optional[str] = None,
        referer: Optional[str] = None,
    ) -> ScanLog:
        """Log a real-time scan event and increment counters."""
        device_type = "Desktop"
        browser = "Unknown"

        if user_agent_str:
            try:
                ua = parse(user_agent_str)
                if ua.is_mobile:
                    device_type = "Mobile"
                elif ua.is_tablet:
                    device_type = "Tablet"
                elif ua.is_pc:
                    device_type = "Desktop"

                browser = ua.browser.family
            except Exception:
                pass

        scan = ScanLog(
            dynamic_qr_id=dynamic_qr.id,
            ip_address=ip_address,
            user_agent=user_agent_str,
            device_type=device_type,
            browser=browser,
            referer=referer,
        )
        db.add(scan)

        # Increment counters
        dynamic_qr.scan_count += 1
        if dynamic_qr.qr_history_id:
            history = db.query(QRHistory).filter(QRHistory.id == dynamic_qr.qr_history_id).first()
            if history:
                history.download_count += 1

        db.commit()
        db.refresh(scan)
        return scan

    def get_analytics(self, db: Session, dynamic_id: int) -> Dict[str, Any]:
        """Return analytics breakdown for a dynamic QR code."""
        dyn = db.query(DynamicQR).filter(DynamicQR.id == dynamic_id).first()
        if not dyn:
            raise ValueError(f"Dynamic QR with ID {dynamic_id} not found")

        total_scans = dyn.scan_count

        # Device breakdown
        device_counts = (
            db.query(ScanLog.device_type, func.count(ScanLog.id))
            .filter(ScanLog.dynamic_qr_id == dynamic_id)
            .group_by(ScanLog.device_type)
            .all()
        )

        # Browser breakdown
        browser_counts = (
            db.query(ScanLog.browser, func.count(ScanLog.id))
            .filter(ScanLog.dynamic_qr_id == dynamic_id)
            .group_by(ScanLog.browser)
            .all()
        )

        return {
            "id": dyn.id,
            "short_code": dyn.short_code,
            "title": dyn.title,
            "target_url": dyn.target_url,
            "total_scans": total_scans,
            "is_active": dyn.is_active,
            "is_expired": self.is_expired(dyn),
            "has_password": bool(dyn.password_hash),
            "expires_at": dyn.expires_at.isoformat() if dyn.expires_at else None,
            "devices": [{"device": d or "Unknown", "count": c} for d, c in device_counts],
            "browsers": [{"browser": b or "Unknown", "count": c} for b, c in browser_counts],
        }


# Singleton
dynamic_qr_service = DynamicQRService()
