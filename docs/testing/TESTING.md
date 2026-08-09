# Master Testing Log

| Test ID | Module | Test Description | Expected Result | Actual Result | Status | Date |
|:---|:---|:---|:---|:---|:---|:---|
| T0.1 | Module 0 | Verify Python dependencies installation | All packages import cleanly | pandas, numpy, sklearn, joblib, flask, tldextract, sqlite3, pytest imported | PASS | 2026-08-08 |
| T0.2 | Module 0 | Verify directory layout & paths | Required folders exist | core, data, static, templates, tests exist | PASS | 2026-08-08 |
| T0.3 | Module 0 | Config module loading | `config.py` loaded without error | `config.py` loaded cleanly with correct paths | PASS | 2026-08-08 |
| T1.1 | Module 1 | Dataset file existence | Dataset file exists at data/raw/phishing_urls.csv | Dataset file verified (2,000 rows) | PASS | 2026-08-08 |
| T1.2 | Module 1 | Dataset loading | `load_dataset` parses CSV cleanly | DataFrame loaded successfully | PASS | 2026-08-08 |
| T1.3 | Module 1 | Required columns check | 'url' and 'label' columns exist | Both required columns present | PASS | 2026-08-08 |
| T1.4 | Module 1 | Row count validation | Dataset contains $\ge 1000$ rows | 2,000 rows verified | PASS | 2026-08-08 |
| T1.5 | Module 1 | Missing value check | 0 missing values in url/label | 0 missing values found | PASS | 2026-08-08 |
| T1.6 | Module 1 | Binary label validity | Labels strictly in {0, 1} | Labels strictly binary {0: 1000, 1: 1000} | PASS | 2026-08-08 |
| T1.7 | Module 1 | Invalid path error handling | FileNotFoundError raised on invalid path | FileNotFoundError correctly raised | PASS | 2026-08-08 |
| T1.8 | Module 1 | Summary dictionary structure | `validate_dataset_summary` returns dict | Summary dict validated | PASS | 2026-08-08 |
| T2.1 | Module 2 | URL normalization | Normalizes spaces, missing `http://` prefix | Stripped spaces and added scheme prefix | PASS | 2026-08-08 |
| T2.2 | Module 2 | Cleaning duplicates & NaNs | Drops NA & duplicate URL records | Cleaned dataset deduplicated | PASS | 2026-08-08 |
| T2.3 | Module 2 | Save processed dataset | Writes CSV to data/processed/ | Cleaned CSV persisted | PASS | 2026-08-08 |
| T2.4 | Module 2 | Stratified train/test split | 80/20 train/test split with class balance | 80/20 stratified split verified | PASS | 2026-08-08 |
| T2.5 | Module 2 | Full preprocessing pipeline integration | Load, clean, save, and split full dataset | End-to-end preprocessing pipeline passed | PASS | 2026-08-08 |
| T3.1 | Module 3 | Valid URL extraction | Extracts 16 features for google.com | `is_https=1`, `num_subdomains=1` | PASS | 2026-08-08 |
| T3.2 | Module 3 | Suspicious keyword extraction | Detects security keywords | `has_suspicious_keyword=1` | PASS | 2026-08-08 |
| T3.3 | Module 3 | Raw IP URL extraction | Detects IPv4 hostname | `has_ip=1` | PASS | 2026-08-08 |
| T3.4 | Module 3 | @ symbol extraction | Counts `@` symbol | `count_at=1` | PASS | 2026-08-08 |
| T3.5 | Module 3 | Very long URL extraction | Computes long URL length | `url_length > 120` | PASS | 2026-08-08 |
| T3.6 | Module 3 | Many subdomains extraction | Counts subdomain levels | `num_subdomains=4` | PASS | 2026-08-08 |
| T3.7 | Module 3 | Malformed / empty input safety | Returns zeroed feature vector without crash | Safe fallback verified | PASS | 2026-08-08 |
| T3.8 | Module 3 | Batch DataFrame extraction | Shape equals (N, 16) | DataFrame shape verified | PASS | 2026-08-08 |
| T4.1 | Module 4 | Random Forest training | Fits RF model with random_state=42 | Accuracy > 90% achieved | PASS | 2026-08-08 |
| T4.2 | Module 4 | Save model & scaler | Persists joblib files | Files created in data/models/ | PASS | 2026-08-08 |
| T4.3 | Module 4 | Load model & scaler | Loads model into memory | Loaded model ready for inference | PASS | 2026-08-08 |
| T4.4 | Module 4 | Class prediction | Returns binary class (0 or 1) | Binary prediction verified | PASS | 2026-08-08 |
| T4.5 | Module 4 | Probability score | Probability floats between 0.0 and 1.0 | Valid probabilities verified | PASS | 2026-08-08 |
| T5.1 | Module 5 | Model evaluation metrics | Accuracy, Precision, Recall, F1, CM | All metrics computed cleanly | PASS | 2026-08-08 |
| T5.2 | Module 5 | Evaluation report writing | Updates MODEL_RESULTS.md | Report file written | PASS | 2026-08-08 |
| T6.1 | Module 6 | Legitimate URL inference | Predicts safe URL via pipeline | `prediction=Legitimate`, `risk_score < 50` | PASS | 2026-08-08 |
| T6.2 | Module 6 | Phishing URL inference | Predicts phishing URL via pipeline | `prediction=Phishing`, `risk_score >= 50` | PASS | 2026-08-08 |
| T6.3 | Module 6 | Empty input handling | Safe error dictionary response | Error handled without crash | PASS | 2026-08-08 |
| T7.1 | Module 7 | GET / Index view | Returns 200 OK HTML page | HTML page rendered | PASS | 2026-08-08 |
| T7.2 | Module 7 | POST /api/scan valid URL | Returns 200 OK JSON prediction | JSON prediction response verified | PASS | 2026-08-08 |
| T7.3 | Module 7 | POST /api/scan phishing URL | Returns 200 OK JSON high risk | High risk score & explanations returned | PASS | 2026-08-08 |
| T7.4 | Module 7 | POST /api/scan empty URL | Returns 400 Bad Request error | 400 error response verified | PASS | 2026-08-08 |
| T7.5 | Module 7 | POST /api/scan invalid JSON | Returns 400 Bad Request error | 400 error response verified | PASS | 2026-08-08 |
| T7.6 | Module 7 | GET /api/history & /api/stats | Returns 200 OK with scan history & stats | History & stats API verified | PASS | 2026-08-08 |
| T9.1 | Module 9 | DB schema initialization | Creates scans table in SQLite DB | Table created | PASS | 2026-08-08 |
| T9.2 | Module 9 | Save & retrieve scan log | Inserts scan record and queries history | Auto-increment ID & row retrieved | PASS | 2026-08-08 |
| T9.3 | Module 9 | Compute aggregate stats | Returns total scans, phishing count, avg risk | Aggregate metrics verified | PASS | 2026-08-08 |
| T10.1| Module 10| Risk score scaling | Probability 0.0-1.0 to 0-100 score | Integer scaling verified | PASS | 2026-08-08 |
| T10.2| Module 10| Risk level badges | SAFE, SUSPICIOUS, HIGH RISK, CRITICAL | Level mapping verified | PASS | 2026-08-08 |
| T10.3| Module 10| Explanation generator | Explanations for IP, keywords, SSL, etc. | Natural language explanations generated | PASS | 2026-08-08 |
| T11.1| Module 11| Full E2E workflow integration | Complete flow from index load to scan DB save | Full workflow PASSED 100% | PASS | 2026-08-08 |
