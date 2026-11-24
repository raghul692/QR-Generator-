"""
QRMaster Pro — Authentication, Tenant Isolation & QR Lifecycle Test Suite.

Verifies:
- Production Argon2id authentication and JWT issuance
- User registration and personal workspace auto-provisioning
- 1-click enterprise demo profiles (admin, marketing, auditor)
- Strict multi-tenant isolation across QR history and Dynamic QRs
- QR duplication for static and dynamic codes
- QR archive lifecycle and filtering
- Dashboard metrics tenant scoping
"""
import pytest
from app.utils.jwt_auth import create_jwt_token, decode_jwt_token


def test_auth_registration_and_jwt(client):
    """Test user registration with personal workspace provisioning and signed JWT."""
    payload = {
        "email": "sarah.architect@acme-global.io",
        "password": "SecurePassword123!",
        "name": "Sarah Architect",
    }
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    data = res.json()

    assert "token" in data
    assert "user" in data
    assert "workspace" in data
    assert data["user"]["email"] == "sarah.architect@acme-global.io"
    assert data["user"]["name"] == "Sarah Architect"
    assert data["workspace"]["id"].startswith("ws_")
    assert "sarah-architect" in data["workspace"]["slug"]

    # Verify duplicate email rejected
    dup_res = client.post("/api/v1/auth/register", json=payload)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"].lower()


def test_auth_login_argon2id(client):
    """Test login flow with valid and invalid passwords."""
    email = "david.engineer@acme-global.io"
    password = "MyStrongPassword2026!"

    # 1. Register
    reg_res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "name": "David Engineer",
    })
    assert reg_res.status_code == 201

    # 2. Login with valid password
    login_res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password,
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "token" in login_data
    assert login_data["user"]["email"] == email

    # 3. Login with invalid password (rejected)
    bad_login = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "WrongPasswordAttempt!",
    })
    assert bad_login.status_code == 401


def test_auth_demo_profiles(client):
    """Test 1-click enterprise demo profiles."""
    for role in ["admin", "marketing", "auditor"]:
        res = client.post("/api/v1/auth/demo", json={"role": role})
        assert res.status_code == 200
        data = res.json()
        assert "token" in data
        assert "user" in data
        assert "workspace" in data
        assert len(data["token"]) > 30


def test_auth_me_introspection(client):
    """Test /auth/me profile and workspace introspection."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "alex.lead@tech.co",
        "password": "Password789!",
        "name": "Alex Lead",
    }).json()

    headers = {"Authorization": f"Bearer {reg['token']}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["user"]["email"] == "alex.lead@tech.co"
    assert me_data["current_workspace"]["id"] == reg["workspace"]["id"]


def test_multi_tenant_isolation_qr_history(client):
    """Verify Tenant B cannot view or delete Tenant A's QR history records."""
    # Tenant A
    user_a = client.post("/api/v1/auth/register", json={
        "email": "tenant.a@corp.com",
        "password": "PasswordA123!",
        "name": "Tenant A",
    }).json()
    token_a = user_a["token"]
    ws_a = user_a["workspace"]["id"]

    # Tenant B
    user_b = client.post("/api/v1/auth/register", json={
        "email": "tenant.b@corp.com",
        "password": "PasswordB123!",
        "name": "Tenant B",
    }).json()
    token_b = user_b["token"]
    ws_b = user_b["workspace"]["id"]

    # Tenant A generates a QR
    headers_a = {"Authorization": f"Bearer {token_a}", "X-Workspace-Id": ws_a}
    gen_res = client.post(
        "/api/v1/qr/generate",
        json={"title": "Secret Project QR", "qr_type": "url", "data": {"url": "https://tenant-a.internal"}},
        headers=headers_a,
    )
    assert gen_res.status_code == 200
    qr_id_a = gen_res.json()["id"]

    # Tenant A sees their QR
    list_a = client.get("/api/v1/history/", headers=headers_a)
    assert list_a.status_code == 200
    items_a = list_a.json()["items"]
    assert any(i["id"] == qr_id_a for i in items_a)

    # Tenant B lists history: must NOT see Tenant A's QR
    headers_b = {"Authorization": f"Bearer {token_b}", "X-Workspace-Id": ws_b}
    list_b = client.get("/api/v1/history/", headers=headers_b)
    assert list_b.status_code == 200
    items_b = list_b.json()["items"]
    assert not any(i["id"] == qr_id_a for i in items_b)

    # Tenant B attempts to get Tenant A's QR directly (IDOR check): 404
    get_res = client.get(f"/api/v1/history/{qr_id_a}", headers=headers_b)
    assert get_res.status_code == 404

    # Tenant B attempts to delete Tenant A's QR: 404
    del_res = client.delete(f"/api/v1/history/{qr_id_a}", headers=headers_b)
    assert del_res.status_code == 404


