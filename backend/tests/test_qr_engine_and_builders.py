"""
Unit & Integration tests for QR Builders (all 31 types), Rendering, Formats, and Scanner.
"""
import pytest
from app.qr_engine.builders import registry
from app.qr_engine.scanner import scanner
from app.qr_engine.customization import QRCustomization
from app.qr_engine.renderer import renderer


# Test samples for all 31 supported QR types
QR_TYPE_SAMPLES = [
    ("text", {"text": "Hello World"}),
    ("url", {"url": "https://example.com"}),
    ("email", {"email": "test@example.com", "subject": "Hi", "body": "Hello"}),
    ("phone", {"phone": "+1234567890"}),
    ("sms", {"phone": "+1234567890", "message": "Test SMS"}),
    ("whatsapp", {"phone": "+1234567890", "message": "Test WhatsApp"}),
    ("telegram", {"username": "testuser"}),
    ("wifi", {"ssid": "HomeNet", "password": "pass", "security": "WPA", "hidden": False}),
    ("vcard", {"first_name": "Jane", "last_name": "Doe", "organization": "Acme", "email": "jane@acme.com"}),
    ("geo", {"latitude": "37.7749", "longitude": "-122.4194"}),
    ("google_maps", {"query": "San Francisco"}),
    ("facebook", {"username": "example"}),
    ("instagram", {"username": "example"}),
    ("linkedin", {"username": "example"}),
    ("github", {"username": "octocat"}),
    ("youtube", {"channel": "example"}),
    ("twitter", {"username": "example"}),
    ("upi", {"vpa": "user@okaxis", "payee_name": "John Doe", "amount": "100"}),
    ("google_pay", {"vpa": "user@okhdfcbank", "payee_name": "John Doe"}),
    ("phonepe", {"vpa": "user@ybl", "payee_name": "John Doe"}),
    ("paytm", {"vpa": "user@paytm", "payee_name": "John Doe"}),
    ("bitcoin", {"address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "amount": "0.01"}),
    ("ethereum", {"address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", "amount": "0.1"}),
    ("event", {"title": "Annual Gala", "location": "Hall A", "start_datetime": "20261201T180000"}),
    ("calendar", {"title": "Team Sync", "location": "Room 101"}),
    ("meeting", {"url": "https://meet.example.com/sync"}),
    ("zoom", {"url": "https://zoom.us/j/123456789"}),
    ("google_meet", {"url": "https://meet.google.com/abc-defg-hij"}),
    ("app_download", {"url": "https://apps.apple.com/app/id123"}),
    ("file_link", {"url": "https://drive.google.com/file/d/123"}),
    ("custom", {"data": "RAW_CUSTOM_PAYLOAD"}),
]


@pytest.mark.parametrize("qr_type,data", QR_TYPE_SAMPLES)
def test_all_31_builders(qr_type, data):
    """Verify that every single builder produces a valid non-empty payload string."""
    encoded = registry.build(qr_type, data)
    assert isinstance(encoded, str)
    assert len(encoded) > 0


def test_qr_preview_and_generate_api(client):
    """Test preview endpoint and full generate endpoint."""
    # Preview
    prev_res = client.post("/api/v1/qr/preview", json={
        "qr_type": "url",
        "data": {"url": "https://qrmaster.pro"},
        "customization": {"size": 300, "foreground_color": "#000000"}
    })
    assert prev_res.status_code == 200
    prev_data = prev_res.json()
    assert prev_data["encoded_data"] == "https://qrmaster.pro"
    assert prev_data["preview_base64"].startswith("data:image/png;base64,")

    # Generate and save
    gen_res = client.post("/api/v1/qr/generate", json={
        "title": "Production Website QR",
        "qr_type": "url",
        "data": {"url": "https://qrmaster.pro"},
        "save_to_history": True,
        "customization": {"size": 300, "qr_style": "rounded"}
    })
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    assert gen_data["id"] is not None
    assert gen_data["title"] == "Production Website QR"

    # Download in all supported formats
    qr_id = gen_data["id"]
    for fmt in ["png", "jpg", "svg", "pdf"]:
        dl_res = client.get(f"/api/v1/qr/download/{qr_id}?fmt={fmt}")
        assert dl_res.status_code == 200
        assert len(dl_res.content) > 0


def test_qr_scanner_workflow():
    """Render a QR code in memory and decode it with the scanner."""
    payload = "WIFI:T:WPA;S:OfficeNet;P:SecretPass;;"
    custom = QRCustomization(size=400, error_correction="H")
    img = renderer.render_image(payload, custom)
    img_bytes = renderer.to_bytes(img, fmt="PNG")

    results = scanner.scan_bytes(img_bytes)
    assert len(results) >= 1
    assert "OfficeNet" in results[0].data
    assert results[0].qr_type == "wifi"


def test_custom_eye_and_pupil_rendering():
    """Verify QR code renders properly with custom eye/pupil shapes and colors."""
    payload = "https://example.com/custom-eyes"
    custom = QRCustomization(
        size=400,
        error_correction="H",
        eye_style="circle",
        eye_color="#4f46e5",
        pupil_style="diamond",
        pupil_color="#10b981"
    )
    img = renderer.render_image(payload, custom)
    assert img.size[0] >= 350 and img.size[1] >= 350
    img_bytes = renderer.to_bytes(img, fmt="PNG")
    assert len(img_bytes) > 0


def test_frame_styles_rendering():
    """Verify that all frame styles render successfully with custom CTA text."""
    payload = "https://example.com/frames"
    for frame in ["simple", "rounded", "banner", "badge"]:
        custom = QRCustomization(
            size=400,
            frame_style=frame,
            frame_text="SCAN HERE",
            frame_color="#2563eb"
        )
        img = renderer.render_image(payload, custom)
        assert img is not None
        assert img.size[0] >= 400
        assert img.size[1] > 400  # Frame adds bottom CTA area


def test_export_formula_sanitization():
    """Verify CSV/Excel formula injection sanitization in export service."""
    from app.services.export_service import sanitize_export_cell

    dangerous_inputs = [
        "=SUM(A1:A10)",
        "+1+2",
        "-5+10",
        "@SUM(B1:B5)",
        "\tcmd|' /C calc'!A0",
        "\r=1+1",
    ]
    for val in dangerous_inputs:
        sanitized = sanitize_export_cell(val)
        assert sanitized.startswith("'"), f"Dangerous input {val} was not escaped with leading single quote"

    safe_inputs = ["Normal Text", "12345", "https://qrmaster.pro", "user@example.com"]
    for val in safe_inputs:
        assert sanitize_export_cell(val) == val

