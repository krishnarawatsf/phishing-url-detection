import os
import csv
import random

# Seed for reproducibility
random.seed(42)

output_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "phishing_urls.csv")
os.makedirs(os.path.dirname(output_path), exist_ok=True)

legitimate_domains = [
    "google.com", "youtube.com", "facebook.com", "wikipedia.org", "yahoo.com",
    "amazon.com", "reddit.com", "netflix.com", "linkedin.com", "twitter.com",
    "instagram.com", "github.com", "microsoft.com", "apple.com", "stackoverflow.com",
    "bing.com", "adobe.com", "wordpress.org", "medium.com", "spotify.com",
    "dropbox.com", "nytimes.com", "cnn.com", "bbc.com", "quora.com",
    "imdb.com", "paypal.com", "chase.com", "wellsfargo.com", "bankofamerica.com"
]

legitimate_paths = [
    "", "/", "/about", "/contact", "/search?q=cyber+security", "/docs/guide",
    "/user/profile", "/products/item123", "/blog/2026/08/article", "/help/center",
    "/settings/account", "/download/version1", "/api/v1/data", "/terms-of-service"
]

phishing_keywords = [
    "secure-login", "verify-account", "update-billing", "bank-security", "paypal-update",
    "account-verification", "signin-portal", "password-reset", "claim-reward", "free-giftcard",
    "unusual-activity", "confirm-identity", "wallet-connect", "support-desk", "security-alert"
]

suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".club", ".info", ".online", ".site"]

urls_data = []

# Generate 1000 Legitimate URLs (label = 0)
for i in range(1000):
    domain = random.choice(legitimate_domains)
    path = random.choice(legitimate_paths)
    sub = random.choice(["", "www.", "blog.", "docs.", "support.", "api."])
    scheme = "https://" if random.random() > 0.1 else "http://"
    url = f"{scheme}{sub}{domain}{path}"
    urls_data.append((url, 0))

# Generate 1000 Phishing URLs (label = 1)
# Including IP-based, @ symbol, deep subdomains, fake brand names, suspicious TLDs
for i in range(1000):
    pattern_type = random.randint(1, 5)
    scheme = random.choice(["http://", "https://"])
    
    if pattern_type == 1:
        # Raw IP address URL
        ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
        path = random.choice(["/login", "/verify", "/bank/account", "/signin.html", "/auth"])
        url = f"{scheme}{ip}{path}"
    elif pattern_type == 2:
        # @ symbol trick
        legit_target = random.choice(["paypal.com", "google.com", "chase.com", "bankofamerica.com"])
        malicious = f"attacker-{random.randint(100,999)}" + random.choice(suspicious_tlds)
        url = f"{scheme}{legit_target}@{malicious}/login.php"
    elif pattern_type == 3:
        # Excessive subdomains and hyphens
        kw = random.choice(phishing_keywords)
        brand = random.choice(["paypal", "apple", "amazon", "microsoft", "netflix"])
        tld = random.choice(suspicious_tlds)
        url = f"{scheme}www.{brand}.{kw}.account-security-alert-check{tld}/index.html?ref=login"
    elif pattern_type == 4:
        # Suspicious keyword path and URL length
        kw = random.choice(phishing_keywords)
        domain = f"login-{random.randint(1000,9999)}" + random.choice(suspicious_tlds)
        path = f"/{kw}/verify_user_credentials_session_id_{random.randint(10000,99999)}_secure_token_abc"
        url = f"{scheme}{domain}{path}"
    else:
        # Brand spoofing TLD
        brand = random.choice(["paypal", "google", "netflix", "amazon", "chase"])
        tld = random.choice(suspicious_tlds)
        url = f"{scheme}{brand}-security-update{tld}/signin"

    urls_data.append((url, 1))

# Shuffle dataset
random.shuffle(urls_data)

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["url", "label"])
    writer.writerows(urls_data)

print(f"Generated benchmark dataset at {output_path} with {len(urls_data)} rows.")
