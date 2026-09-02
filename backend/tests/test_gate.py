from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_catalog_feed():
    response = client.get("/api/catalog/semantic-feed?max_price=5000")
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] == 2

def test_spend_gate_approval():
    payload = {
        "mandate_id": "MANDATE-DEMO-001",
        "merchant_id": "MERCHANT-01",
        "items": [{"sku": "PROD-OFFICE-CHAIR-01", "quantity": 1, "unit_price": 3499.0}],
        "claimed_total": 3499.0,
        "reasoning_trace": "Legitimate purchase test"
    }
    response = client.post("/api/gate/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_approved"] is True
    assert data["status_code"] == "APPROVED"

def test_spend_gate_price_tampering():
    payload = {
        "mandate_id": "MANDATE-DEMO-001",
        "merchant_id": "MERCHANT-01",
        "items": [{"sku": "PROD-OFFICE-CHAIR-01", "quantity": 1, "unit_price": 3499.0}],
        "claimed_total": 500.0,  # Tampered total
        "reasoning_trace": "Simulated tampering attack"
    }
    response = client.post("/api/gate/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_approved"] is False
    assert data["status_code"] == "PRICE_MISMATCH"
    assert data["requires_human_fallback"] is True