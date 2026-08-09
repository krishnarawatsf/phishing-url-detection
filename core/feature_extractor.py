import re
from urllib.parse import urlparse
import tldextract
import numpy as np
import pandas as pd
from typing import Dict, List, Union

FEATURE_NAMES = [
    "url_length",
    "hostname_length",
    "path_length",
    "count_dots",
    "count_hyphens",
    "count_at",
    "count_question",
    "count_equals",
    "count_slash",
    "count_percent",
    "count_digits",
    "count_letters",
    "has_ip",
    "is_https",
    "num_subdomains",
    "has_suspicious_keyword",
]

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "account", "update", "bank", "secure", "signin",
    "password", "confirm", "claim", "reward", "security", "wallet", "support", "billing"
]

# Regex for IPv4 and IPv6 addresses
IP_PATTERN = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|"
    r"^(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}$"
)


def extract_features(url: str) -> Dict[str, Union[int, float]]:
    """
    Extracts 16 structural, lexical, and security features from a given URL string.
    
    Args:
        url: Target URL string.
        
    Returns:
        Dict[str, Union[int, float]]: Feature dictionary mapping feature names to extracted numeric values.
    """
    if not isinstance(url, str) or not url.strip():
        # Fallback for empty or invalid input
        return {name: 0 for name in FEATURE_NAMES}
    
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url_with_scheme = "http://" + url
    else:
        url_with_scheme = url
        
    parsed = urlparse(url_with_scheme)
    hostname = parsed.netloc or ""
    path = parsed.path or ""
    
    # Strip port if present in hostname
    hostname_clean = hostname.split(":")[0] if ":" in hostname else hostname
    
    # Feature 1: URL Length
    url_len = len(url)
    
    # Feature 2: Hostname Length
    host_len = len(hostname_clean)
    
    # Feature 3: Path Length
    path_len = len(path)
    
    # Character Counts
    count_dots = url.count(".")
    count_hyphens = url.count("-")
    count_at = url.count("@")
    count_question = url.count("?")
    count_equals = url.count("=")
    count_slash = url.count("/")
    count_percent = url.count("%")
    
    # Digit and Letter counts
    count_digits = sum(c.isdigit() for c in url)
    count_letters = sum(c.isalpha() for c in url)
    
    # Feature: Has IP Address
    has_ip = 1 if IP_PATTERN.match(hostname_clean) else 0
    
    # Feature: Is HTTPS
    is_https = 1 if url.startswith("https://") else 0
    
    # Feature: Subdomains Count using tldextract
    ext = tldextract.extract(url_with_scheme)
    subdomain_str = ext.subdomain
    num_subdomains = len(subdomain_str.split(".")) if subdomain_str else 0
    
    # Feature: Suspicious Keywords
    url_lower = url.lower()
    has_keyword = 1 if any(kw in url_lower for kw in SUSPICIOUS_KEYWORDS) else 0
    
    return {
        "url_length": url_len,
        "hostname_length": host_len,
        "path_length": path_len,
        "count_dots": count_dots,
        "count_hyphens": count_hyphens,
        "count_at": count_at,
        "count_question": count_question,
        "count_equals": count_equals,
        "count_slash": count_slash,
        "count_percent": count_percent,
        "count_digits": count_digits,
        "count_letters": count_letters,
        "has_ip": has_ip,
        "is_https": is_https,
        "num_subdomains": num_subdomains,
        "has_suspicious_keyword": has_keyword,
    }


def extract_features_df(urls: List[str]) -> pd.DataFrame:
    """
    Extracts features for a list of URLs and returns a pandas DataFrame.
    
    Args:
        urls: List of URL strings.
        
    Returns:
        pd.DataFrame: DataFrame where columns equal FEATURE_NAMES.
    """
    feature_list = [extract_features(url) for url in urls]
    df_features = pd.DataFrame(feature_list)
    return df_features[FEATURE_NAMES]
