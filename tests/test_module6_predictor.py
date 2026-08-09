import os
import sys
import pytest

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.predictor import PhishingPredictor


def test_predictor_valid_url():
    """TC6.1: Verify inference pipeline on valid legitimate URL"""
    predictor = PhishingPredictor()
    res = predictor.predict_url("https://www.google.com")
    
    assert res["status"] == "success"
    assert res["prediction"] == "Legitimate"
    assert res["prediction_class"] == 0
    assert res["risk_score"] < 50
    assert isinstance(res["explanations"], list)


def test_predictor_phishing_url():
    """TC6.2: Verify inference pipeline on obvious phishing URL"""
    predictor = PhishingPredictor()
    res = predictor.predict_url("http://192.168.1.1/verify-account-bank-login.php")
    
    assert res["status"] == "success"
    assert res["prediction"] == "Phishing"
    assert res["prediction_class"] == 1
    assert res["risk_score"] >= 50
    assert len(res["explanations"]) > 0


def test_predictor_empty_or_invalid_url():
    """TC6.3: Verify graceful error response for empty URL"""
    predictor = PhishingPredictor()
    res = predictor.predict_url("")
    assert res["status"] == "error"
    assert "cannot be empty" in res["message"]
