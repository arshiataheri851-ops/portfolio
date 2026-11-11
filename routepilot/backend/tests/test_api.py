from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    assert client.get("/health").json()["status"]=="ok"

def test_seeded_deliveries_are_readable():
    response=client.get("/deliveries")
    assert response.status_code==200
    assert any(row["id"]=="DL-2083" for row in response.json())

def test_delivery_note_discloses_preview_status():
    response=client.get("/deliveries/DL-2083/note")
    assert response.status_code==200
    assert response.json()["legal_validity"] is False
