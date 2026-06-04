from fastapi.testclient import TestClient

from app.main import app


def test_analysis_api_lifecycle():
    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={
            "symbol": "000001",
            "start_date": "2024-01-01",
            "end_date": "2024-03-31",
            "horizon": "1m",
            "risk_preference": "balanced",
        },
    )
    assert response.status_code == 200
    run_id = response.json()["run_id"]

    snapshot = client.get(f"/api/analysis/{run_id}")
    assert snapshot.status_code == 200
    payload = snapshot.json()
    assert payload["run_id"] == run_id
    assert payload["status"] == "completed"
    assert payload["result"]["report"]["summary"]
