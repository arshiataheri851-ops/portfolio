from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app, connect
from app.security import current_user

# Existing workflow tests run as a trusted fixture identity; auth rejection is tested separately.
app.dependency_overrides[current_user] = lambda: {
    'id': 'test-user', 'organization_id': 'test-org', 'email': 'tester@example.test', 'role': 'admin'
}

client = TestClient(app)

# Deterministic tenant fixture; CI intentionally has no bootstrap secrets.
with connect() as _db:
    _db.execute("INSERT OR IGNORE INTO organizations(id,name,created_at) VALUES('test-org','Test Org','2026-01-01T00:00:00+00:00')")
    _db.execute("INSERT OR IGNORE INTO vehicles(id,label,status,organization_id) VALUES('VAN-12','Van 12','on_route','test-org')")
    _db.execute("INSERT OR IGNORE INTO deliveries(id,recipient,address,route_id,vehicle_id,status,eta,created_at,organization_id) VALUES('DL-2083','Market Hall','Berlin Kreuzberg','R-204','VAN-12','delivered',NULL,'2026-01-01T00:00:00+00:00','test-org')")


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_seeded_deliveries_are_readable():
    response = client.get("/deliveries")
    assert response.status_code == 200
    assert any(row["id"] == "DL-2083" for row in response.json())


def test_delivery_note_discloses_preview_status():
    response = client.get("/deliveries/DL-2083/note")
    assert response.status_code == 200
    assert response.json()["legal_validity"] is False


def test_position_is_saved_and_returned_in_history():
    response = client.post("/vehicles/VAN-12/positions", json={"latitude": 52.52, "longitude": 13.405})
    assert response.status_code == 201
    history = client.get("/vehicles/VAN-12/positions")
    assert history.status_code == 200
    assert history.json()[0]["latitude"] == 52.52


def test_unknown_vehicle_is_rejected_for_delivery():
    response = client.post("/deliveries", json={
        "id": f"DL-{uuid4().hex[:10]}",
        "recipient": "Test recipient",
        "address": "Berlin Mitte",
        "route_id": "R-TEST",
        "vehicle_id": "NO-SUCH-VAN"
    })
    assert response.status_code == 422


def test_delivery_requires_proof_before_delivered_status():
    delivery_id = f"DL-{uuid4().hex[:10]}"
    created = client.post("/deliveries", json={
        "id": delivery_id,
        "recipient": "Test recipient",
        "address": "Berlin Mitte",
        "route_id": "R-TEST",
        "vehicle_id": "VAN-12"
    })
    assert created.status_code == 201
    blocked = client.patch(f"/deliveries/{delivery_id}/status", json={"status": "delivered"})
    assert blocked.status_code == 409
    proof = client.post(f"/deliveries/{delivery_id}/proof", json={
        "recipient_name": "Test receiver",
        "method": "manual",
        "note": "Test confirmation"
    })
    assert proof.status_code == 201
    assert client.get(f"/deliveries/{delivery_id}/proofs").json()
    allowed = client.patch(f"/deliveries/{delivery_id}/status", json={"status": "delivered"})
    assert allowed.status_code == 200

def test_readiness_checks_database():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_business_api_rejects_missing_authentication():
    override = app.dependency_overrides.pop(current_user, None)
    try:
        response = client.get("/deliveries")
        assert response.status_code == 401
    finally:
        if override is not None:
            app.dependency_overrides[current_user] = override
