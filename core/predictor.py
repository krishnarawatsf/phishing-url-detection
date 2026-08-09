import os
import pandas as pd
from typing import Dict, Any, Union

import config
from core.trainer import train_model, save_model_and_scaler, load_model_and_scaler
from core.feature_extractor import extract_features, extract_features_df, FEATURE_NAMES
from core.preprocessor import normalize_url
from core.risk_engine import calculate_risk_score, get_risk_level, generate_explanations


class PhishingPredictor:
    """
    Unified Prediction Pipeline encapsulating model loading, URL normalization, 
    feature extraction, probability prediction, risk scoring, and explanation generation.
    """
    def __init__(self, model_path: str = None, scaler_path: str = None):
        if model_path is None:
            model_path = config.MODEL_PATH
        if scaler_path is None:
            scaler_path = config.SCALER_PATH
            
        # Ensure model exists, train if missing
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            model, scaler, _ = train_model()
            save_model_and_scaler(model, scaler, model_path, scaler_path)
            self.model = model
            self.scaler = scaler
        else:
            self.model, self.scaler = load_model_and_scaler(model_path, scaler_path)

    def predict_url(self, raw_url: str) -> Dict[str, Any]:
        """
        Executes complete inference pipeline on a single URL string.
        
        Args:
            raw_url: Input URL string from user or API.
            
        Returns:
            Dict[str, Any]: Complete analysis result containing normalized URL, prediction label, 
                            probabilities, risk score, risk level, feature breakdown, and explanations.
        """
        if not raw_url or not isinstance(raw_url, str) or not raw_url.strip():
            return {
                "status": "error",
                "message": "URL input cannot be empty.",
                "url": ""
            }
            
        clean_url = normalize_url(raw_url)
        
        # 1. Feature Extraction
        features = extract_features(clean_url)
        features_df = pd.DataFrame([features])[FEATURE_NAMES]
        
        # 2. Scale Features
        features_scaled = self.scaler.transform(features_df)
        
        # 3. Model Prediction
        prediction_class = int(self.model.predict(features_scaled)[0])
        probabilities = self.model.predict_proba(features_scaled)[0]
        phishing_prob = float(probabilities[1])
        legitimate_prob = float(probabilities[0])
        
        # 4. Risk Scoring & Explanations
        risk_score = calculate_risk_score(phishing_prob)
        risk_level = get_risk_level(risk_score)
        explanations = generate_explanations(clean_url, features, risk_score)
        
        return {
            "status": "success",
            "url": clean_url,
            "prediction": "Phishing" if prediction_class == 1 else "Legitimate",
            "prediction_class": prediction_class,
            "phishing_probability": round(phishing_prob, 4),
            "legitimate_probability": round(legitimate_prob, 4),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "explanations": explanations,
            "features": features
        }
