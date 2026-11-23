"""
Unit & Integration tests for Dynamic QR Codes, Redirection, Argon2 Password Gates, and Scan Analytics.
"""
import hashlib
from datetime import datetime, timedelta
from app.models import DynamicQR, ScanLog
from app.services.dynamic_qr_service import dynamic_qr_service


def test_dynamic_qr_creation_and_redirection(client, db_session):
    """Test full dynamic QR creation, public short-code redirect, and scan logging."""
    create_res = client.post("/api/v1/dynamic", json={
        "title": "Summer Campaign",
        "target_url": "https://company.com/summer-sale",
    })
    assert create_res.status_code == 201
    data = create_res.json()
    assert "short_code" in data
    assert "redirect_url" in data
    assert data["target_url"] == "https://company.com/summer-sale"
    short_code = data["short_code"]
    dyn_id = data["id"]

    # Perform scan via public redirect
    redir_res = client.get(
        f"/r/{short_code}",
        headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"},
        follow_redirects=False,
    )
    assert redir_res.status_code == 307
    assert redir_res.headers["location"] == "https://company.com/summer-sale"

    # Verify scan count in DB
    dyn = db_session.query(DynamicQR).filter(DynamicQR.id == dyn_id).first()
    assert dyn.scan_count == 1

    # Verify analytics endpoint
    analytics_res = client.get(f"/api/v1/dynamic/{dyn_id}/analytics")
    assert analytics_res.status_code == 200
    analytics = analytics_res.json()
    assert analytics["total_scans"] == 1
    assert analytics["unique_scans"] >= 1
    devices = [d["device"] for d in analytics["devices"]]
    assert "Mobile" in devices


def test_password_protected_dynamic_qr(client, db_session):
    """Test Argon2 password gating, wrong password rejection, and correct unlock."""
    create_res = client.post("/api/v1/dynamic", json={
        "title": "Confidential Document",
        "target_url": "https://company.com/confidential",
        "password": "SuperSecretPassword123!",
    })
    assert create_res.status_code == 201
    data = create_res.json()
    short_code = data["short_code"]

    # Initial scan should show password prompt
    prompt_res = client.get(f"/r/{short_code}")
    assert prompt_res.status_code == 200
    assert "Password Protected" in prompt_res.text

    # Submit wrong password -> 401
    wrong_res = client.post(f"/r/{short_code}/unlock", data={"password": "WrongPassword"})
    assert wrong_res.status_code == 401
    assert "Incorrect Password" in wrong_res.text

    # Submit correct password -> 307 redirect
    correct_res = client.post(f"/r/{short_code}/unlock", data={"password": "SuperSecretPassword123!"}, follow_redirects=False)
    assert correct_res.status_code == 307
    assert correct_res.headers["location"] == "https://company.com/confidential"


def test_legacy_sha256_password_upgrade(db_session):
    """Test that legacy SHA-256 hashes are verified and upgraded to Argon2id."""
    raw_pass = "LegacyPass123"
    legacy_hash = hashlib.sha256(raw_pass.encode("utf-8")).hexdigest()

    dyn = DynamicQR(
        short_code="legacy1",
        target_url="https://example.com/legacy",
        title="Legacy QR",
        password_hash=legacy_hash,
        is_active=True,
    )
    db_session.add(dyn)
    db_session.commit()
    db_session.refresh(dyn)

    # Verify with automatic upgrade
    verified = dynamic_qr_service.verify_password(dyn, raw_pass, db=db_session)
    assert verified is True
    # Check that stored hash is now Argon2id
    assert dyn.password_hash.startswith("$argon2id$")


def test_expired_dynamic_qr(client, db_session):
    """Test that expired dynamic QR links return 410 Gone."""
    expired_time = (datetime.now() - timedelta(days=2)).isoformat()
    create_res = client.post("/api/v1/dynamic", json={
        "title": "Expired Promo",
        "target_url": "https://company.com/promo",
        "expires_at": expired_time,
    })
    assert create_res.status_code == 201
    short_code = create_res.json()["short_code"]

    scan_res = client.get(f"/r/{short_code}")
    assert scan_res.status_code == 410
    assert "Expired" in scan_res.text
