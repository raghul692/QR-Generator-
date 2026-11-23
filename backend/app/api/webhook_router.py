"""
QRMaster Pro — Webhooks API Router.

Endpoints for managing real-time webhook subscriptions, viewing delivery logs,
and sending test ping payloads with HMAC-SHA256 signatures.
"""
from __future__ import annotations

import secrets
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_workspace
from app.database.session import get_db
from app.models import WebhookDeliveryLog, WebhookSubscription
from app.services.webhook_service import is_safe_webhook_url, webhook_service

router = APIRouter(prefix="/webhooks", tags=["Developer Webhooks"])


class WebhookCreateRequest(BaseModel):
    target_url: str = Field(..., max_length=2048, example="https://api.yourcompany.com/qrmaster-webhook")
    events: str = Field(
        default="scan.created,qr.expired,qr.limit_reached",
        max_length=255,
        example="scan.created,qr.expired",
    )


class WebhookUpdateRequest(BaseModel):
    target_url: Optional[str] = Field(None, max_length=2048)
    events: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


@router.get("", response_model=List[Dict[str, Any]])
def list_webhooks(
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """List all registered webhook subscriptions for the current tenant."""
    subs = (
        db.query(WebhookSubscription)
        .filter(WebhookSubscription.workspace_id == workspace_id)
        .order_by(WebhookSubscription.created_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "workspace_id": s.workspace_id,
            "target_url": s.target_url,
            "events": [e.strip() for e in s.events.split(",") if e.strip()],
            "is_active": s.is_active,
            "failure_count": s.failure_count,
            "last_triggered_at": s.last_triggered_at.isoformat() if s.last_triggered_at else None,
            "last_status_code": s.last_status_code,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in subs
    ]


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_webhook(
    data: WebhookCreateRequest,
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Register a new webhook subscription and generate an HMAC signing secret."""
    if not is_safe_webhook_url(data.target_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unsafe webhook URL. Must be public HTTP/HTTPS destination.",
        )

    # Generate 32-byte secure signing secret
    secret = "whsec_" + secrets.token_hex(24)

    sub = WebhookSubscription(
        workspace_id=workspace_id,
        target_url=data.target_url.strip(),
        secret=secret,
        events=data.events.strip(),
        is_active=True,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    return {
        "id": sub.id,
        "workspace_id": sub.workspace_id,
        "target_url": sub.target_url,
        "events": [e.strip() for e in sub.events.split(",") if e.strip()],
        "secret": sub.secret,  # Returned upon creation for user to copy
        "is_active": sub.is_active,
        "created_at": sub.created_at.isoformat(),
        "warning": "Store this webhook signing secret securely. Use it to verify HMAC signatures.",
    }


@router.get("/{webhook_id}", response_model=Dict[str, Any])
def get_webhook(
    webhook_id: int,
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Retrieve webhook details and recent delivery history."""
    sub = (
        db.query(WebhookSubscription)
        .filter(WebhookSubscription.id == webhook_id, WebhookSubscription.workspace_id == workspace_id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return {
        "id": sub.id,
        "workspace_id": sub.workspace_id,
        "target_url": sub.target_url,
        "events": [e.strip() for e in sub.events.split(",") if e.strip()],
        "is_active": sub.is_active,
        "failure_count": sub.failure_count,
        "last_triggered_at": sub.last_triggered_at.isoformat() if sub.last_triggered_at else None,
        "last_status_code": sub.last_status_code,
        "created_at": sub.created_at.isoformat() if sub.created_at else None,
    }


@router.put("/{webhook_id}", response_model=Dict[str, Any])
def update_webhook(
    webhook_id: int,
    data: WebhookUpdateRequest,
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Update webhook URL, subscribed events, or active status."""
    sub = (
        db.query(WebhookSubscription)
        .filter(WebhookSubscription.id == webhook_id, WebhookSubscription.workspace_id == workspace_id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Webhook not found")

    if data.target_url is not None:
        if not is_safe_webhook_url(data.target_url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or unsafe webhook URL. Must be public HTTP/HTTPS destination.",
            )
        sub.target_url = data.target_url.strip()

    if data.events is not None:
        sub.events = data.events.strip()

    if data.is_active is not None:
        sub.is_active = data.is_active

    db.commit()
    db.refresh(sub)

    return {
        "id": sub.id,
        "workspace_id": sub.workspace_id,
        "target_url": sub.target_url,
        "events": [e.strip() for e in sub.events.split(",") if e.strip()],
        "is_active": sub.is_active,
        "failure_count": sub.failure_count,
        "last_triggered_at": sub.last_triggered_at.isoformat() if sub.last_triggered_at else None,
        "last_status_code": sub.last_status_code,
        "created_at": sub.created_at.isoformat() if sub.created_at else None,
    }


@router.delete("/{webhook_id}")
def delete_webhook(
    webhook_id: int,
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Delete a webhook subscription and all its delivery logs."""
    sub = (
        db.query(WebhookSubscription)
        .filter(WebhookSubscription.id == webhook_id, WebhookSubscription.workspace_id == workspace_id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Webhook not found")

    db.delete(sub)
    db.commit()
    return {"status": "success", "message": f"Webhook {webhook_id} deleted successfully"}


@router.post("/{webhook_id}/test")
def test_ping_webhook(
    webhook_id: int,
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Dispatch a test ping payload (`webhook.test_ping`) to verify connectivity and signature."""
    sub = (
        db.query(WebhookSubscription)
        .filter(WebhookSubscription.id == webhook_id, WebhookSubscription.workspace_id == workspace_id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Webhook not found")

    test_payload = {
        "message": "This is a test notification from QRMaster Pro.",
        "webhook_id": sub.id,
        "timestamp": int(sub.created_at.timestamp() if sub.created_at else 0),
    }

    result = webhook_service.send_webhook(db, sub, "webhook.test_ping", test_payload)
    return {
        "status": "success",
        "result": result,
    }


@router.get("/{webhook_id}/deliveries")
def list_webhook_deliveries(
    webhook_id: int,
    limit: int = 20,
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """List the most recent execution logs and HTTP responses for this webhook."""
    sub = (
        db.query(WebhookSubscription)
        .filter(WebhookSubscription.id == webhook_id, WebhookSubscription.workspace_id == workspace_id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Webhook not found")

    logs = (
        db.query(WebhookDeliveryLog)
        .filter(WebhookDeliveryLog.webhook_id == webhook_id)
        .order_by(WebhookDeliveryLog.delivered_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": log.id,
            "event_type": log.event_type,
            "response_status": log.response_status,
            "execution_duration_ms": log.execution_duration_ms,
            "delivered_at": log.delivered_at.isoformat() if log.delivered_at else None,
            "response_body": log.response_body,
        }
        for log in logs
    ]
