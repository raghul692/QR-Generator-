"""
QRMaster Pro — Dynamic QR Service.

Manages Dynamic QR codes, short code generation, target URL updates,
Argon2id password protection (with SHA-256 upgrade), expiration checks,
and privacy-aware real-time scan telemetry.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from user_agents import parse

from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.config import settings
from app.models import DynamicQR, QRHistory, ScanLog
from app.utils.logger import logger

_password_hasher = PasswordHasher()


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
    ) -> DynamicQR:
        """Create a new Dynamic QR record with Argon2id password hashing."""
        short_code = self.generate_short_code(db)
        password_hash = _password_hasher.hash(password) if password else None

        dyn_qr = DynamicQR(
            short_code=short_code,
            target_url=target_url.strip(),
            title=title.strip(),
            qr_history_id=qr_history_id,
            password_hash=password_hash,
            expires_at=expires_at,
            is_active=True,
            scan_count=0,
        )
        db.add(dyn_qr)
        db.commit()
        db.refresh(dyn_qr)
        logger.info(f"Created Dynamic QR code '{short_code}' for target '{target_url}'")
        return dyn_qr

    def get_by_code(self, db: Session, short_code: str) -> Optional[DynamicQR]:
        """Fetch Dynamic QR by short code."""
        return db.query(DynamicQR).filter(DynamicQR.short_code == short_code).first()

    def get_by_id(self, db: Session, dynamic_id: int) -> Optional[DynamicQR]:
        """Fetch Dynamic QR by primary key ID."""
        return db.query(DynamicQR).filter(DynamicQR.id == dynamic_id).first()

    def update_dynamic_qr(
        self,
        db: Session,
        dynamic_id: int,
        target_url: Optional[str] = None,
        title: Optional[str] = None,
        is_active: Optional[bool] = None,
        password: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> DynamicQR:
        """Update Dynamic QR attributes (e.g. target URL after print)."""
        dyn = db.query(DynamicQR).filter(DynamicQR.id == dynamic_id).first()
        if not dyn:
            raise ValueError(f"Dynamic QR with ID {dynamic_id} not found")

        if target_url is not None:
            dyn.target_url = target_url.strip()
        if title is not None:
            dyn.title = title.strip()
        if is_active is not None:
            dyn.is_active = is_active
        if password is not None:
            dyn.password_hash = _password_hasher.hash(password) if password else None
        if expires_at is not None:
            dyn.expires_at = expires_at

        db.commit()
        db.refresh(dyn)
        logger.info(f"Updated Dynamic QR ID {dynamic_id} target to '{dyn.target_url}'")
        return dyn

    def verify_password(self, dyn: DynamicQR, password: str, db: Optional[Session] = None) -> bool:
        """
        Verify password using Argon2id with backward compatibility for legacy SHA-256.
        Automatically upgrades valid SHA-256 hashes to Argon2id.
        """
        if not dyn.password_hash:
            return True

        if dyn.password_hash.startswith("$argon2"):
            try:
                return _password_hasher.verify(dyn.password_hash, password)
            except (VerifyMismatchError, Exception):
                return False

        # Legacy SHA-256 verification
        legacy_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if legacy_hash == dyn.password_hash:
            if db:
                try:
                    dyn.password_hash = _password_hasher.hash(password)
                    db.commit()
                except Exception as exc:
                    logger.warning(f"Could not upgrade legacy password hash: {exc}")
            return True
        return False

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
        """Log a real-time scan event with device, browser, and OS detection."""
        device_type = "Desktop"
        browser = "Unknown"

        # Privacy-aware IP masking: mask last octet/hextet
        masked_ip = self._mask_ip(ip_address) if ip_address else None

        if user_agent_str:
            try:
                ua = parse(user_agent_str)
                if ua.is_mobile:
                    device_type = "Mobile"
                elif ua.is_tablet:
                    device_type = "Tablet"
                elif ua.is_pc:
                    device_type = "Desktop"
                elif ua.is_bot:
                    device_type = "Bot"

                browser_name = ua.browser.family or "Unknown"
                os_name = ua.os.family or "Unknown"
                browser = f"{browser_name} ({os_name})"
            except Exception:
                pass

        scan = ScanLog(
            dynamic_qr_id=dynamic_qr.id,
            ip_address=masked_ip,
            user_agent=user_agent_str[:500] if user_agent_str else None,
            device_type=device_type,
            browser=browser[:50] if browser else None,
            referer=referer[:500] if referer else None,
        )
        db.add(scan)

        # Increment counters
        dynamic_qr.scan_count += 1
        if dynamic_qr.qr_history_id:
            history = db.query(QRHistory).filter(QRHistory.id == dynamic_qr.qr_history_id).first()
            if history:
                history.download_count = (history.download_count or 0) + 1

        db.commit()
        db.refresh(scan)
        return scan

    def _mask_ip(self, ip: str) -> str:
        """Mask IP address to preserve privacy (e.g. 192.168.1.xxx)."""
        if ":" in ip:  # IPv6
            parts = ip.split(":")
            return ":".join(parts[:3]) + ":*:*" if len(parts) >= 3 else ip
        if "." in ip:  # IPv4
            parts = ip.split(".")
            return ".".join(parts[:3]) + ".xxx" if len(parts) == 4 else ip
        return ip

    def get_analytics(self, db: Session, dynamic_id: int) -> Dict[str, Any]:
        """Return comprehensive analytics breakdown for a dynamic QR code."""
        dyn = db.query(DynamicQR).filter(DynamicQR.id == dynamic_id).first()
        if not dyn:
            raise ValueError(f"Dynamic QR with ID {dynamic_id} not found")

        total_scans = dyn.scan_count
        unique_scans = (
            db.query(func.count(distinct(ScanLog.ip_address)))
            .filter(ScanLog.dynamic_qr_id == dynamic_id)
            .scalar() or 0
        )

        device_counts = (
            db.query(ScanLog.device_type, func.count(ScanLog.id))
            .filter(ScanLog.dynamic_qr_id == dynamic_id)
            .group_by(ScanLog.device_type)
            .all()
        )

        browser_counts = (
            db.query(ScanLog.browser, func.count(ScanLog.id))
            .filter(ScanLog.dynamic_qr_id == dynamic_id)
            .group_by(ScanLog.browser)
            .all()
        )

        # 7-day scan timeline
        timeline_rows = (
            db.query(func.date(ScanLog.scanned_at).label("d"), func.count(ScanLog.id))
            .filter(ScanLog.dynamic_qr_id == dynamic_id)
            .group_by("d")
            .order_by("d")
            .limit(30)
            .all()
        )
        timeline = [{"date": str(r[0]), "scans": r[1]} for r in timeline_rows]

        return {
            "id": dyn.id,
            "short_code": dyn.short_code,
            "title": dyn.title,
            "target_url": dyn.target_url,
            "redirect_url": f"{settings.PUBLIC_REDIRECT_BASE_URL.rstrip('/')}/r/{dyn.short_code}",
            "total_scans": total_scans,
            "unique_scans": unique_scans,
            "is_active": dyn.is_active,
            "is_expired": self.is_expired(dyn),
            "has_password": bool(dyn.password_hash),
            "expires_at": dyn.expires_at.isoformat() if dyn.expires_at else None,
            "devices": [{"device": d or "Unknown", "count": c} for d, c in device_counts],
            "browsers": [{"browser": b or "Unknown", "count": c} for b, c in browser_counts],
            "timeline": timeline,
        }


# Singleton
dynamic_qr_service = DynamicQRService()
