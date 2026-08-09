import os
import sys
import pytest
import numpy as np

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.trainer import train_model, save_model_and_scaler, load_model_and_scaler
from core.feature_extractor import extract_features_df


def test_train_model_completes_and_returns_valid():
    """TC4.1: Verify Random Forest training completes with valid accuracy metrics"""
    model, scaler, meta = train_model()
    assert meta["train_accuracy"] > 0.85
    assert meta["test_accuracy"] > 0.85
    assert meta["train_samples"] > 0
    assert meta["test_samples"] > 0


def test_save_and_load_model_persists():
    """TC4.2 & TC4.3: Verify saving model & scaler creates files that load cleanly"""
    model, scaler, _ = train_model()
    m_path, s_path = save_model_and_scaler(model, scaler)
    
    assert os.path.exists(m_path)
    assert os.path.exists(s_path)
    
    loaded_model, loaded_scaler = load_model_and_scaler(m_path, s_path)
    assert loaded_model is not None
    assert loaded_scaler is not None


def test_model_prediction_and_probability():
    """TC4.4 & TC4.5: Verify model prediction class is binary and probability is between 0 and 1"""
    model, scaler, _ = train_model()
    test_urls = ["https://google.com", "http://192.168.1.1/login"]
    features_df = extract_features_df(test_urls)
    features_scaled = scaler.transform(features_df)
    
    preds = model.predict(features_scaled)
    probs = model.predict_proba(features_scaled)
    
    assert len(preds) == 2
    assert set(preds).issubset({0, 1})
    assert probs.shape == (2, 2)
    assert np.all((probs >= 0.0) & (probs <= 1.0))
    assert np.allclose(probs.sum(axis=1), 1.0)
