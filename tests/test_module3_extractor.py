import os
import sys
import pytest
import pandas as pd

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.feature_extractor import extract_features, extract_features_df, FEATURE_NAMES


def test_valid_google_url():
    """TC3.1: Valid URL https://www.google.com"""
    feat = extract_features("https://www.google.com")
    assert feat["is_https"] == 1
    assert feat["has_ip"] == 0
    assert feat["count_at"] == 0
    assert feat["num_subdomains"] == 1  # 'www'
    assert len(feat) == len(FEATURE_NAMES)


def test_suspicious_keywords_url():
    """TC3.2: Suspicious URL with security keywords"""
    feat = extract_features("http://secure-login-example.com/verify-account")
    assert feat["has_suspicious_keyword"] == 1
    assert feat["count_hyphens"] >= 2
    assert feat["is_https"] == 0


def test_raw_ip_url():
    """TC3.3: URL with IPv4 address"""
    feat = extract_features("http://192.168.1.1/login")
    assert feat["has_ip"] == 1
    assert feat["has_suspicious_keyword"] == 1


def test_at_symbol_url():
    """TC3.4: URL containing @ symbol"""
    feat = extract_features("http://example.com@malicious.com")
    assert feat["count_at"] == 1


test_long_url_str = "http://www.example.com/path/" + "a" * 100 + "?ref=123"


def test_very_long_url():
    """TC3.5: Very long URL length calculation"""
    feat = extract_features(test_long_url_str)
    assert feat["url_length"] > 120
    assert feat["count_question"] == 1


def test_many_subdomains_url():
    """TC3.6: URL with multiple subdomains"""
    feat = extract_features("http://a.b.c.d.example.com/test")
    assert feat["num_subdomains"] == 4
    assert feat["count_dots"] >= 4


def test_malformed_and_empty_inputs():
    """TC3.7: Safe handling of malformed or empty inputs without crashing"""
    feat_empty = extract_features("")
    assert len(feat_empty) == len(FEATURE_NAMES)
    assert all(val == 0 for val in feat_empty.values())

    feat_none = extract_features(None)
    assert len(feat_none) == len(FEATURE_NAMES)


def test_extract_features_df_shape():
    """TC3.8: DataFrame extraction shape and column consistency"""
    urls = ["https://google.com", "http://192.168.1.1/login", "http://example.com@malicious.com"]
    df = extract_features_df(urls)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, len(FEATURE_NAMES))
    assert list(df.columns) == FEATURE_NAMES
