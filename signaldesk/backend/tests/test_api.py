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


def test_sla_risk_filter_returns_only_at_risk_records():
    response=client.get("/tickets",params={"sla_state":"at_risk"})
    assert response.status_code==200
    assert response.json()
    assert all(ticket["sla_state"]=="at_risk" for ticket in response.json())

def test_invalid_sla_filter_is_rejected():
    response=client.get("/tickets",params={"sla_state":"urgent"})
    assert response.status_code==422
