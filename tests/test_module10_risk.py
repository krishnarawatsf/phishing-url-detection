import os
import sys
import pytest

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.risk_engine import calculate_risk_score, get_risk_level, generate_explanations
from core.feature_extractor import extract_features


def test_calculate_risk_score_bounds():
    """TC10.1: Verify risk score scales float probabilities (0.0 to 1.0) into integers (0 to 100)"""
    assert calculate_risk_score(0.0) == 0
    assert calculate_risk_score(0.5) == 50
    assert calculate_risk_score(0.999) == 100
    assert calculate_risk_score(1.0) == 100


def test_get_risk_level_badges():
    """TC10.2: Verify risk level thresholds"""
    assert get_risk_level(10) == "SAFE"
    assert get_risk_level(45) == "SUSPICIOUS"
    assert get_risk_level(75) == "HIGH RISK"
    assert get_risk_level(95) == "CRITICAL PHISHING RISK"


def test_generate_explanations_ip_and_keywords():
    """TC10.3: Verify explanations list generated for IP & suspicious keywords"""
    url = "http://192.168.1.1/login"
    features = extract_features(url)
    reasons = generate_explanations(url, features, 90)
    
    assert len(reasons) >= 2
    assert any("raw IP address" in r for r in reasons)
    assert any("sensitive target keywords" in r for r in reasons)
