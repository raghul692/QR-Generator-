"""
Unit & Integration tests for health probes and Developer API Key authentication.
"""
import pytest
from app.api.deps import verify_api_key
from app.models import APIKey


def test_health_endpoints(client):
    """Verify /health and /health/live."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "app" in data

    res_live = client.get("/health/live")
    assert res_live.status_code == 200
    assert res_live.json()["status"] == "live"


def test_health_readiness(client):
    """Verify /health/ready probe."""
    res = client.get("/health/ready")
    assert res.status_code in (200, 503)


def test_api_key_lifecycle_and_auth(client, db_session):
    """Test API key creation, header verification, listing, and revocation."""
    # 1. Create API key
    create_res = client.post("/api/v1/keys", json={"name": "Test Integration", "rate_limit": 500})
    assert create_res.status_code == 201
    key_data = create_res.json()
    assert "api_key" in key_data
    assert key_data["name"] == "Test Integration"
    full_key = key_data["api_key"]
    key_id = key_data["id"]

    # 2. List keys (full secret is never returned)
    list_res = client.get("/api/v1/keys")
    assert list_res.status_code == 200
    keys = list_res.json()
    found = [k for k in keys if k["id"] == key_id]
    assert len(found) == 1
    assert "api_key" not in found[0]

    # 3. Test verification dependency with valid key
    verified_key = verify_api_key(x_api_key=full_key, db=db_session)
    assert verified_key.id == key_id
    assert verified_key.is_active is True

    # 4. Test verification dependency with invalid key
    with pytest.raises(Exception):
        verify_api_key(x_api_key="invalid_fake_key_12345", db=db_session)

    # 5. Revoke key
    del_res = client.delete(f"/api/v1/keys/{key_id}")
    assert del_res.status_code == 200

    # 6. Verify revoked key is rejected
    with pytest.raises(Exception):
        verify_api_key(x_api_key=full_key, db=db_session)
