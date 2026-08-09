from typing import Dict, List, Any, Union


def calculate_risk_score(phishing_probability: float) -> int:
    """
    Converts model phishing probability (0.0 to 1.0) to a integer risk score (0 to 100).
    
    Args:
        phishing_probability: Float probability of phishing class from Random Forest model.
        
    Returns:
        int: Risk score scaled from 0 to 100.
    """
    prob = max(0.0, min(1.0, float(phishing_probability)))
    return int(round(prob * 100))


def get_risk_level(risk_score: int) -> str:
    """
    Maps 0-100 Risk Score to Risk Level string badge: LOW, MEDIUM, HIGH, CRITICAL.
    """
    if risk_score < 30:
        return "SAFE"
    elif risk_score < 60:
        return "SUSPICIOUS"
    elif risk_score < 85:
        return "HIGH RISK"
    else:
        return "CRITICAL PHISHING RISK"


def generate_explanations(url: str, features: Dict[str, Union[int, float]], risk_score: int) -> List[str]:
    """
    Generates human-readable cybersecurity explanations detailing why a URL is risky or safe.
    
    Args:
        url: Analyzed URL.
        features: Extracted feature values dictionary.
        risk_score: Calculated risk score (0-100).
        
    Returns:
        List[str]: Explanations list for UI display.
    """
    reasons = []
    
    # Feature 1: Raw IP Usage
    if features.get("has_ip", 0) == 1:
        reasons.append("URL uses a raw IP address instead of a trusted domain name (common in phishing).")
        
    # Feature 2: Suspicious Security Keywords
    if features.get("has_suspicious_keyword", 0) == 1:
        reasons.append("URL contains sensitive target keywords (e.g., login, verify, account, billing, bank).")
        
    # Feature 3: At Symbol Usage
    if features.get("count_at", 0) > 0:
        reasons.append("URL contains the '@' symbol which can obscure the real destination host.")
        
    # Feature 4: Excessive Subdomains
    if features.get("num_subdomains", 0) >= 3:
        reasons.append(f"URL contains excessive subdomain levels ({features.get('num_subdomains')} subdomains).")
        
    # Feature 5: Missing HTTPS
    if features.get("is_https", 1) == 0:
        reasons.append("URL uses insecure HTTP protocol without SSL/TLS encryption.")
        
    # Feature 6: URL Length
    if features.get("url_length", 0) > 75:
        reasons.append(f"Excessively long URL string ({features.get('url_length')} characters).")
        
    # Feature 7: Hyphen Count
    if features.get("count_hyphens", 0) >= 3:
        reasons.append("URL hostname contains multiple hyphens often used in brand impersonation.")
        
    # Default positive message if clean
    if not reasons and risk_score < 30:
        reasons.append("URL exhibits standard domain structure with valid SSL and no suspicious security indicators.")
        
    return reasons
