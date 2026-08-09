<div align="center">

```
██████╗ ██████╗ ██████╗  █████╗
██╔══██╗██╔══██╗██╔══██╗██╔══██╗
██████╔╝██║  ██║██████╔╝███████║
██╔═══╝ ██║  ██║██╔══██╗██╔══██║
██║     ██████╔╝██║  ██║██║  ██║
╚═╝     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
Phishing Detection & Risk Analysis
```

# 🎣 PDRA — Phishing URL Detection & Risk Analysis

> *"Not every link is what it seems. PDRA sees through the deception."*

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5+-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-13%20Modules-brightgreen?style=for-the-badge&logo=pytest)](tests/)

</div>

---

## 🧠 What is PDRA?

**PDRA** is a lightweight, explainable phishing URL detection system powered by a **Random Forest classifier** and a custom **risk scoring engine**. It analyzes URLs in real-time using **16 structural and lexical features** — no external APIs, no heavyweight dependencies, no black box.

Submit any URL. Get a verdict in milliseconds. Understand *why*.

```
https://paypa1-secure-login.account-verify.xyz/billing/confirm?token=xX99

                         🔴 CRITICAL PHISHING RISK — Score: 94/100

  ⚠ URL contains sensitive keywords (login, verify, account, billing)
  ⚠ Excessive subdomain levels detected (3 subdomains)
  ⚠ Excessively long URL string (72 characters)
  ⚠ Uses insecure HTTP without SSL/TLS
```

---

## ✨ Features at a Glance

| Feature | Description |
|---|---|
| 🔍 **16-Feature Extraction** | URL length, hostname structure, IP detection, HTTPS, hyphens, subdomains & more |
| 🌲 **Random Forest Model** | Trained on a synthetic benchmark; generalizable, fast, interpretable |
| 🎯 **0–100 Risk Scoring** | Raw probability → human-readable risk score with 4 tiers |
| 💬 **Plain-English Explanations** | Every prediction comes with *why* it flagged the URL |
| 📊 **Scan History Dashboard** | SQLite-backed scan log with aggregate stats via REST API |
| 🌐 **Browser Dashboard** | Vanilla HTML/CSS/JS frontend — no framework bloat |
| 🔒 **Security-Hardened API** | Input validation, size limits, error isolation |
| 🧪 **13 Test Modules** | Full coverage: unit, integration, Flask, OWASP, E2E |

---

## 🎨 Risk Level Scale

```
 0 ──────────── 30 ──────────── 60 ──────────── 85 ─────── 100
 │                │               │               │          │
 │    ✅ SAFE     │  ⚠ SUSPICIOUS │  🔶 HIGH RISK │ 🔴 CRIT  │
 │   (Legitimate) │  (Borderline) │  (Likely Bad) │(Phishing)│
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser Dashboard                     │
│              (HTML + CSS + Vanilla JS)                   │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP/JSON
┌──────────────────────────▼──────────────────────────────┐
│                    Flask REST API                        │
│          POST /api/scan  ·  GET /api/history             │
│                          ·  GET /api/stats               │
└──────┬───────────────────────────────────────┬──────────┘
       │                                       │
┌──────▼──────┐                       ┌────────▼────────┐
│  ML Engine  │                       │  SQLite Store   │
│─────────────│                       │─────────────────│
│ Feature     │                       │ Scan History    │
│ Extractor   │                       │ Aggregate Stats │
│ RF Model    │                       └─────────────────┘
│ Risk Engine │
│ Explainer   │
└─────────────┘
```

---

## 📁 Project Structure

