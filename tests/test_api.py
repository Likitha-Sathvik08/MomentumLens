from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.db.database import get_db

client = TestClient(app)

def override_get_db():
    from tests.conftest import test_db
    # This is a bit tricky with pytest fixtures, we'll just test the routes via Client
    pass


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_load_match_no_events():
    payload = {
        "match_id": "test_api_1",
        "home_team": "Team A",
        "away_team": "Team B"
    }
    response = client.post("/matches/load", json=payload)
    assert response.status_code == 200
    assert response.json()["match_id"] == "test_api_1"


def test_load_match_with_events():
    payload = {
        "match_id": "test_api_2",
        "home_team": "Team A",
        "away_team": "Team B",
        "events": [
            {"minute": 1, "type": "Shot"},
            {"minute": 2, "type": "Pass"}
        ]
    }
    response = client.post("/matches/load", json=payload)
    assert response.status_code == 200
    
    # Try to analyze it - should work since it has events
    analyze_resp = client.post(f"/matches/test_api_2/analyze")
    assert analyze_resp.status_code == 200
    assert "turning_points" in analyze_resp.json()
