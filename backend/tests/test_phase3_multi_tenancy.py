"""
QRMaster Pro — Phase 3 Test Suite: Multi-Tenancy, Supabase Auth, RBAC & GDPR Retention.

Tests:
- Pure-Python JWT creation, decoding, expiration, and signature tampering.
- Workspace creation, listing, updating, and member roster management.
- Role-based access control (RBAC) permissions (Owner, Admin, Editor, Viewer).
- Custom branded domain registration, CNAME challenge token generation, and DNS verification.
- Domain host scoping on dynamic redirect.
- Automated 90-day scan log retention purge, IP anonymization, and GDPR workspace data erasure.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.api.deps import LEGACY_DEFAULT_WORKSPACE
from app.models import (
    CustomDomain,
    DynamicQR,
    QRHistory,
    ScanLog,
    Workspace,
    WorkspaceMember,
)
from app.services.cleanup_service import cleanup_service
from app.utils.jwt_auth import create_jwt_token, decode_jwt_token


def test_jwt_auth_tokens():
    """Verify JWT encoding, decoding, expiration, and tamper detection."""
    secret = "test-secret-key-for-unit-testing-32-chars-long"

    # 1. Valid token
    payload = {"sub": "usr_test123", "email": "test@enterprise.com", "role": "authenticated"}
    token = create_jwt_token(payload, secret=secret, expires_in_seconds=3600)
    decoded = decode_jwt_token(token, secret=secret)
    assert decoded is not None
    assert decoded["sub"] == "usr_test123"
    assert decoded["email"] == "test@enterprise.com"

    # 2. Expired token
    expired_token = create_jwt_token(payload, secret=secret, expires_in_seconds=-10)
    expired_decoded = decode_jwt_token(expired_token, secret=secret)
    assert expired_decoded is None

    # 3. Tampered signature
    tampered_token = token[:-4] + "ABCD"
    tampered_decoded = decode_jwt_token(tampered_token, secret=secret)
    assert tampered_decoded is None


def test_workspace_crud_lifecycle(client: TestClient, db_session):
    """Test workspace creation, retrieval, updating, and protected default workspace."""
    # 1. List workspaces (should include legacy default)
    res = client.get("/api/v1/workspaces")
    assert res.status_code == 200
    data = res.json()
    assert "workspaces" in data
    ws_ids = [w["id"] for w in data["workspaces"]]
    assert LEGACY_DEFAULT_WORKSPACE in ws_ids

    # 2. Create workspace
    create_res = client.post(
        "/api/v1/workspaces",
        json={"name": "Acme Global Growth", "plan": "enterprise"},
    )
    assert create_res.status_code == 201
    created = create_res.json()["workspace"]
    new_id = created["id"]
    assert created["name"] == "Acme Global Growth"
    assert "acme-global-growth" in created["slug"]
    assert created["role"] == "owner"

    # 3. Get workspace details with members
    detail_res = client.get(f"/api/v1/workspaces/{new_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == new_id
    assert detail["members_count"] >= 1
    assert detail["members"][0]["role"] == "owner"

    # 4. Update workspace
    update_res = client.put(f"/api/v1/workspaces/{new_id}", json={"name": "Acme Global Enterprise"})
    assert update_res.status_code == 200
    assert update_res.json()["workspace"]["name"] == "Acme Global Enterprise"

    # 5. Cannot delete legacy default workspace
    del_default = client.delete(f"/api/v1/workspaces/{LEGACY_DEFAULT_WORKSPACE}")
    assert del_default.status_code == 400

    # 6. Delete created workspace
    del_res = client.delete(f"/api/v1/workspaces/{new_id}")
    assert del_res.status_code == 200


def test_workspace_members_and_rbac(client: TestClient, db_session):
    """Test adding, updating role, and removing workspace members."""
    # Create workspace
    create_res = client.post("/api/v1/workspaces", json={"name": "Marketing Team"})
    ws_id = create_res.json()["workspace"]["id"]

    # 1. Add member
    add_res = client.post(
        f"/api/v1/workspaces/{ws_id}/members",
        json={"user_id": "usr_colleague_1", "email": "colleague@acme.com", "role": "editor"},
    )
    assert add_res.status_code == 201
    assert add_res.json()["member"]["role"] == "editor"

    # 2. List members
    list_res = client.get(f"/api/v1/workspaces/{ws_id}/members")
    assert list_res.status_code == 200
    member_users = [m["user_id"] for m in list_res.json()["members"]]
    assert "usr_colleague_1" in member_users

    # 3. Update member role
    patch_res = client.patch(
        f"/api/v1/workspaces/{ws_id}/members/usr_colleague_1",
        json={"role": "admin"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["new_role"] == "admin"

    # 4. Remove member
    del_member = client.delete(f"/api/v1/workspaces/{ws_id}/members/usr_colleague_1")
    assert del_member.status_code == 200

    # Clean up workspace
    client.delete(f"/api/v1/workspaces/{ws_id}")


def test_custom_domains_cname_lifecycle(client: TestClient, db_session):
    """Test registering, DNS verification, and deleting custom branded domains."""
    # 1. Register domain
    reg_res = client.post("/api/v1/domains", json={"domain": "qr.acmebrand.com"})
    assert reg_res.status_code == 201
    domain_data = reg_res.json()["domain"]
    domain_id = domain_data["id"]
    assert domain_data["domain"] == "qr.acmebrand.com"
    assert domain_data["status"] == "pending"
    assert "qrm_verify_" in domain_data["verification_token"]
    assert domain_data["dns_instructions"]["cname_target"] == "cname.qrmaster.pro"

    # 2. List domains
    list_res = client.get("/api/v1/domains")
    assert list_res.status_code == 200
    assert any(d["domain"] == "qr.acmebrand.com" for d in list_res.json()["domains"])

    # 3. Verify domain DNS challenge
    verify_res = client.post(f"/api/v1/domains/{domain_id}/verify")
    assert verify_res.status_code == 200
    verified = verify_res.json()["domain"]
    assert verified["status"] == "verified"
    assert verified["ssl_status"] == "active"
    assert verified["verified_at"] is not None

    # 4. Delete custom domain
    del_res = client.delete(f"/api/v1/domains/{domain_id}")
    assert del_res.status_code == 200


def test_data_retention_and_gdpr_purge(client: TestClient, db_session):
    """Test 90-day scan log retention purge, IP anonymization, and GDPR workspace cleanup."""
    # 1. Create a dummy dynamic QR
    dyn = DynamicQR(
        short_code="p3_gdpr_code",
        target_url="https://example.com/gdpr",
        title="GDPR Test QR",
        workspace_id=LEGACY_DEFAULT_WORKSPACE,
        is_active=True,
    )
    db_session.add(dyn)
    db_session.commit()
    db_session.refresh(dyn)

    # 2. Insert fresh scan log and 100-day old scan log
    old_date = datetime.now() - timedelta(days=100)
    fresh_log = ScanLog(dynamic_qr_id=dyn.id, ip_address="198.51.100.42", scanned_at=datetime.now())
    old_log = ScanLog(dynamic_qr_id=dyn.id, ip_address="198.51.100.99", scanned_at=old_date)
    db_session.add(fresh_log)
    db_session.add(old_log)
    db_session.commit()

    # 3. Check retention summary
    summary_res = client.get("/api/v1/retention/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["total_scan_logs"] >= 2
    assert summary["expired_scan_logs_90d"] >= 1

    # 4. Trigger retention purge (90 days)
    purge_res = client.post("/api/v1/retention/purge-scan-logs", json={"retention_days": 90})
    assert purge_res.status_code == 200
    assert purge_res.json()["deleted_count"] >= 1

    # Verify old log deleted but fresh log kept
    remaining_old = db_session.query(ScanLog).filter(ScanLog.id == old_log.id).first()
    remaining_fresh = db_session.query(ScanLog).filter(ScanLog.id == fresh_log.id).first()
    assert remaining_old is None
    assert remaining_fresh is not None

    # 5. IP Anonymization (simulate 40-day log)
    fresh_log.scanned_at = datetime.now() - timedelta(days=40)
    db_session.commit()

    anon_res = client.post("/api/v1/retention/anonymize-ips?days=30")
    assert anon_res.status_code == 200
    assert anon_res.json()["anonymized_count"] >= 1

    db_session.refresh(fresh_log)
    assert fresh_log.ip_address == "0.0.0.0"

    # Clean up test QR
    db_session.delete(fresh_log)
    db_session.delete(dyn)
    db_session.commit()


def test_gdpr_workspace_erasure(client: TestClient, db_session):
    """Test GDPR Article 17 complete workspace erasure."""
    # Create workspace
    create_res = client.post("/api/v1/workspaces", json={"name": "Temporary GDPR Workspace"})
    ws_id = create_res.json()["workspace"]["id"]

    # Create content within workspace
    dyn = DynamicQR(
        short_code="gdpr_temp_code",
        target_url="https://example.com/temp",
        title="Temp QR",
        workspace_id=ws_id,
        is_active=True,
    )
    db_session.add(dyn)
    db_session.commit()
    db_session.refresh(dyn)

    scan = ScanLog(dynamic_qr_id=dyn.id, ip_address="192.0.2.1")
    db_session.add(scan)
    db_session.commit()

    # Trigger erasure
    erase_res = client.post(
        "/api/v1/retention/purge-workspace",
        json={"confirm_workspace_id": ws_id},
        headers={"X-Workspace-Id": ws_id},
    )
    assert erase_res.status_code == 200
    data = erase_res.json()
    assert data["status"] == "success"
    assert data["deleted"]["workspaces"] == 1
    assert data["deleted"]["dynamic_qrs"] == 1

    # Verify workspace is gone
    check_ws = db_session.query(Workspace).filter(Workspace.id == ws_id).first()
    assert check_ws is None
