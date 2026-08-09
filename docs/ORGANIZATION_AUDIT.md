# Organization Audit

Audit date: 2026-08-07

| Item | Purpose | Current Location | Recommended Location | Action |
|---|---|---|---|---|
| `.agents/` | AI agent configuration root | `.agents/` | `.agents/` | KEEP |
| `.agents/workflows/` | Workflow definitions for agent automation | `.agents/workflows/` | `.agents/workflows/` | KEEP |
| `app.py` | Flask web application and API routes | `app.py` | `app.py` | KEEP |
| `config.py` | Central paths and hyperparameters | `config.py` | `config.py` | KEEP |
| `database.py` | SQLite schema, history writes, and stats queries | `database.py` | `database.py` | KEEP |
| `core/` | Main application package | `core/` | `core/` | KEEP |
| `core/__init__.py` | Package marker | `core/__init__.py` | `core/__init__.py` | KEEP |
| `core/dataset_loader.py` | Dataset loading and validation | `core/dataset_loader.py` | `core/dataset_loader.py` | KEEP |
| `core/preprocessor.py` | URL normalization, cleaning, and split logic | `core/preprocessor.py` | `core/preprocessor.py` | KEEP |
| `core/feature_extractor.py` | 16-feature URL extraction | `core/feature_extractor.py` | `core/feature_extractor.py` | KEEP |
| `core/trainer.py` | Model training, persistence, and reload | `core/trainer.py` | `core/trainer.py` | KEEP |
| `core/evaluator.py` | Metric calculation and report generation | `core/evaluator.py` | `core/evaluator.py` | KEEP |
| `core/predictor.py` | End-to-end phishing inference pipeline | `core/predictor.py` | `core/predictor.py` | KEEP |
| `core/risk_engine.py` | Risk scoring and explanation generation | `core/risk_engine.py` | `core/risk_engine.py` | KEEP |
| `scripts/` | Offline evaluation and dataset utility scripts | `scripts/` | `scripts/` | KEEP |
| `scripts/generate_dataset.py` | Synthetic dataset generator | `scripts/generate_dataset.py` | `scripts/generate_dataset.py` | KEEP |
| `scripts/check_adversarial_inputs.py` | Adversarial input checks | `scripts/check_adversarial_inputs.py` | `scripts/check_adversarial_inputs.py` | KEEP |
| `scripts/ml_quality_audit.py` | Quality audit helper | `scripts/ml_quality_audit.py` | `scripts/ml_quality_audit.py` | KEEP |
| `scripts/ml_comprehensive_evaluation.py` | Full evaluation and report generation | `scripts/ml_comprehensive_evaluation.py` | `scripts/ml_comprehensive_evaluation.py` | KEEP |
| `scripts/perfect_score_investigation.py` | Investigation into perfect scores | `scripts/perfect_score_investigation.py` | `scripts/perfect_score_investigation.py` | KEEP |
| `tests/` | Automated verification suite | `tests/` | `tests/` | KEEP |
| `tests/test_module0_setup.py` | Environment and config checks | `tests/test_module0_setup.py` | `tests/test_module0_setup.py` | KEEP |
| `tests/test_module1_dataset.py` | Dataset loading checks | `tests/test_module1_dataset.py` | `tests/test_module1_dataset.py` | KEEP |
| `tests/test_module2_preprocessor.py` | Preprocessing checks | `tests/test_module2_preprocessor.py` | `tests/test_module2_preprocessor.py` | KEEP |
| `tests/test_module3_extractor.py` | Feature extraction checks | `tests/test_module3_extractor.py` | `tests/test_module3_extractor.py` | KEEP |
| `tests/test_module4_trainer.py` | Training and persistence checks | `tests/test_module4_trainer.py` | `tests/test_module4_trainer.py` | KEEP |
| `tests/test_module5_evaluator.py` | Evaluation report checks | `tests/test_module5_evaluator.py` | `tests/test_module5_evaluator.py` | KEEP |
| `tests/test_module6_predictor.py` | Prediction pipeline checks | `tests/test_module6_predictor.py` | `tests/test_module6_predictor.py` | KEEP |
| `tests/test_module7_flask.py` | Flask route checks | `tests/test_module7_flask.py` | `tests/test_module7_flask.py` | KEEP |
| `tests/test_module9_database.py` | SQLite persistence checks | `tests/test_module9_database.py` | `tests/test_module9_database.py` | KEEP |
| `tests/test_module10_risk.py` | Risk score and explanation checks | `tests/test_module10_risk.py` | `tests/test_module10_risk.py` | KEEP |
| `tests/test_module11_e2e.py` | End-to-end workflow checks | `tests/test_module11_e2e.py` | `tests/test_module11_e2e.py` | KEEP |
| `tests/test_security.py` | Security-focused checks | `tests/test_security.py` | `tests/test_security.py` | KEEP |
| `tests/test_owasp_security.py` | OWASP-oriented security checks | `tests/test_owasp_security.py` | `tests/test_owasp_security.py` | KEEP |
| `data/` | Data root | `data/` | `data/` | KEEP |
| `data/raw/` | Raw dataset storage | `data/raw/` | `data/raw/` | KEEP |
| `data/raw/phishing_urls.csv` | Raw synthetic dataset | `data/raw/phishing_urls.csv` | `data/raw/phishing_urls.csv` | KEEP |
| `data/processed/` | Cleaned dataset storage | `data/processed/` | `data/processed/` | KEEP |
| `data/processed/cleaned_phishing_urls.csv` | Cleaned dataset | `data/processed/cleaned_phishing_urls.csv` | `data/processed/cleaned_phishing_urls.csv` | KEEP |
| `data/models/` | Persisted ML artifacts | `data/models/` | `data/models/` | KEEP |
| `data/models/phishing_rf_model.joblib` | Trained Random Forest model | `data/models/phishing_rf_model.joblib` | `data/models/phishing_rf_model.joblib` | KEEP |
| `data/models/scaler.joblib` | Feature scaler for inference | `data/models/scaler.joblib` | `data/models/scaler.joblib` | KEEP |
| `data/phishing_history.db` | SQLite scan history database | `data/phishing_history.db` | `data/phishing_history.db` | KEEP |
| `evaluation_outputs/` | Evaluation artifacts | `evaluation_outputs/` | `evaluation_outputs/` | KEEP |
| `evaluation_outputs/model_comparison.csv` | Model comparison table | `evaluation_outputs/model_comparison.csv` | `evaluation_outputs/model_comparison.csv` | KEEP |
| `evaluation_outputs/threshold_analysis.csv` | Threshold sweep results | `evaluation_outputs/threshold_analysis.csv` | `evaluation_outputs/threshold_analysis.csv` | KEEP |
| `evaluation_outputs/robustness_tests.csv` | Robustness test results | `evaluation_outputs/robustness_tests.csv` | `evaluation_outputs/robustness_tests.csv` | KEEP |
| `evaluation_outputs/evaluation_results.json` | Full evaluation JSON output | `evaluation_outputs/evaluation_results.json` | `evaluation_outputs/evaluation_results.json` | KEEP |
| `investigation_outputs/` | Investigation artifacts | `investigation_outputs/` | `investigation_outputs/` | KEEP |
| `investigation_outputs/feature_statistics.csv` | Feature distribution audit | `investigation_outputs/feature_statistics.csv` | `investigation_outputs/feature_statistics.csv` | KEEP |
| `investigation_outputs/feature_target_correlation.csv` | Feature-target correlation audit | `investigation_outputs/feature_target_correlation.csv` | `investigation_outputs/feature_target_correlation.csv` | KEEP |
| `investigation_outputs/ood_test_results.csv` | Out-of-distribution test results | `investigation_outputs/ood_test_results.csv` | `investigation_outputs/ood_test_results.csv` | KEEP |
| `investigation_outputs/investigation_results.json` | Full investigation JSON output | `investigation_outputs/investigation_results.json` | `investigation_outputs/investigation_results.json` | KEEP |
| `static/` | Frontend assets root | `static/` | `static/` | KEEP |
| `static/css/` | Stylesheet directory | `static/css/` | `static/css/` | KEEP |
| `static/css/style.css` | Application styles | `static/css/style.css` | `static/css/style.css` | KEEP |
| `static/js/` | JavaScript asset directory | `static/js/` | `static/js/` | KEEP |
| `static/js/app.js` | Frontend behavior script | `static/js/app.js` | `static/js/app.js` | KEEP |
| `templates/` | Flask template root | `templates/` | `templates/` | KEEP |
| `templates/index.html` | Main UI template | `templates/index.html` | `templates/index.html` | KEEP |
| `docs/` | Documentation root | `docs/` | `docs/` | KEEP |
| `docs/ORGANIZATION_AUDIT.md` | Folder organization audit | `docs/ORGANIZATION_AUDIT.md` | `docs/ORGANIZATION_AUDIT.md` | KEEP |
| `docs/MODEL_RESULTS.md` | Model evaluation summary | `docs/MODEL_RESULTS.md` | `docs/MODEL_RESULTS.md` | KEEP |
| `docs/ML_EVALUATION_REPORT.md` | Full model evaluation report | `docs/ML_EVALUATION_REPORT.md` | `docs/ML_EVALUATION_REPORT.md` | KEEP |
| `docs/PERFECT_SCORE_INVESTIGATION.md` | Investigation report for perfect scores | `docs/PERFECT_SCORE_INVESTIGATION.md` | `docs/PERFECT_SCORE_INVESTIGATION.md` | KEEP |
| `docs/RESEARCH_GAP.md` | Contribution and research-gap summary | `docs/RESEARCH_GAP.md` | `docs/RESEARCH_GAP.md` | KEEP |
| `docs/TESTING.md` | Consolidated testing log | `docs/TESTING.md` | `docs/TESTING.md` | KEEP |
| `README.md` | Project overview and quick start | `README.md` | `README.md` | KEEP |
| `PROJECT_STATUS.md` | Short project status note | `PROJECT_STATUS.md` | `PROJECT_STATUS.md` | KEEP |
| `requirements.txt` | Python dependencies | `requirements.txt` | `requirements.txt` | KEEP |
| `.gitignore` | Ignore rules for generated/local files | `.gitignore` | `.gitignore` | KEEP |
| `__pycache__/`, `core/__pycache__/`, `tests/__pycache__/`, `.pytest_cache/` | Python bytecode and pytest caches | Removed | None | DELETE |

## Notes

- The long markdown reports were moved out of the repo root to reduce clutter.
- `core/evaluator.py` now writes the evaluation summary to `docs/MODEL_RESULTS.md`.
- The SQLite history database was moved from the repo root to `data/phishing_history.db` so the root stays clean without changing runtime behavior.
