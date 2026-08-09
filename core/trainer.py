import os
import joblib
import pandas as pd
from typing import Tuple, Dict, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import logging

import config
from core.dataset_loader import load_dataset
from core.preprocessor import clean_dataset, split_dataset
from core.feature_extractor import extract_features_df, FEATURE_NAMES

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def train_model(
    df_clean: pd.DataFrame = None,
    n_estimators: int = None,
    random_state: int = None
) -> Tuple[RandomForestClassifier, StandardScaler, Dict[str, Any]]:
    """
    Trains Random Forest model and StandardScaler on extracted URL features.
    
    Args:
        df_clean: Cleaned input DataFrame containing 'url' and 'label'.
        n_estimators: Number of trees in Random Forest (defaults to config.RF_N_ESTIMATORS).
        random_state: Seed for reproducibility (defaults to config.RANDOM_STATE).
        
    Returns:
        Tuple[RandomForestClassifier, StandardScaler, Dict[str, Any]]: Trained model, scaler, and training metadata.
    """
    if df_clean is None:
        raw_df = load_dataset(config.RAW_DATASET_PATH)
        df_clean = clean_dataset(raw_df)
        
    if n_estimators is None:
        n_estimators = config.RF_N_ESTIMATORS
    if random_state is None:
        random_state = config.RANDOM_STATE
        
    train_df, test_df = split_dataset(df_clean, test_size=config.TEST_SIZE, random_state=random_state)
    
    logging.info(f"Extracting features for {len(train_df)} training samples...")
    X_train_raw = extract_features_df(train_df["url"].tolist())
    y_train = train_df["label"].values
    
    X_test_raw = extract_features_df(test_df["url"].tolist())
    y_test = test_df["label"].values
    
    # Fit StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_raw)
    X_test_scaled = scaler.transform(X_test_raw)
    
    # Fit Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=-1
    )
    rf_model.fit(X_train_scaled, y_train)
    
    train_acc = rf_model.score(X_train_scaled, y_train)
    test_acc = rf_model.score(X_test_scaled, y_test)
    logging.info(f"Training Complete. Train Acc: {train_acc:.4f}, Test Acc: {test_acc:.4f}")
    
    meta = {
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "train_accuracy": float(train_acc),
        "test_accuracy": float(test_acc),
        "feature_names": FEATURE_NAMES,
        "X_test_scaled": X_test_scaled,
        "y_test": y_test
    }
    
    return rf_model, scaler, meta


def save_model_and_scaler(
    model: RandomForestClassifier,
    scaler: StandardScaler,
    model_path: str = None,
    scaler_path: str = None
) -> Tuple[str, str]:
    """
    Persists trained model and scaler to joblib files.
    """
    if model_path is None:
        model_path = config.MODEL_PATH
    if scaler_path is None:
        scaler_path = config.SCALER_PATH
        
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    logging.info(f"Model saved to {model_path}, Scaler saved to {scaler_path}")
    
    return str(model_path), str(scaler_path)


def load_model_and_scaler(
    model_path: str = None,
    scaler_path: str = None
) -> Tuple[RandomForestClassifier, StandardScaler]:
    """
    Loads saved model and scaler from joblib files.
    """
    if model_path is None:
        model_path = config.MODEL_PATH
    if scaler_path is None:
        scaler_path = config.SCALER_PATH
        
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Scaler file not found at: {scaler_path}")
        
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler
