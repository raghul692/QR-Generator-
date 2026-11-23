"""
QRMaster Pro — Phase 2 Endpoints & Features Verification Suite.

Tests:
1. LandingPage CRUD (/api/v1/landing-pages) and public view (/p/{slug})
2. DigitalMenu CRUD (/api/v1/menus) and public view (/m/{id})
3. vCard RFC 6350 / v3.0 generator, parser, and API endpoints
4. Dynamic QR UTM attribution pass-through
5. Dynamic QR max scans deactivation and HTTP 410 expiration
6. Dynamic QR retargeting pixel interstitial page (Meta Pixel & Google Tag)
"""
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import DynamicQR, LandingPage, DigitalMenu
from app.services.vcard_service import vcard_service


def test_landing_page_crud_and_public_view(client: TestClient, db_session: Session):
    """Test full CRUD lifecycle for LandingPage and public rendering under /p/{slug}."""
    # 1. Create
    payload = {
        "title": "Jane Doe Creative Studio",
        "slug": "jane-doe-studio",
        "theme": "dark",
        "headline": "Award-Winning Product Design & Strategy",
        "description": "Crafting bespoke digital interfaces and design systems.",
        "button_text": "Book Consultation",
        "button_url": "https://example.com/book",
        "social_links": [
            {"platform": "twitter", "label": "Twitter", "url": "https://twitter.com/janedoe"},
            {"platform": "github", "label": "GitHub", "url": "https://github.com/janedoe"},
        ],
        "is_published": True,
    }
    create_res = client.post("/api/v1/landing-pages", json=payload)
    assert create_res.status_code == 201, create_res.text
    page_data = create_res.json()
    assert page_data["title"] == payload["title"]
    assert page_data["slug"] == "jane-doe-studio"
    assert page_data["is_published"] is True
    page_id = page_data["id"]

    # 2. List
    list_res = client.get("/api/v1/landing-pages")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(item["id"] == page_id for item in items)

    # 3. Read
    get_res = client.get(f"/api/v1/landing-pages/{page_id}")
    assert get_res.status_code == 200
    assert get_res.json()["headline"] == payload["headline"]

    # 4. Update
    update_res = client.put(
        f"/api/v1/landing-pages/{page_id}",
        json={"title": "Jane Doe Studio & Lab", "button_text": "Contact Us Now"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Jane Doe Studio & Lab"
    assert update_res.json()["button_text"] == "Contact Us Now"

    # 5. Public /p/{slug} - HTML view
    public_html_res = client.get("/p/jane-doe-studio", headers={"Accept": "text/html"})
    assert public_html_res.status_code == 200
    assert "text/html" in public_html_res.headers["content-type"]
    assert "Jane Doe Studio & Lab" in public_html_res.text
    assert "Contact Us Now" in public_html_res.text
    assert "Book Consultation" not in public_html_res.text

    # 6. Public /p/{slug} - JSON view
    public_json_res = client.get("/p/jane-doe-studio", headers={"Accept": "application/json"})
    assert public_json_res.status_code == 200
    assert public_json_res.json()["title"] == "Jane Doe Studio & Lab"

    # 7. Delete
    del_res = client.delete(f"/api/v1/landing-pages/{page_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Confirm 404 after deletion
    assert client.get(f"/api/v1/landing-pages/{page_id}").status_code == 404
    assert client.get("/p/jane-doe-studio").status_code == 404


def test_digital_menu_crud_and_public_view(client: TestClient, db_session: Session):
    """Test full CRUD lifecycle for DigitalMenu and public rendering under /m/{id}."""
    # 1. Create
    payload = {
        "title": "Bistro Deluxe",
        "description": "Artisanal bakery and farm-to-table lunch specialties.",
        "currency": "EUR",
        "sections": [
            {
                "title": "Appetizers",
                "items": [
                    {
                        "name": "Truffle Bruschetta",
                        "price": "9.50",
                        "description": "Grilled sourdough with black truffle and burrata.",
                        "dietary_tags": ["Vegetarian"],
                    }
                ],
            },
            {
                "title": "Main Courses",
                "items": [
                    {
                        "name": "Wild Mushroom Risotto",
                        "price": "18.00",
                        "description": "Arborio rice, porcini mushrooms, aged parmesan.",
                        "dietary_tags": ["GF", "Vegetarian"],
                    }
                ],
            },
        ],
        "is_active": True,
    }
    create_res = client.post("/api/v1/menus", json=payload)
    assert create_res.status_code == 201, create_res.text
    menu_data = create_res.json()
    assert menu_data["title"] == payload["title"]
    assert menu_data["currency"] == "EUR"
    menu_id = menu_data["id"]

    # 2. List
    list_res = client.get("/api/v1/menus")
    assert list_res.status_code == 200
    assert any(m["id"] == menu_id for m in list_res.json())

    # 3. Read
    get_res = client.get(f"/api/v1/menus/{menu_id}")
    assert get_res.status_code == 200
    assert get_res.json()["currency"] == "EUR"

    # 4. Update
    upd_res = client.put(
        f"/api/v1/menus/{menu_id}",
        json={"title": "Bistro Deluxe & Wine Bar"},
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["title"] == "Bistro Deluxe & Wine Bar"

    # 5. Public /m/{id} - HTML view
    pub_html_res = client.get(f"/m/{menu_id}", headers={"Accept": "text/html"})
    assert pub_html_res.status_code == 200
    assert "text/html" in pub_html_res.headers["content-type"]
    assert "Bistro Deluxe & Wine Bar" in pub_html_res.text
    assert "Truffle Bruschetta" in pub_html_res.text
    assert "Wild Mushroom Risotto" in pub_html_res.text
    assert "EUR" in pub_html_res.text

    # 6. Public /m/{id} - JSON view
    pub_json_res = client.get(f"/m/{menu_id}", headers={"Accept": "application/json"})
    assert pub_json_res.status_code == 200
    assert pub_json_res.json()["title"] == "Bistro Deluxe & Wine Bar"

    # 7. Delete
    del_res = client.delete(f"/api/v1/menus/{menu_id}")
    assert del_res.status_code == 200
    assert client.get(f"/api/v1/menus/{menu_id}").status_code == 404
    assert client.get(f"/m/{menu_id}").status_code == 404


def test_vcard_service_and_api(client: TestClient):
    """Test RFC 6350 / v3.0 generator and parser service and router endpoints."""
    contact_data = {
        "first_name": "Alexander",
        "last_name": "Hamilton",
        "organization": "Treasury Department",
        "title": "Secretary of the Treasury",
        "phone": "+1-555-1776-01",
        "work_phone": "+1-555-1776-02",
        "email": "ahamilton@treasury.gov",
        "work_email": "secretary@treasury.gov",
        "url": "https://treasury.gov",
        "street": "1500 Pennsylvania Ave NW",
        "city": "Washington",
        "state": "DC",
        "postal_code": "20220",
        "country": "USA",
        "note": "First Secretary of the US Treasury.",
        "social_links": {
            "linkedin": "https://linkedin.com/in/ahamilton",
            "twitter": "https://twitter.com/ahamilton",
        },
    }

    # 1. Direct Service Generation & Parsing
    vcf = vcard_service.generate(contact_data)
    assert "BEGIN:VCARD" in vcf
    assert "VERSION:3.0" in vcf
    assert "N:Hamilton;Alexander;;;" in vcf
    assert "FN:Alexander Hamilton" in vcf
    assert "ORG:Treasury Department" in vcf
    assert "TITLE:Secretary of the Treasury" in vcf
    assert "TEL;TYPE=CELL,VOICE:+1-555-1776-01" in vcf
    assert "EMAIL;TYPE=INTERNET,PREF:ahamilton@treasury.gov" in vcf
    assert "1500 Pennsylvania Ave NW" in vcf
    assert "END:VCARD" in vcf

    # 2. Round-trip parse
    parsed = vcard_service.parse(vcf)
    assert parsed["first_name"] == "Alexander"
    assert parsed["last_name"] == "Hamilton"
    assert parsed["organization"] == "Treasury Department"
    assert parsed["phone"] == "+1-555-1776-01"
    assert parsed["email"] == "ahamilton@treasury.gov"
    assert "Washington" in parsed["city"]
    assert parsed["postal_code"] == "20220"

    # 3. API endpoint /api/v1/vcard/generate
    gen_res = client.post("/api/v1/vcard/generate", json=contact_data)
    assert gen_res.status_code == 200
    gen_json = gen_res.json()
    assert "BEGIN:VCARD" in gen_json["vcf"]
    assert gen_json["filename"] == "Alexander_Hamilton.vcf"

    # 4. API endpoint /api/v1/vcard/download
    dl_res = client.post("/api/v1/vcard/download", json=contact_data)
    assert dl_res.status_code == 200
    assert "text/vcard" in dl_res.headers["content-type"]
    assert 'attachment; filename="Alexander_Hamilton.vcf"' in dl_res.headers["content-disposition"]
    assert b"BEGIN:VCARD" in dl_res.content

    # 5. API endpoint /api/v1/vcard/parse
    parse_res = client.post("/api/v1/vcard/parse", json={"vcf": vcf})
    assert parse_res.status_code == 200
    assert parse_res.json()["first_name"] == "Alexander"


def test_utm_passthrough(client: TestClient, db_session: Session):
    """Test UTM parameter preservation and pass-through on dynamic QR redirection."""
    # Create dynamic QR with UTM parameters
    create_res = client.post(
        "/api/v1/dynamic",
        json={
            "title": "Summer Campaign Link",
            "target_url": "https://example.com/shop?store=ny",
            "utm_source": "newsletter",
            "utm_medium": "email",
            "utm_campaign": "summer_promo_2026",
        },
    )
    assert create_res.status_code == 201
    data = create_res.json()
    short_code = data["short_code"]

    # Scan the dynamic QR link
    res = client.get(f"/r/{short_code}", follow_redirects=False)
    assert res.status_code == 307
    redirect_location = res.headers["location"]

    # Verify query params
    assert "store=ny" in redirect_location
    assert "utm_source=newsletter" in redirect_location
    assert "utm_medium=email" in redirect_location
    assert "utm_campaign=summer_promo_2026" in redirect_location


def test_max_scans_expiration(client: TestClient, db_session: Session):
    """Test that reaching max_scans deactivates the dynamic QR and returns HTTP 410."""
    # Create dynamic QR configured with max_scans = 2
    create_res = client.post(
        "/api/v1/dynamic",
        json={
            "title": "Limited 2-Scan Coupon",
            "target_url": "https://example.com/vip-coupon",
            "max_scans": 2,
        },
    )
    assert create_res.status_code == 201
    short_code = create_res.json()["short_code"]
    dynamic_id = create_res.json()["id"]

    # 1st scan - should succeed
    res1 = client.get(f"/r/{short_code}", follow_redirects=False)
    assert res1.status_code == 307

    # 2nd scan - should succeed and trip the max_scans limit
    res2 = client.get(f"/r/{short_code}", follow_redirects=False)
    assert res2.status_code == 307

    # Verify database state after 2nd scan
    dyn = db_session.query(DynamicQR).filter(DynamicQR.id == dynamic_id).first()
    assert dyn.scan_count == 2
    assert dyn.is_active is False

    # 3rd scan - should return HTTP 410 (Gone / Expired)
    res3 = client.get(f"/r/{short_code}", follow_redirects=False)
    assert res3.status_code == 410
    assert "maximum scan limit" in res3.text or "Expired" in res3.text


def test_retargeting_pixel_interstitial(client: TestClient, db_session: Session):
    """Test that configured Meta Pixel and Google Tag trigger interstitial tracking page."""
    create_res = client.post(
        "/api/v1/dynamic",
        json={
            "title": "Pixel Tracked QR",
            "target_url": "https://example.com/product/123",
            "meta_pixel_id": "9876543210",
            "google_tag_id": "G-TESTPIXEL123",
        },
    )
    assert create_res.status_code == 201
    short_code = create_res.json()["short_code"]

    # Request the redirect
    res = client.get(f"/r/{short_code}", follow_redirects=False)
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "fbq('init', '9876543210')" in res.text
    assert "gtag('config', 'G-TESTPIXEL123')" in res.text
    assert "https://example.com/product/123" in res.text
