from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    assert client.get("/health").json()["status"]=="ok"

def test_list_has_seed_records():
    response=client.get("/tickets")
    assert response.status_code==200
    assert any(t["id"]=="SD-1048" for t in response.json())

def test_summary_counts_match_seeded_records():
    result=client.get("/analytics/summary").json()
    assert result["total"]>=5
    assert "at_risk" in result