```
phishing-url-detection/
│
├── 🚀 app.py                    # Flask entry point & API routes
├── ⚙️  config.py                 # Paths, hyperparameters, app settings
├── 🗄️  database.py               # SQLite schema, scan persistence, stats
├── 📋 requirements.txt          # Pinned production dependencies
│
├── 🧩 core/
│   ├── dataset_loader.py        # CSV loader with validation
│   ├── preprocessor.py          # Data cleaning and normalization
│   ├── feature_extractor.py     # 16-feature URL parser
│   ├── trainer.py               # Random Forest training pipeline
│   ├── evaluator.py             # Metrics: accuracy, F1, ROC-AUC
│   ├── predictor.py             # Inference + explanation orchestrator
│   └── risk_engine.py           # Probability → Risk score + explanations
│
├── 🧪 tests/
│   ├── test_module0_setup.py    # Environment checks
│   ├── test_module1_dataset.py  # Data loading
│   ├── test_module2_preprocessor.py
│   ├── test_module3_extractor.py
│   ├── test_module4_trainer.py
│   ├── test_module5_evaluator.py
│   ├── test_module6_predictor.py
│   ├── test_module7_flask.py    # API route tests
│   ├── test_module9_database.py
│   ├── test_module10_risk.py
│   ├── test_module11_e2e.py     # End-to-end tests
│   ├── test_owasp_security.py   # OWASP input fuzzing
│   └── test_security.py         # Security boundary tests
│
├── 📊 data/
│   ├── raw/                     # Raw dataset CSV
│   ├── processed/               # Cleaned dataset
│   └── models/                  # Trained .joblib model + scaler
│
├── 📄 docs/                     # Research, audits, investigation reports
├── 📈 evaluation_outputs/       # Model evaluation JSON results
├── 🔬 investigation_outputs/    # Perfect-score investigation results
├── 🖥️  scripts/                  # Dataset generation & audit scripts
├── 🎨 static/                   # CSS and JS assets
└── 📝 templates/index.html      # Single-page dashboard UI
```

---

## ⚡ Quick Start

### 1 · Clone the repo

```bash
git clone https://github.com/krishnarawatsf/phishing-url-detection.git
cd phishing-url-detection
```

### 2 · Set up a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

### 3 · Install dependencies

```bash
pip install -r requirements.txt
```

### 4 · Launch the app

```bash
python app.py
```

