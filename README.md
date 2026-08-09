# PDRA: Phishing URL Detection and Risk Analysis

A lightweight phishing URL detection system built around a Random Forest classifier and explainable risk scoring. This project combines lexical URL feature extraction, a Flask API, SQLite scan history, and a browser-based dashboard for live phishing assessment.

## Overview

This repository implements a practical ML prototype for identifying suspicious phishing URLs using structural and lexical indicators such as:

- URL length and hostname length
- presence of IP addresses
- suspicious keyword matches
- `@` symbols and encoded/obfuscated host patterns
- excessive subdomains and hyphen-heavy hostnames
- HTTP vs HTTPS usage

The system predicts whether a URL is phishing or legitimate, converts the model probability to a 0–100 risk score, and produces human-readable explanations for the result.

## Architecture at a Glance

- Frontend: HTML + CSS + JavaScript
- Backend: Flask REST API
- Model: Random Forest trained on URL features
- Persistence: SQLite scan history
- Data: locally generated synthetic benchmark dataset

## Tech Stack

- Python 3.12+
- Pandas, NumPy
- scikit-learn
- Joblib
- Flask
- SQLite
- tldextract
- Vanilla JavaScript + HTML/CSS

## Project Structure

```text
.
├── app.py
├── config.py
├── database.py
├── requirements.txt
├── constraints.txt
├── upgrade_dependencies.sh
├── LICENSE
├── README.md
├── core/
│   ├── dataset_loader.py
│   ├── evaluator.py
│   ├── feature_extractor.py
│   ├── predictor.py
│   ├── preprocessor.py
│   ├── risk_engine.py
│   └── trainer.py
├── data/
│   ├── models/
│   ├── processed/
│   └── raw/
├── docs/
│   ├── MODEL_RESULTS.md
│   ├── ORGANIZATION_AUDIT.md
│   ├── PERFECT_SCORE_INVESTIGATION.md
│   ├── REAL_WORLD_DATASET_PLAN.md
│   ├── ml/
│   ├── project/
│   ├── research/
│   └── security/
├── evaluation_outputs/
├── investigation_outputs/
├── scripts/
│   ├── check_adversarial_inputs.py
│   ├── generate_dataset.py
│   ├── ml_comprehensive_evaluation.py
│   ├── ml_quality_audit.py
│   └── perfect_score_investigation.py
├── static/
│   ├── css/
│   └── js/
├── templates/
│   └── index.html
├── tests/
└── .gitignore
```

## Quick Start

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

### 4. Run tests

```bash
pytest -q
```

## API Usage

### Scan a URL

```bash
curl -X POST http://127.0.0.1:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.wikipedia.org"}'
```

Example response:

```json
{
  "status": "success",
  "url": "https://www.wikipedia.org",
  "prediction": "Legitimate",
  "prediction_class": 0,
  "phishing_probability": 0.01,
  "legitimate_probability": 0.99,
  "risk_score": 1,
  "risk_level": "SAFE",
  "explanations": [
    "URL exhibits standard domain structure with valid SSL and no suspicious security indicators."
  ]
}
```

## Model and Dataset Notes

This project uses a locally generated synthetic phishing benchmark rather than a live phishing feed. The training and evaluation scripts explicitly document the dataset generation pattern and the resulting performance characteristics. The repository also includes an investigation report that examines why the model appears to achieve perfect metrics on the benchmark.

## Research and Audit Material

The repository contains additional project documentation and investigation output, including:

- [docs/ml/ML_EVALUATION_REPORT.md](docs/ml/ML_EVALUATION_REPORT.md)
- [docs/PERFECT_SCORE_INVESTIGATION.md](docs/PERFECT_SCORE_INVESTIGATION.md)
- [docs/REAL_WORLD_DATASET_PLAN.md](docs/REAL_WORLD_DATASET_PLAN.md)
- [evaluation_outputs/evaluation_results.json](evaluation_outputs/evaluation_results.json)
- [investigation_outputs/investigation_results.json](investigation_outputs/investigation_results.json)

These files provide a more detailed assessment of the model, dataset realism, and evaluation limitations.

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

This project is intended for research and educational use. It is not a production-grade phishing defense system without additional evaluation on real-world phishing data and stronger adversarial testing.
