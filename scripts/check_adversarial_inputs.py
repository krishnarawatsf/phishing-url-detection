import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.predictor import PhishingPredictor

predictor = PhishingPredictor()

test_cases = [
    ("<script>alert(1)</script>", "XSS Payload"),
    ("' OR '1'='1", "SQL Injection Payload"),
    ("javascript:alert(1)", "JavaScript URI Scheme"),
    ("../../etc/passwd", "Path Traversal Payload"),
    ("http://example.com@evil.com", "At-Symbol Domain Spoofing"),
    ("http://example.com/" + "a" * 1000, "Extremely Long URL"),
    ("", "Empty Input"),
    ("not_a_valid_url_123", "Invalid / Arbitrary Text")
]

print("=== ADVERSARIAL INPUT TEST RESULTS ===")
for url, description in test_cases:
    print(f"\n--- [Test: {description}] ---")
    print(f"Input: {url[:60]}{'...' if len(url) > 60 else ''}")
    res = predictor.predict_url(url)
    print(f"Status: {res['status']}")
    if res['status'] == 'success':
        print(f"Normalized URL: {res['url'][:60]}{'...' if len(res['url']) > 60 else ''}")
        print(f"Prediction: {res['prediction']}")
        print(f"Risk Score: {res['risk_score']} / 100 ({res['risk_level']})")
        print(f"Explanations: {res['explanations']}")
    else:
        print(f"Error Message: {res['message']}")