Open your browser at **[http://127.0.0.1:5000](http://127.0.0.1:5000)** 🎉

---

## 🌐 REST API Reference

### `POST /api/scan` — Analyze a URL

```bash
curl -X POST http://127.0.0.1:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://paypal.com/login"}'
```

<details>
<summary>📦 Example Response</summary>

```json
{
  "status": "success",
  "url": "https://paypal.com/login",
  "prediction": "Phishing",
  "prediction_class": 1,
  "phishing_probability": 0.82,
  "legitimate_probability": 0.18,
  "risk_score": 82,
  "risk_level": "HIGH RISK",
  "explanations": [
    "URL contains sensitive target keywords (e.g., login, verify, account, billing, bank)."
  ],
  "scan_id": 42
}
```

</details>

### `GET /api/history` — Recent Scan Logs

```bash
curl "http://127.0.0.1:5000/api/history?limit=5"
```

### `GET /api/stats` — Aggregate Metrics

```bash
curl http://127.0.0.1:5000/api/stats
```

---

## 🔬 The 16 Features

| # | Feature | Why It Matters |
|---|---------|---------------|
| 1 | `url_length` | Phishing URLs are often abnormally long |
| 2 | `hostname_length` | Bloated hostnames signal obfuscation |
| 3 | `path_length` | Deep paths hide malicious redirects |
| 4 | `count_dots` | Excessive dots = subdomain abuse |
| 5 | `count_hyphens` | Brand impersonation pattern |
| 6 | `count_at` | `@` symbol masks the real host |
| 7 | `count_question` | Query string injection indicator |
| 8 | `count_equals` | Parameter-heavy URLs are suspicious |
| 9 | `count_slash` | Deep directory traversal |
| 10 | `count_percent` | URL-encoded evasion |
| 11 | `count_digits` | Digit-heavy hostnames avoid detection |
| 12 | `count_letters` | Character ratio analysis |
| 13 | `has_ip` | Raw IP instead of domain = red flag |
| 14 | `is_https` | Missing SSL is a major risk indicator |
| 15 | `num_subdomains` | Excessive subdomains = deception |
| 16 | `has_suspicious_keyword` | login, verify, bank, billing, wallet… |

---

## 🧪 Running Tests

```bash
# Run all tests
pytest -q

# Run specific module
pytest tests/test_module7_flask.py -v

# Run security tests only
pytest tests/test_owasp_security.py tests/test_security.py -v

# Run with coverage report
pytest --cov=core --cov=database --cov-report=term-missing
```

---

## 🧪 Test Coverage Map

```
Module  0  · Environment & Setup         ████████████ 100%
Module  1  · Dataset Loader              ████████████ 100%
Module  2  · Preprocessor               ████████████ 100%
Module  3  · Feature Extractor          ████████████ 100%
Module  4  · Trainer                    ████████████ 100%
Module  5  · Evaluator                  ████████████ 100%
Module  6  · Predictor                  ████████████ 100%
Module  7  · Flask API Routes           ████████████ 100%
Module  9  · Database / SQLite          ████████████ 100%
Module 10  · Risk Engine                ████████████ 100%
Module 11  · End-to-End                 ████████████ 100%
Security   · OWASP Fuzzing              ████████████ 100%
Security   · Boundary & Injection       ████████████ 100%
```

---

## 🔒 Security Design

- **Input validation** on all API endpoints (type, length, emptiness)
- **Max payload size**: 1 MB hard cap — no request flooding
- **OWASP-tested**: Injection strings, oversized payloads, null bytes
- **No eval, no shell calls** — pure Python inference
- **SQLite parameterized queries** — no SQL injection surface
- **Secret key** loaded from environment: `FLASK_SECRET_KEY`

---

## 📚 Research & Documentation

| Document | Description |
|---|---|
| [`docs/MODEL_RESULTS.md`](docs/MODEL_RESULTS.md) | Accuracy, F1, precision, recall summary |
| [`docs/PERFECT_SCORE_INVESTIGATION.md`](docs/PERFECT_SCORE_INVESTIGATION.md) | Why the model scores so high — investigated |
| [`docs/REAL_WORLD_DATASET_PLAN.md`](docs/REAL_WORLD_DATASET_PLAN.md) | Plan for real phishing feed integration |
| [`docs/ORGANIZATION_AUDIT.md`](docs/ORGANIZATION_AUDIT.md) | Codebase quality and structure audit |
| [`evaluation_outputs/`](evaluation_outputs/) | JSON evaluation results |
| [`investigation_outputs/`](investigation_outputs/) | Dataset realism investigation results |

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Web Framework | Flask 3.1.1 |
| ML Library | scikit-learn 1.5+ |
| Data Processing | pandas 2.2+, NumPy 2.1+ |
| Model Persistence | joblib |
| URL Parsing | tldextract 5.3+, urllib |
| Database | SQLite (built-in) |
| Frontend | Vanilla HTML5 / CSS3 / JavaScript |
| Testing | pytest 8.3+ |

</div>

---

## ⚠️ Disclaimer

> This project is developed for **academic research and educational purposes** as a Major Project submission. It is **not a production-grade phishing defense system**. Real-world deployment would require:
> - Live phishing feed integration (e.g., PhishTank, OpenPhish)
> - Adversarial robustness testing
> - Continuous model retraining
> - HTTPS deployment behind a reverse proxy

---

## 👨‍💻 Author

<div align="center">

**Krishna Rawat**
B.Tech Computer Science · Major Project 2026

[![GitHub](https://img.shields.io/badge/GitHub-krishnarawatsf-181717?style=flat-square&logo=github)](https://github.com/krishnarawatsf)

</div>

---

## 📄 License

<div align="center">

Copyright © 2026 **Krishna Rawat**

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for full details.

*Free to use, modify, and distribute — just keep the copyright notice.*

</div>

---

<div align="center">

*Built with 🛡️ to make the internet a little safer, one URL at a time.*

</div>