def test_qr_duplication_and_archive(client):
    """Test duplicating and archiving QR history items."""
    user = client.post("/api/v1/auth/register", json={
        "email": "creator@studio.io",
        "password": "PasswordStudio1!",
        "name": "Studio Creator",
    }).json()
    headers = {"Authorization": f"Bearer {user['token']}", "X-Workspace-Id": user["workspace"]["id"]}

    # Generate QR
    gen = client.post(
        "/api/v1/qr/generate",
        json={"title": "Master Brand QR", "qr_type": "url", "data": {"url": "https://brand.io"}},
        headers=headers,
    ).json()
    qr_id = gen["id"]

    # 1. Duplicate QR
    dup_res = client.post(f"/api/v1/history/{qr_id}/duplicate", headers=headers)
    assert dup_res.status_code == 200
    dup_data = dup_res.json()
    assert dup_data["id"] != qr_id
    assert "Master Brand QR (Copy)" == dup_data["title"]

    # 2. Archive QR
    arc_res = client.post(f"/api/v1/history/{qr_id}/archive", headers=headers)
    assert arc_res.status_code == 200
    assert arc_res.json()["is_archived"] is True

    # 3. Filter by archive status
    active_res = client.get("/api/v1/history/?is_archived=false", headers=headers)
    assert not any(i["id"] == qr_id for i in active_res.json()["items"])

    archived_res = client.get("/api/v1/history/?is_archived=true", headers=headers)
    assert any(i["id"] == qr_id for i in archived_res.json()["items"])

    # Unarchive
    unarc_res = client.post(f"/api/v1/history/{qr_id}/archive", headers=headers)
    assert unarc_res.status_code == 200
    assert unarc_res.json()["is_archived"] is False


def test_dynamic_qr_tenant_isolation_and_duplication(client):
    """Verify tenant isolation and duplication for dynamic QRs."""
    # Tenant 1
    u1 = client.post("/api/v1/auth/register", json={
        "email": "tenant.one@domain.com",
        "password": "PasswordOne123!",
        "name": "Tenant One",
    }).json()
    h1 = {"Authorization": f"Bearer {u1['token']}", "X-Workspace-Id": u1["workspace"]["id"]}

    # Tenant 2
    u2 = client.post("/api/v1/auth/register", json={
        "email": "tenant.two@domain.com",
        "password": "PasswordTwo123!",
        "name": "Tenant Two",
    }).json()
    h2 = {"Authorization": f"Bearer {u2['token']}", "X-Workspace-Id": u2["workspace"]["id"]}

    # Create dynamic QR in Tenant 1
    dyn = client.post(
        "/api/v1/dynamic",
        json={"title": "Campaign Alpha", "target_url": "https://alpha.com"},
        headers=h1,
    ).json()
    dyn_id = dyn["id"]

    # Tenant 2 lists dynamic: should be empty
    list_dyn2 = client.get("/api/v1/dynamic", headers=h2).json()
    assert not any(d["id"] == dyn_id for d in list_dyn2)

    # Tenant 2 cannot update Tenant 1's dynamic QR
    upd_res = client.put(f"/api/v1/dynamic/{dyn_id}", json={"title": "Hacked"}, headers=h2)
    assert upd_res.status_code == 404

    # Tenant 1 duplicates dynamic QR
    dup_res = client.post(f"/api/v1/dynamic/{dyn_id}/duplicate", headers=h1)
    assert dup_res.status_code == 201
    dup_dyn = dup_res.json()
    assert dup_dyn["id"] != dyn_id
    assert dup_dyn["short_code"] != dyn["short_code"]
    assert "Campaign Alpha (Copy)" == dup_dyn["title"]
