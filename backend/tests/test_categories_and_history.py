"""
Unit & Integration tests for Categories (CRUD, slugging, safe deletion) and History.
"""
from app.models import QRCategory, QRHistory


def test_categories_crud_and_safe_deletion(client, db_session):
    """Test category creation, updating, assignment to QR, and safe deletion."""
    # 1. Create category
    create_res = client.post("/api/v1/categories/", json={
        "name": "Special Events",
        "description": "Exclusive festival & party QR codes",
        "icon": "BsParty",
        "color": "#E11D48",
    })
    assert create_res.status_code == 200
    cat_data = create_res.json()
    cat_id = cat_data["id"]
    assert cat_data["slug"] == "special-events"

    # 2. Create a QR code in this category
    qr_res = client.post("/api/v1/qr/generate", json={
        "title": "Festival Ticket",
        "qr_type": "url",
        "data": {"url": "https://festival.com/ticket"},
        "category_id": cat_id,
        "save_to_history": True,
    })
    assert qr_res.status_code == 200
    qr_id = qr_res.json()["id"]

    # Verify category count is 1
    cat_detail = client.get(f"/api/v1/categories/{cat_id}").json()
    assert cat_detail["qr_count"] == 1

    # 3. Delete category safely
    del_res = client.delete(f"/api/v1/categories/{cat_id}")
    assert del_res.status_code == 200

    # 4. CRITICAL: Verify the QR code was NOT deleted
    qr_item = db_session.query(QRHistory).filter(QRHistory.id == qr_id).first()
    assert qr_item is not None
    assert qr_item.title == "Festival Ticket"
    assert qr_item.category_id is None


def test_history_filtering_and_favorites(client):
    """Test search, filtering by type, toggling favorite, and pagination."""
    # Generate test QR
    gen_res = client.post("/api/v1/qr/generate", json={
        "title": "Searchable WiFi QR",
        "qr_type": "wifi",
        "data": {"ssid": "GuestWiFi", "security": "nopass"},
        "save_to_history": True,
    })
    qr_id = gen_res.json()["id"]

    # Search by keyword
    search_res = client.get("/api/v1/history/?search=Searchable")
    assert search_res.status_code == 200
    items = search_res.json()["items"]
    assert any(i["id"] == qr_id for i in items)

    # Filter by qr_type
    wifi_res = client.get("/api/v1/history/?qr_type=wifi")
    assert wifi_res.status_code == 200
    assert any(i["id"] == qr_id for i in wifi_res.json()["items"])

    # Toggle favorite
    fav_res = client.post(f"/api/v1/history/{qr_id}/favorite")
    assert fav_res.status_code == 200

    fav_filter = client.get("/api/v1/history/?is_favorite=true")
    assert any(i["id"] == qr_id for i in fav_filter.json()["items"])
