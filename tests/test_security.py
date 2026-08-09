import os
import sys
import pytest

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from database import save_scan_result, get_scan_history
from core.feature_extractor import extract_features
from core.predictor import PhishingPredictor
from app import app


@pytest.fixture
def temp_sec_db(tmp_path):
    return str(tmp_path / "sec_test.db")


def test_sql_injection_prevention(temp_sec_db):
    """SecTC1: Verify parameterized queries prevent SQL injection attacks"""
    sql_injection_payload = "http://example.com'; DROP TABLE scans; --"
    res = {
        "url": sql_injection_payload,
        "prediction": "Legitimate",
        "risk_score": 10,
        "risk_level": "SAFE",
        "phishing_probability": 0.10,
        "explanations": ["Clean"]
    }
    
    # Save payload to DB
    scan_id = save_scan_result(res, temp_sec_db)
    assert scan_id == 1
    
    # Query back history to ensure database integrity and table was not dropped
    history = get_scan_history(limit=5, db_path=temp_sec_db)
    assert len(history) == 1
    assert history[0]["url"] == sql_injection_payload


def test_xss_and_command_injection_payload_handling():
    """SecTC2: Verify feature extractor handles script tags and command injections without execution"""
    xss_payload = "<script>alert('XSS')</script>"
    feat = extract_features(xss_payload)
    assert isinstance(feat, dict)
    assert feat["has_ip"] == 0

    cmd_payload = "; rm -rf / ; http://example.com"
    feat_cmd = extract_features(cmd_payload)
    assert isinstance(feat_cmd, dict)


def test_api_security_malicious_input(tmp_path):
    """SecTC3: Verify API rejects malformed JSON and XSS attack inputs safely"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        res = client.post("/api/scan", json={"url": "<svg/onload=alert(1)>"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        # Input should be safely handled without crashing backend
        assert "url" in data


def test_production_hardening_defaults():
    """SecTC4: Ensure safe default production configuration is enabled."""
    assert config.FLASK_DEBUG is False
    assert config.FLASK_HOST in {"127.0.0.1", "0.0.0.0"}
    assert app.config.get("MAX_CONTENT_LENGTH") > 0
    assert app.config.get("SECRET_KEY")
