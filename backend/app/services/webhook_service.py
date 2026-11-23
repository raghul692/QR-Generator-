"""
QRMaster Pro — Webhook Dispatcher & HMAC-SHA256 Signing Service.

Dispatches real-time event notifications (`scan.created`, `qr.expired`, `qr.limit_reached`)
to customer endpoints with HMAC-SHA256 cryptographic signatures, SSRF loopback protections,
and delivery execution logging.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from sqlalchemy.orm import Session

from app.models import WebhookDeliveryLog, WebhookSubscription
from app.utils.logger import logger

SIGNATURE_VERSION = "v1"
BLOCKED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "169.254.169.254",
    "::1",
}


def is_safe_webhook_url(url: str) -> bool:
    """
    Validate webhook URL against SSRF attacks (Server-Side Request Forgery).
    Enforces http/https schemes and disallows internal loopback or cloud metadata addresses.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme not in ("http", "https"):
            return False
        host = (parsed.hostname or "").lower()
        if not host or host in BLOCKED_HOSTS:
            return False
        # Disallow private RFC 1918 subnets in hostname
        if host.startswith("10.") or host.startswith("192.168.") or host.startswith("172.16."):
            return False
        return True
    except Exception:
        return False


def generate_hmac_signature(secret: str, payload_str: str, timestamp: int) -> str:
    """
    Compute Stripe-standard HMAC-SHA256 signature header:
    Header format: t={timestamp},v1={hex_digest}
    Signed data: {timestamp}.{payload_str}
    """
    signed_payload = f"{timestamp}.{payload_str}"
    signature = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},{SIGNATURE_VERSION}={signature}"


class WebhookService:
    """Service orchestrating webhook signing, HTTP dispatch, and delivery audits."""

    @staticmethod
    def dispatch_event(
        db: Session,
        event_type: str,
        payload: Dict[str, Any],
        workspace_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find all active webhook subscriptions matching event_type and workspace,
        deliver HTTP POST payloads with HMAC-SHA256 signatures, and log results.
        """
        query = db.query(WebhookSubscription).filter(WebhookSubscription.is_active == True)
        if workspace_id:
            query = query.filter(
                (WebhookSubscription.workspace_id == workspace_id)
                | (WebhookSubscription.workspace_id == "ws_legacy_default")
            )

        subscriptions = query.all()
        results: List[Dict[str, Any]] = []

        for sub in subscriptions:
            # Check event subscription match
            subscribed_events = [e.strip() for e in sub.events.split(",") if e.strip()]
            if "*" not in subscribed_events and event_type not in subscribed_events:
                continue

            result = WebhookService.send_webhook(db, sub, event_type, payload)
            results.append(result)

        return results

    @staticmethod
    def send_webhook(
        db: Session,
        sub: WebhookSubscription,
        event_type: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Deliver a single webhook payload, sign it, and record delivery log."""
        if not is_safe_webhook_url(sub.target_url):
            logger.warning(f"[WEBHOOK] Blocked unsafe target URL: {sub.target_url}")
            return {
                "webhook_id": sub.id,
                "status": "blocked",
                "error": "Target URL blocked by SSRF defense policy",
            }

        now_ts = int(time.time())
        envelope = {
            "id": f"evt_{now_ts}_{sub.id}",
            "event": event_type,
            "created_at": datetime.now().isoformat(),
            "data": payload,
        }
        payload_str = json.dumps(envelope, separators=(",", ":"), sort_keys=True)
        signature_header = generate_hmac_signature(sub.secret, payload_str, now_ts)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "QRMaster-Webhook-Worker/2.5",
            "X-QRMaster-Event": event_type,
            "X-QRMaster-Signature": signature_header,
        }

        start_time = time.perf_counter()
        status_code = None
        response_body = None

        try:
            with httpx.Client(timeout=5.0) as http_client:
                resp = http_client.post(sub.target_url, content=payload_str, headers=headers)
                status_code = resp.status_code
                response_body = resp.text[:1000]
                if resp.is_success:
                    sub.failure_count = 0
                else:
                    sub.failure_count += 1
        except Exception as exc:
            sub.failure_count += 1
            response_body = f"Connection error: {str(exc)}"[:1000]

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        sub.last_triggered_at = datetime.now()
        sub.last_status_code = status_code

        # Record delivery log
        log_entry = WebhookDeliveryLog(
            webhook_id=sub.id,
            event_type=event_type,
            payload_json=payload_str,
            response_status=status_code,
            response_body=response_body,
            execution_duration_ms=duration_ms,
        )
        db.add(log_entry)
        db.commit()

        return {
            "webhook_id": sub.id,
            "event": event_type,
            "target_url": sub.target_url,
            "status_code": status_code,
            "duration_ms": duration_ms,
        }


webhook_service = WebhookService()
