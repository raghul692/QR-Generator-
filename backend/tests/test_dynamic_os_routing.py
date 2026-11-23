"""
Unit and Integration Tests for Dynamic OS Smart Routing and Open Redirect Defense.
"""
import pytest
from app.services.dynamic_qr_service import dynamic_qr_service

IPHONE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
)
ANDROID_UA = (
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
)
DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def test_dynamic_os_smart_routing(client):
    """Verify that dynamic redirects steer iOS, Android, and Desktop to configured targets."""
    # 1. Create dynamic QR with OS targets
    payload = {
        "title": "Multi-OS App Launch",
        "target_url": "https://myapp.com/download",
        "ios_target_url": "https://apps.apple.com/app/id123456789",
        "android_target_url": "https://play.google.com/store/apps/details?id=com.myapp",
    }
    create_res = client.post("/api/v1/dynamic", json=payload)
    assert create_res.status_code == 201
    dyn_data = create_res.json()
    short_code = dyn_data["short_code"]
    assert dyn_data["ios_target_url"] == payload["ios_target_url"]
    assert dyn_data["android_target_url"] == payload["android_target_url"]

    # 2. Test iOS redirect
    res_ios = client.get(f"/r/{short_code}", headers={"User-Agent": IPHONE_UA}, follow_redirects=False)
    assert res_ios.status_code == 307
    assert res_ios.headers["location"] == payload["ios_target_url"]

    # 3. Test Android redirect
    res_android = client.get(f"/r/{short_code}", headers={"User-Agent": ANDROID_UA}, follow_redirects=False)
    assert res_android.status_code == 307
    assert res_android.headers["location"] == payload["android_target_url"]

    # 4. Test Desktop / Web fallback
    res_desktop = client.get(f"/r/{short_code}", headers={"User-Agent": DESKTOP_UA}, follow_redirects=False)
    assert res_desktop.status_code == 307
    assert res_desktop.headers["location"] == payload["target_url"]


def test_open_redirect_defense(client, db_session):
    """Verify that unsafe protocol schemes and loopback addresses are blocked."""
    dyn = dynamic_qr_service.create_dynamic_qr(
        db=db_session,
        title="Unsafe Probe",
        target_url="http://127.0.0.1:8000/admin/secret",
    )
    res = client.get(f"/r/{dyn.short_code}", follow_redirects=False)
    assert res.status_code == 400
    assert "unsafe destination" in res.text.lower()
