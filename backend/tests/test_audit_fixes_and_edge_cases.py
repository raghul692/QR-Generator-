"""
Tests for audit fixes, edge cases, templates, and analytics telemetry.
"""
import io
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.deps import verify_api_key
from app.database.seed import seed_templates
from app.models import ActivityLog, DynamicQR, QRCategory, QRHistory, QRTemplate, ScanLog
from app.services.analytics_service import analytics_service
from app.services.category_service import category_service
from app.services.dynamic_qr_service import dynamic_qr_service
from app.services.qr_service import qr_service
from app.services.storage_service import storage_service


def test_failed_password_attempt_logging_and_analytics(client, db_session: Session):
    """Verify failed password attempt is logged to ActivityLog and reported in stats."""
    # 1. Create protected dynamic QR
    dyn = dynamic_qr_service.create_dynamic_qr(
        db=db_session,
        title="Protected Report",
        target_url="https://example.com/confidential",
        password="secret123",
    )

    # 2. Submit wrong password
    res = client.post(f"/r/{dyn.short_code}/unlock", data={"password": "wrongpassword"})
    assert res.status_code == 401

    # 3. Check ActivityLog
    log = (
        db_session.query(ActivityLog)
        .filter(ActivityLog.action == "failed_password_attempt")
        .order_by(ActivityLog.id.desc())
        .first()
    )
    assert log is not None
    assert log.module == "dynamic_qr"
    assert dyn.short_code in log.details

    # 4. Check analytics reports failed password attempt
    stats = analytics_service.get_dashboard_stats(db_session)
    assert stats["failed_password_attempts"] >= 1


