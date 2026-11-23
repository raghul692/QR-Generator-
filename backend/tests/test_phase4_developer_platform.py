"""
QRMaster Pro — Phase 4 Test Suite: Developer Platform, Webhooks, Geo-Fencing & Scheduling.

Tests:
1. API key scopes generation and granular scope checking.
2. Webhook subscription CRUD and SSRF loopback protections.
3. HMAC-SHA256 signature calculation and test ping dispatch recording.
4. Dynamic QR Geo-Fencing routing (country headers and fallback).
5. Dynamic QR Time-of-day business schedule routing and off-hours fallback.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import require_api_key_scope, verify_api_key
from app.models import APIKey, DynamicQR, WebhookDeliveryLog, WebhookSubscription
from app.services.dynamic_qr_service import dynamic_qr_service
from app.services.webhook_service import (
    generate_hmac_signature,
    is_safe_webhook_url,
    webhook_service,
)


def test_api_key_creation_and_scopes(client: TestClient, db_session: Session):
    """Test API key creation with scopes and listing."""
    # 1. Create a key with restricted scopes
    create_res = client.post(
        "/api/v1/keys",
        json={
            "name": "Phase 4 Analytics Reader",
            "rate_limit": 500,
            "scopes": "qr:read,analytics:read",
        },
    )
    assert create_res.status_code == 201
    data = create_res.json()
    assert "api_key" in data
    assert data["name"] == "Phase 4 Analytics Reader"
    assert data["scopes"] == "qr:read,analytics:read"
    raw_key = data["api_key"]
    assert raw_key.startswith("qrm_live_")

    # 2. List keys and verify scopes are exposed
    list_res = client.get("/api/v1/keys")
    assert list_res.status_code == 200
    keys = list_res.json()
    created_key_entry = next((k for k in keys if k["name"] == "Phase 4 Analytics Reader"), None)
    assert created_key_entry is not None
    assert created_key_entry["scopes"] == "qr:read,analytics:read"

    # 3. Verify require_api_key_scope logic
    key_record = db_session.query(APIKey).filter(APIKey.name == "Phase 4 Analytics Reader").first()
    assert key_record is not None

    # Allowed scope check
    checker_read = require_api_key_scope("qr:read")
    assert checker_read(key_record) == key_record

    checker_analytics = require_api_key_scope("analytics:read")
    assert checker_analytics(key_record) == key_record

    # Disallowed scope check -> HTTP 403 Forbidden
    checker_write = require_api_key_scope("qr:write")
    with pytest.raises(HTTPException) as exc_info:
        checker_write(key_record)
    assert exc_info.value.status_code == 403

    # Admin scope grants everything
    admin_key = APIKey(
        name="Phase 4 Super Admin Key",
        key_prefix="qrm_adm1",
        key_hash=hashlib.sha256(b"admin_secret_test").hexdigest(),
        is_active=True,
        scopes="admin",
    )
    assert checker_write(admin_key) == admin_key


def test_ssrf_webhook_url_validation():
    """Verify is_safe_webhook_url blocks SSRF attack targets and allows valid HTTPS targets."""
    # Disallowed SSRF loopback and cloud metadata
    assert is_safe_webhook_url("http://127.0.0.1:8000/webhook") is False
    assert is_safe_webhook_url("http://localhost:3000/hook") is False
    assert is_safe_webhook_url("http://0.0.0.0/webhook") is False
    assert is_safe_webhook_url("http://169.254.169.254/latest/meta-data/") is False
    assert is_safe_webhook_url("http://[::1]:8080/hook") is False
    assert is_safe_webhook_url("http://192.168.1.1/hook") is False
    assert is_safe_webhook_url("http://10.0.0.5/hook") is False
    assert is_safe_webhook_url("ftp://api.example.com/hook") is False
    assert is_safe_webhook_url("") is False
    assert is_safe_webhook_url(None) is False

    # Allowed public production endpoints
    assert is_safe_webhook_url("https://api.acmecorp.com/webhooks/qrmaster") is True
    assert is_safe_webhook_url("https://hooks.zapier.com/hooks/catch/12345/abcde") is True
    assert is_safe_webhook_url("http://webhook.site/unique-uuid-1234") is True


def test_webhook_crud_and_ssrf_blocking(client: TestClient, db_session: Session):
    """Test webhook subscription creation, listing, updating, SSRF rejection, and deletion."""
    # 1. Attempt SSRF URL -> 400 Bad Request
    ssrf_res = client.post(
        "/api/v1/webhooks",
        json={"target_url": "http://127.0.0.1:9000/internal-admin", "events": "scan.created"},
    )
    assert ssrf_res.status_code == 400
    assert "Invalid or unsafe webhook URL" in ssrf_res.json()["detail"]

    # 2. Create valid webhook
    create_res = client.post(
        "/api/v1/webhooks",
        json={
            "target_url": "https://api.partner.io/v1/qr-events",
            "events": "scan.created,qr.expired",
        },
    )
    assert create_res.status_code == 201
    webhook_data = create_res.json()
    webhook_id = webhook_data["id"]
    secret = webhook_data["secret"]
    assert secret.startswith("whsec_")
    assert webhook_data["target_url"] == "https://api.partner.io/v1/qr-events"

    # 3. List webhooks
    list_res = client.get("/api/v1/webhooks")
    assert list_res.status_code == 200
    hooks = list_res.json()
    assert any(h["id"] == webhook_id for h in hooks)

    # 4. Update webhook
    update_res = client.put(
        f"/api/v1/webhooks/{webhook_id}",
        json={"is_active": False},
    )
    assert update_res.status_code == 200
    assert update_res.json()["is_active"] is False

    # Reactivate
    client.put(f"/api/v1/webhooks/{webhook_id}", json={"is_active": True})

    # 5. Delete webhook
    del_res = client.delete(f"/api/v1/webhooks/{webhook_id}")
    assert del_res.status_code == 200


def test_webhook_signing_and_test_ping(client: TestClient, db_session: Session):
    """Verify HMAC-SHA256 signature format and test ping dispatch logging."""
    secret = "whsec_supersecretkey123456789"
    payload = json.dumps({"event": "ping", "message": "Test ping from QRMaster Pro"})
    timestamp = 1774390000

    sig_header = generate_hmac_signature(secret, payload, timestamp)
    assert sig_header.startswith(f"t={timestamp},v1=")

    # 1. Create a webhook subscription
    create_res = client.post(
        "/api/v1/webhooks",
        json={
            "target_url": "https://api.test-receiver.org/webhook",
            "events": "scan.created",
        },
    )
    assert create_res.status_code == 201
    hook_id = create_res.json()["id"]

    # 2. Trigger test ping with mocked httpx.Client in webhook_service
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = '{"received": true}'
    mock_resp.is_success = True

    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_resp
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = None

    with patch("app.services.webhook_service.httpx.Client", return_value=mock_client_instance):
        ping_res = client.post(f"/api/v1/webhooks/{hook_id}/test")
        assert ping_res.status_code == 200
        ping_data = ping_res.json()
        assert ping_data["status"] == "success"
        assert ping_data["result"]["status_code"] == 200

    # 3. Check delivery logs endpoint
    deliveries_res = client.get(f"/api/v1/webhooks/{hook_id}/deliveries")
    assert deliveries_res.status_code == 200
    logs = deliveries_res.json()
    assert len(logs) >= 1
    assert logs[0]["event_type"] == "webhook.test_ping"
    assert logs[0]["response_status"] == 200


def test_geo_fencing_resolution(client: TestClient, db_session: Session):
    """Verify Dynamic QR Geo-Fencing country code routing and fallback."""
    geo_config = {
        "IN": "https://in.brand.com/special-deal",
        "US": "https://us.brand.com/special-deal",
        "DEFAULT": "https://global.brand.com/special-deal",
    }
    primary_url = "https://brand.com/default"

    dyn_qr = dynamic_qr_service.create_dynamic_qr(
        db=db_session,
        title="Global Campaign 2026",
        target_url=primary_url,
        geo_routing_json=json.dumps(geo_config),
    )

    # 1. Country match: IN
    res_in = dynamic_qr_service.resolve_destination_url(
        dyn=dyn_qr,
        country_code="IN",
    )
    assert res_in == "https://in.brand.com/special-deal"

    # 2. Country match: US (case insensitive)
    res_us = dynamic_qr_service.resolve_destination_url(
        dyn=dyn_qr,
        country_code="us",
    )
    assert res_us == "https://us.brand.com/special-deal"

    # 3. Country unmapped -> DEFAULT from json
    res_de = dynamic_qr_service.resolve_destination_url(
        dyn=dyn_qr,
        country_code="DE",
    )
    assert res_de == "https://global.brand.com/special-deal"

    # 4. No country provided -> fallback primary target_url
    res_none = dynamic_qr_service.resolve_destination_url(
        dyn=dyn_qr,
        country_code=None,
    )
    assert res_none == primary_url

    # 5. Test redirection endpoint with CF-IPCountry header
    redirect_res = client.get(
        f"/r/{dyn_qr.short_code}",
        headers={"CF-IPCountry": "IN"},
        follow_redirects=False,
    )
    assert redirect_res.status_code in (302, 307)
    assert redirect_res.headers["location"] == "https://in.brand.com/special-deal"


def test_time_of_day_schedule_resolution(client: TestClient, db_session: Session):
    """Verify Dynamic QR business schedule routing and off-hours fallback."""
    primary_target = "https://restaurant.com/live-menu"
    closed_fallback = "https://restaurant.com/closed-hours"

    # Daytime schedule: 09:00 to 17:00
    dyn_daytime = dynamic_qr_service.create_dynamic_qr(
        db=db_session,
        title="Lunch Specials",
        target_url=primary_target,
        schedule_start_time="09:00",
        schedule_end_time="17:00",
        schedule_fallback_url=closed_fallback,
    )

    # During business hours (12:00) -> primary target
    during_hours = datetime(2026, 6, 1, 12, 0, 0)
    assert dynamic_qr_service.resolve_destination_url(dyn_daytime, current_time=during_hours) == primary_target

    # Outside business hours (20:00) -> off-hours fallback
    outside_hours = datetime(2026, 6, 1, 20, 0, 0)
    assert dynamic_qr_service.resolve_destination_url(dyn_daytime, current_time=outside_hours) == closed_fallback

    # Overnight schedule: 22:00 to 06:00
    dyn_overnight = dynamic_qr_service.create_dynamic_qr(
        db=db_session,
        title="Nightclub VIP Access",
        target_url=primary_target,
        schedule_start_time="22:00",
        schedule_end_time="06:00",
        schedule_fallback_url=closed_fallback,
    )

    # Late night (23:30) -> within window -> primary target
    late_night = datetime(2026, 6, 1, 23, 30, 0)
    assert dynamic_qr_service.resolve_destination_url(dyn_overnight, current_time=late_night) == primary_target

    # Early morning (03:15) -> within window -> primary target
    early_morning = datetime(2026, 6, 1, 3, 15, 0)
    assert dynamic_qr_service.resolve_destination_url(dyn_overnight, current_time=early_morning) == primary_target

    # Daytime (14:00) -> outside window -> fallback
    afternoon = datetime(2026, 6, 1, 14, 0, 0)
    assert dynamic_qr_service.resolve_destination_url(dyn_overnight, current_time=afternoon) == closed_fallback
