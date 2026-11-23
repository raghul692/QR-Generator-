"""
QRMaster Pro — Dynamic QR Service.

Manages Dynamic QR codes, short code generation, target URL updates,
Argon2id password protection (with SHA-256 upgrade), expiration checks,
and privacy-aware real-time scan telemetry.
"""
from __future__ import annotations

import hashlib
import json
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
        ios_target_url: Optional[str] = None,
        android_target_url: Optional[str] = None,
        max_scans: Optional[int] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        meta_pixel_id: Optional[str] = None,
        google_tag_id: Optional[str] = None,
        geo_routing_json: Optional[str] = None,
        schedule_start_time: Optional[str] = None,
        schedule_end_time: Optional[str] = None,
        schedule_timezone: Optional[str] = None,
        schedule_fallback_url: Optional[str] = None,
        workspace_id: str = "ws_legacy_default",
    ) -> DynamicQR:
        """Create a new Dynamic QR record with Argon2id password hashing, smart OS routing, geo-fencing, and scheduling."""
        short_code = self.generate_short_code(db)
        password_hash = _password_hasher.hash(password) if password else None

        dyn_qr = DynamicQR(
            short_code=short_code,
            target_url=target_url.strip(),
            title=title.strip(),
            workspace_id=workspace_id,
            qr_history_id=qr_history_id,
            password_hash=password_hash,
            expires_at=expires_at,
            ios_target_url=ios_target_url.strip() if ios_target_url else None,
            android_target_url=android_target_url.strip() if android_target_url else None,
            max_scans=max_scans,
            utm_source=utm_source.strip() if utm_source else None,
            utm_medium=utm_medium.strip() if utm_medium else None,
            utm_campaign=utm_campaign.strip() if utm_campaign else None,
            meta_pixel_id=meta_pixel_id.strip() if meta_pixel_id else None,
            google_tag_id=google_tag_id.strip() if google_tag_id else None,
            geo_routing_json=geo_routing_json.strip() if geo_routing_json else None,
            schedule_start_time=schedule_start_time.strip() if schedule_start_time else None,
            schedule_end_time=schedule_end_time.strip() if schedule_end_time else None,
            schedule_timezone=schedule_timezone.strip() if schedule_timezone else None,
            schedule_fallback_url=schedule_fallback_url.strip() if schedule_fallback_url else None,
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
        ios_target_url: Optional[str] = None,
        android_target_url: Optional[str] = None,
        max_scans: Optional[int] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        meta_pixel_id: Optional[str] = None,
        google_tag_id: Optional[str] = None,
        geo_routing_json: Optional[str] = None,
        schedule_start_time: Optional[str] = None,
        schedule_end_time: Optional[str] = None,
        schedule_timezone: Optional[str] = None,
        schedule_fallback_url: Optional[str] = None,
    ) -> DynamicQR:
        """Update Dynamic QR attributes (e.g. target URL after print, OS routes, attribution, limits, geo & schedule)."""
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
        if ios_target_url is not None:
            dyn.ios_target_url = ios_target_url.strip() if ios_target_url else None
        if android_target_url is not None:
            dyn.android_target_url = android_target_url.strip() if android_target_url else None
        if max_scans is not None:
            dyn.max_scans = max_scans
        if utm_source is not None:
            dyn.utm_source = utm_source.strip() if utm_source else None
        if utm_medium is not None:
            dyn.utm_medium = utm_medium.strip() if utm_medium else None
        if utm_campaign is not None:
            dyn.utm_campaign = utm_campaign.strip() if utm_campaign else None
        if meta_pixel_id is not None:
            dyn.meta_pixel_id = meta_pixel_id.strip() if meta_pixel_id else None
        if google_tag_id is not None:
            dyn.google_tag_id = google_tag_id.strip() if google_tag_id else None
        if geo_routing_json is not None:
            dyn.geo_routing_json = geo_routing_json.strip() if geo_routing_json else None
        if schedule_start_time is not None:
            dyn.schedule_start_time = schedule_start_time.strip() if schedule_start_time else None
        if schedule_end_time is not None:
            dyn.schedule_end_time = schedule_end_time.strip() if schedule_end_time else None
        if schedule_timezone is not None:
            dyn.schedule_timezone = schedule_timezone.strip() if schedule_timezone else None
        if schedule_fallback_url is not None:
            dyn.schedule_fallback_url = schedule_fallback_url.strip() if schedule_fallback_url else None

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

    def resolve_destination_url(
        self,
        dyn: DynamicQR,
        user_agent_str: Optional[str] = None,
        country_code: Optional[str] = None,
        current_time: Optional[datetime] = None,
    ) -> str:
        """
        Resolve destination URL applying multi-layer smart routing:
        1. Time-of-Day Business Hours Check: if outside schedule window, route to fallback URL.
        2. Geo-Fencing: if country code matches geo_routing_json, route to country target.
        3. OS Smart Routing: if user on iOS or Android, route to platform app target.
        4. Default fallback: primary target_url.
        """
        now = current_time or datetime.now()

        # 1. Time-of-Day Schedule Check
        if dyn.schedule_start_time and dyn.schedule_end_time and dyn.schedule_fallback_url:
            try:
                # Compare HH:MM strings
                now_str = now.strftime("%H:%M")
                start = dyn.schedule_start_time.strip()
                end = dyn.schedule_end_time.strip()
                is_within = (start <= now_str <= end) if start <= end else (now_str >= start or now_str <= end)
                if not is_within:
                    logger.info(f"Time Schedule applied: {dyn.short_code} redirected to off-hours fallback")
                    return dyn.schedule_fallback_url
            except Exception as exc:
                logger.warning(f"Schedule evaluation error for {dyn.short_code}: {exc}")

        # 2. Geo-Fencing Check
        if dyn.geo_routing_json and country_code:
            try:
                geo_map = json.loads(dyn.geo_routing_json)
                code_upper = country_code.strip().upper()
                if code_upper in geo_map and geo_map[code_upper]:
                    logger.info(f"Geo-Fencing applied: routed {dyn.short_code} for country {code_upper}")
                    return geo_map[code_upper]
                elif "DEFAULT" in geo_map and geo_map["DEFAULT"]:
                    return geo_map["DEFAULT"]
            except Exception as exc:
                logger.warning(f"Geo routing parsing error for {dyn.short_code}: {exc}")

        # 3. OS Smart Routing Check
        if user_agent_str:
            try:
                ua = parse(user_agent_str)
                os_family = (ua.os.family or "").lower()
                if any(token in os_family for token in ["ios", "iphone", "ipad", "ipod"]) and dyn.ios_target_url:
                    logger.info(f"OS Smart Routing applied: directed {dyn.short_code} to iOS App Store target")
                    return dyn.ios_target_url
                elif "android" in os_family and dyn.android_target_url:
                    logger.info(f"OS Smart Routing applied: directed {dyn.short_code} to Android Play Store target")
                    return dyn.android_target_url
            except Exception as exc:
                logger.warning(f"OS parsing error in resolve_destination_url: {exc}")

        return dyn.target_url

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

        # Increment scan counter
        dynamic_qr.scan_count += 1

        db.commit()
        db.refresh(scan)

        # Real-time Webhook dispatch
        try:
            from app.services.webhook_service import webhook_service
            webhook_service.dispatch_event(
                db,
                event_type="scan.created",
                payload={
                    "scan_id": scan.id,
                    "dynamic_qr_id": dynamic_qr.id,
                    "short_code": dynamic_qr.short_code,
                    "title": dynamic_qr.title,
                    "device_type": device_type,
                    "browser": browser,
                    "scan_count": dynamic_qr.scan_count,
                    "scanned_at": scan.scanned_at.isoformat() if scan.scanned_at else datetime.now().isoformat(),
                },
                workspace_id=dynamic_qr.workspace_id,
            )
        except Exception as exc:
            logger.warning(f"Could not dispatch scan.created webhook: {exc}")

        return scan

    def _mask_ip(self, ip: str) -> str:
        """Mask IP address according to GDPR data minimization standards."""
        if not ip:
            return "0.0.0.0"
        if ":" in ip:  # IPv6 - mask host identifier
            parts = ip.split(":")
            return ":".join(parts[:3]) + "::0" if len(parts) >= 3 else ip
        if "." in ip:  # IPv4 - mask last octet to .0 for /24 anonymization
            parts = ip.split(".")
            return ".".join(parts[:3]) + ".0" if len(parts) == 4 else ip
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
            "max_scans": dyn.max_scans,
            "utm_source": dyn.utm_source,
            "utm_medium": dyn.utm_medium,
            "utm_campaign": dyn.utm_campaign,
            "meta_pixel_id": dyn.meta_pixel_id,
            "google_tag_id": dyn.google_tag_id,
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