def test_unique_scans_and_browser_os_breakdown(client, db_session: Session):
    """Verify unique scans calculation and browser/OS telemetry parsing."""
    dyn = dynamic_qr_service.create_dynamic_qr(
        db=db_session,
        title="Multi-Device Scan",
        target_url="https://example.com/docs",
    )

    # Log 3 scans from 2 distinct IPs
    dynamic_qr_service.log_scan(
        db_session, dyn, ip_address="203.0.113.10",
        user_agent_str="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    )
    dynamic_qr_service.log_scan(
        db_session, dyn, ip_address="203.0.113.10",  # Same IP (repeat scan)
        user_agent_str="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    )
    dynamic_qr_service.log_scan(
        db_session, dyn, ip_address="198.51.100.44",  # Different IP
        user_agent_str="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 Mobile Safari/16.5",
    )

    stats = analytics_service.get_dashboard_stats(db_session)
    assert stats["total_scans"] >= 3
    assert stats["unique_scans"] >= 2

    # Check breakdown functions
    browsers = analytics_service._browser_distribution(db_session)
    os_dist = analytics_service._os_distribution(db_session)
    assert any("Chrome" in b["label"] or "Safari" in b["label"] for b in browsers)
    assert any("Windows" in o["label"] or "iOS" in o["label"] for o in os_dist)


def test_storage_service_qr_integration(db_session: Session):
    """Verify QR persistence uses relative paths and reads through storage_service."""
    res = qr_service.generate(
        db=db_session,
        title="Storage Integration Test",
        qr_type="url",
        data={"url": "https://example.com"},
        save_to_history=True,
    )
    assert res["id"] is not None
    file_path = res["file_path"]
    assert file_path is not None
    # Must NOT be an absolute Windows or Linux path
    assert not file_path.startswith("D:\\")
    assert not file_path.startswith("C:\\")

    # Verify storage_service can read back the asset
    content = storage_service.read_asset(file_path, bucket="qr-assets")
    assert content is not None
    assert len(content) > 100


def test_api_key_revocation_403_and_audit(client, db_session: Session):
    """Verify revoked API key returns 403 Forbidden and logs audit record."""
    create_res = client.post("/api/v1/keys", json={"name": "Audit Key Test", "rate_limit": 100})
    assert create_res.status_code == 201
    key_id = create_res.json()["id"]
    api_key = create_res.json()["api_key"]

    # Verify active
    verified = verify_api_key(x_api_key=api_key, db=db_session)
    assert verified.id == key_id

    # Revoke (soft deactivate by default)
    del_res = client.delete(f"/api/v1/keys/{key_id}")
    assert del_res.status_code == 200

    # Verify 403 Forbidden is raised with revoked detail
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(x_api_key=api_key, db=db_session)
    assert exc_info.value.status_code == 403
    assert "revoked" in exc_info.value.detail.lower()

    # Verify ActivityLog recorded revocation
    log = (
        db_session.query(ActivityLog)
        .filter(ActivityLog.action == "api_key_revoked")
        .order_by(ActivityLog.id.desc())
        .first()
    )
    assert log is not None
    assert str(key_id) in log.details


def test_template_crud_and_builtins(client, db_session: Session):
    """Verify template seeder, list, get, create, and built-in protection."""
    seed_templates(db_session)

    # 1. List templates
    list_res = client.get("/api/v1/templates")
    assert list_res.status_code == 200
    templates = list_res.json()
    assert len(templates) >= 6
    builtin_tmpl = next(t for t in templates if t["is_builtin"])

    # 2. Cannot delete built-in template
    del_builtin_res = client.delete(f"/api/v1/templates/{builtin_tmpl['id']}")
    assert del_builtin_res.status_code == 400

    # 3. Create custom template
    create_res = client.post(
        "/api/v1/templates",
        json={
            "name": "Custom Test Template",
            "description": "My test template",
            "config": {"size": 500, "foreground_color": "#112233", "qr_style": "dots"},
        },
    )
    assert create_res.status_code == 201
    custom_id = create_res.json()["id"]

    # 4. Get template
    get_res = client.get(f"/api/v1/templates/{custom_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Custom Test Template"

    # 5. Delete custom template
    del_custom_res = client.delete(f"/api/v1/templates/{custom_id}")
    assert del_custom_res.status_code == 200


def test_category_update_slug_collision_handled(db_session: Session):
    """Verify renaming a category to an existing name does not crash with unique constraint error."""
    cat1 = category_service.create(db_session, name="Newsletters", description="Email news")
    cat2 = category_service.create(db_session, name="Updates & Alerts", description="Alerts")

    # Update cat2 to "Newsletters" (which generates slug 'newsletters')
    updated = category_service.update(db_session, category_id=cat2["id"], name="Newsletters")
    assert updated is not None
    assert updated["id"] == cat2["id"]
    assert updated["slug"] != cat1["slug"]  # Disambiguated!


def test_bulk_upload_validation_edge_cases(client):
    """Verify bulk upload rejects invalid extensions, empty files, and sanitizes filenames."""
    # 1. Invalid extension
    res1 = client.post(
        "/api/v1/bulk/upload",
        files={"file": ("malicious.exe", b"binarycontent", "application/octet-stream")},
        data={"qr_type": "url"},
    )
    assert res1.status_code == 400
    assert "not supported" in res1.json()["detail"].lower()

    # 2. Empty file
    res2 = client.post(
        "/api/v1/bulk/upload",
        files={"file": ("empty.csv", b"", "text/csv")},
        data={"qr_type": "url"},
    )
    assert res2.status_code == 400
    assert "empty" in res2.json()["detail"].lower()

    # 3. Path traversal in filename is sanitized
    valid_csv = b"url\nhttps://example.com/1\nhttps://example.com/2\n"
    res3 = client.post(
        "/api/v1/bulk/upload",
        files={"file": ("../../traversal_test.csv", valid_csv, "text/csv")},
        data={"qr_type": "url", "job_name": "Traversal Test"},
    )
    assert res3.status_code == 200
    assert res3.json()["total_rows"] == 2


def test_generator_category_assignment_from_data_and_top_level(client, db_session: Session):
    """Verify category_id is assigned whether passed at top level or inside data dict."""
    cat = category_service.create(db_session, name="Web Destinations")
    cat_id = cat["id"]

    # Top-level category_id
    res1 = client.post(
        "/api/v1/qr/generate",
        json={
            "title": "Top-level Cat QR",
            "qr_type": "url",
            "data": {"url": "https://example.com/a"},
            "category_id": cat_id,
            "save_to_history": True,
        },
    )
    assert res1.status_code == 200
    qr1_id = res1.json()["id"]
    h1 = db_session.query(QRHistory).filter(QRHistory.id == qr1_id).first()
    assert h1.category_id == cat_id

    # Fallback category_id inside data dict
    res2 = client.post(
        "/api/v1/qr/generate",
        json={
            "title": "Data-nested Cat QR",
            "qr_type": "url",
            "data": {"url": "https://example.com/b", "category_id": cat_id},
            "save_to_history": True,
        },
    )
    assert res2.status_code == 200
    qr2_id = res2.json()["id"]
    h2 = db_session.query(QRHistory).filter(QRHistory.id == qr2_id).first()
    assert h2.category_id == cat_id


def test_gdpr_ip_masking():
    """Verify IPv4 (/24 zeroed) and IPv6 (host masked) anonymization."""
    # IPv4 standard
    assert dynamic_qr_service._mask_ip("192.168.1.150") == "192.168.1.0"
    assert dynamic_qr_service._mask_ip("10.0.5.42") == "10.0.5.0"

    # IPv6 standard
    assert dynamic_qr_service._mask_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334") == "2001:0db8:85a3::0"

    # Empty / fallback
    assert dynamic_qr_service._mask_ip("") == "0.0.0.0"


def test_qr_size_dos_bounds():
    """Verify QRCustomization enforces lower (120) and upper (2048) pixel size bounds."""
    from pydantic import ValidationError
    from app.qr_engine.customization import QRCustomization

    # Valid within bounds
    c_valid = QRCustomization(size=500)
    assert c_valid.size == 500

    # Below 120 -> ValidationError
    with pytest.raises(ValidationError):
        QRCustomization(size=50)

    # Above 2048 -> ValidationError (DoS prevention)
    with pytest.raises(ValidationError):
        QRCustomization(size=50000)


def test_rate_limiter_sliding_window():
    """Verify rate limiter allows up to limit and blocks subsequent requests."""
    from app.middleware.rate_limit import InMemoryRateLimiter

    limiter = InMemoryRateLimiter()
    ip = "192.0.2.1"
    bucket = "test_bucket"

    # Allow 3 requests
    assert limiter.is_allowed(ip, bucket, max_requests=3, window_seconds=10)[0] is True
    assert limiter.is_allowed(ip, bucket, max_requests=3, window_seconds=10)[0] is True
    assert limiter.is_allowed(ip, bucket, max_requests=3, window_seconds=10)[0] is True

    # 4th request must be blocked
    allowed, retry_after = limiter.is_allowed(ip, bucket, max_requests=3, window_seconds=10)
    assert allowed is False
    assert retry_after > 0


def test_storage_service_file_validation_and_lifecycle():
    """Verify storage_service file size, extension validation, and deletion."""
    from app.services.storage_service import storage_service, ALLOWED_IMAGE_EXTENSIONS

    # 1. Allowed extension passes
    storage_service.validate_file("logo.png", 1024, allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)

    # 2. Disallowed extension raises ValueError
    with pytest.raises(ValueError, match="not permitted"):
        storage_service.validate_file("malicious.exe", 1024, allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)

    # 3. Oversized file raises ValueError
    with pytest.raises(ValueError, match="exceeds limit"):
        storage_service.validate_file("huge.png", 20 * 1024 * 1024, max_bytes=15 * 1024 * 1024)

    # 4. Save and delete local asset
    dummy_bytes = b"QR_TEST_BYTES"
    stored_key = storage_service.save_asset(dummy_bytes, "unit_test_asset.png")
    assert stored_key is not None
    read_bytes = storage_service.read_asset(stored_key)
    assert read_bytes == dummy_bytes

    deleted = storage_service.delete_asset(stored_key)
    assert deleted is True
    assert storage_service.read_asset(stored_key) is None


