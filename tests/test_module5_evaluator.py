import os
import sys
import pytest

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.trainer import train_model, save_model_and_scaler
from core.evaluator import evaluate_model, generate_evaluation_report


def test_evaluate_model_calculates_all_metrics():
    """TC5.1: Verify evaluation computes Accuracy, Precision, Recall, F1, CM, and Feature Importances"""
    model, scaler, meta = train_model()
    metrics = evaluate_model(model, scaler, meta["X_test_scaled"], meta["y_test"])
    
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1_score" in metrics
    assert "confusion_matrix" in metrics
    assert "feature_importances" in metrics
    
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["precision"] <= 1.0
    assert 0.0 <= metrics["recall"] <= 1.0
    assert 0.0 <= metrics["f1_score"] <= 1.0
    assert len(metrics["confusion_matrix"]) == 2
    assert len(metrics["confusion_matrix"][0]) == 2


def test_generate_evaluation_report_writes_file():
    """TC5.2: Verify report generator writes docs/MODEL_RESULTS.md"""
    model, scaler, meta = train_model()
    save_model_and_scaler(model, scaler)
    metrics = evaluate_model(model, scaler, meta["X_test_scaled"], meta["y_test"])
    
    report_path = generate_evaluation_report(metrics)
    assert os.path.exists(report_path)
    
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Accuracy" in content
        assert "Confusion Matrix" in content
        assert "Feature Importance" in content
