import os
import sys
import pytest

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, save_scan_result, get_scan_history, get_scan_stats


@pytest.fixture
def temp_db(tmp_path):
    return str(tmp_path / "test_phishing.db")


def test_init_db_creates_table(temp_db):
    """TC9.1: Verify SQLite database initializes scans table"""
    init_db(temp_db)
    assert os.path.exists(temp_db)


def test_save_and_retrieve_scan_result(temp_db):
    """TC9.2 & TC9.3: Verify inserting scan log and retrieving history"""
    sample_result = {
        "url": "http://192.168.1.1/login",
        "prediction": "Phishing",
        "risk_score": 90,
        "risk_level": "CRITICAL PHISHING RISK",
        "phishing_probability": 0.90,
        "explanations": ["URL uses a raw IP address."]
    }
    
    scan_id = save_scan_result(sample_result, temp_db)
    assert scan_id == 1
    
    history = get_scan_history(limit=10, db_path=temp_db)
    assert len(history) == 1
    assert history[0]["url"] == "http://192.168.1.1/login"
    assert history[0]["prediction"] == "Phishing"
    assert history[0]["risk_score"] == 90
    assert history[0]["explanations"] == ["URL uses a raw IP address."]


def test_scan_stats_computation(temp_db):
    """TC9.4: Verify scan aggregate statistics calculation"""
    res1 = {"url": "http://g.com", "prediction": "Legitimate", "risk_score": 10, "risk_level": "SAFE", "phishing_probability": 0.1, "explanations": []}
    res2 = {"url": "http://bad.com", "prediction": "Phishing", "risk_score": 90, "risk_level": "CRITICAL PHISHING RISK", "phishing_probability": 0.9, "explanations": []}
    
    save_scan_result(res1, temp_db)
    save_scan_result(res2, temp_db)
    
    stats = get_scan_stats(temp_db)
    assert stats["total_scans"] == 2
    assert stats["phishing_count"] == 1
    assert stats["legitimate_count"] == 1
    assert stats["average_risk_score"] == 50.0
