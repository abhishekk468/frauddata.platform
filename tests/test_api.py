from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_drain_transfer_scores_higher_than_small_transfer():
    risky = {
        "step": 10,
        "txn_type": "TRANSFER",
        "amount": 500000,
        "oldbalance_org": 500000,
        "oldbalance_dest": 0,
        "dest_prev_txn_count": 0,
    }
    safe = {
        "step": 10,
        "txn_type": "TRANSFER",
        "amount": 100,
        "oldbalance_org": 90000,
        "oldbalance_dest": 5000,
        "dest_prev_txn_count": 3,
    }
    risky_probability = client.post("/predict", json=risky).json()["fraud_probability"]
    safe_probability = client.post("/predict", json=safe).json()["fraud_probability"]
    assert risky_probability > safe_probability


def test_rejects_payment_type():
    invalid = {
        "step": 10,
        "txn_type": "PAYMENT",
        "amount": 1,
        "oldbalance_org": 1,
        "oldbalance_dest": 1,
        "dest_prev_txn_count": 0,
    }
    assert client.post("/predict", json=invalid).status_code == 422
