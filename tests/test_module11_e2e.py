import os
import sys
import pytest

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import get_scan_history, get_scan_stats


@pytest.fixture
def e2e_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_complete_e2e_workflow(e2e_client):
    """
    TC11.1: Complete End-to-End System Workflow Verification:
    1. GET / (Index Page load)
    2. POST /api/scan with Legitimate URL -> Extract, Predict, Risk, Explain, Save
    3. POST /api/scan with Phishing URL -> Extract, Predict, Risk, Explain, Save
    4. GET /api/history -> Verify both scans logged in SQLite
    5. GET /api/stats -> Verify aggregate counts updated correctly
    """
    # Step 1: Open main app page
    index_res = e2e_client.get("/")
    assert index_res.status_code == 200
    assert b"Phishing URL Risk Analyzer" in index_res.data
    
    # Step 2: Scan legitimate URL
    legit_res = e2e_client.post("/api/scan", json={"url": "https://www.wikipedia.org"})
    assert legit_res.status_code == 200
    legit_data = legit_res.get_json()
    assert legit_data["status"] == "success"
    assert legit_data["prediction"] == "Legitimate"
    assert legit_data["risk_score"] < 50
    assert "scan_id" in legit_data
    
    # Step 3: Scan phishing URL
    phish_res = e2e_client.post("/api/scan", json={"url": "http://192.168.1.1/login-account-paypal.php"})
    assert phish_res.status_code == 200
    phish_data = phish_res.get_json()
    assert phish_data["status"] == "success"
    assert phish_data["prediction"] == "Phishing"
    assert phish_data["risk_score"] >= 50
    assert len(phish_data["explanations"]) > 0
    assert "scan_id" in phish_data
    
    # Step 4: Verify Scan History in DB via API
    hist_res = e2e_client.get("/api/history?limit=10")
    assert hist_res.status_code == 200
    hist_data = hist_res.get_json()
    assert hist_data["status"] == "success"
    history_urls = [item["url"] for item in hist_data["history"]]
    assert "http://192.168.1.1/login-account-paypal.php" in history_urls
    
    # Step 5: Verify aggregate statistics via API
    stats_res = e2e_client.get("/api/stats")
    assert stats_res.status_code == 200
    stats_data = stats_res.get_json()
    assert stats_data["status"] == "success"
    assert stats_data["stats"]["total_scans"] >= 2
    assert stats_data["stats"]["phishing_count"] >= 1
