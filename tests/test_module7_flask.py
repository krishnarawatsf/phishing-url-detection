import os
import sys
import pytest

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """TC7.1: GET / returns HTML 200 OK"""
    res = client.get("/")
    assert res.status_code == 200


def test_scan_url_valid(client):
    """TC7.2: POST /api/scan with valid URL returns JSON prediction"""
    res = client.post("/api/scan", json={"url": "https://google.com"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "prediction" in data
    assert "risk_score" in data
    assert "explanations" in data


def test_scan_url_phishing(client):
    """TC7.3: POST /api/scan with phishing URL returns high risk score"""
    res = client.post("/api/scan", json={"url": "http://192.168.1.1/login-bank"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["prediction"] == "Phishing"
    assert data["risk_score"] >= 50


def test_scan_url_empty_validation_error(client):
    """TC7.4: POST /api/scan with empty URL returns 400 Bad Request"""
    res = client.post("/api/scan", json={"url": ""})
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"


def test_scan_url_invalid_payload(client):
    """TC7.5: POST /api/scan with invalid non-JSON payload returns 400 Bad Request"""
    res = client.post("/api/scan", data="not json", content_type="text/plain")
    assert res.status_code == 400


def test_get_history_and_stats(client):
    """TC7.6: GET /api/history and GET /api/stats return JSON success"""
    # Trigger a scan first
    client.post("/api/scan", json={"url": "https://wikipedia.org"})
    
    h_res = client.get("/api/history")
    assert h_res.status_code == 200
    h_data = h_res.get_json()
    assert h_data["status"] == "success"
    assert len(h_data["history"]) > 0
    
    s_res = client.get("/api/stats")
    assert s_res.status_code == 200
    s_data = s_res.get_json()
    assert s_data["status"] == "success"
    assert s_data["stats"]["total_scans"] > 0
