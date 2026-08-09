import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODEL_DIR = DATA_DIR / "models"
DATABASE_PATH = DATA_DIR / "phishing_history.db"

# Data & Model Configuration
RAW_DATASET_NAME = "phishing_urls.csv"
RAW_DATASET_PATH = RAW_DATA_DIR / RAW_DATASET_NAME
CLEAN_DATASET_PATH = PROCESSED_DATA_DIR / "cleaned_phishing_urls.csv"
MODEL_PATH = MODEL_DIR / "phishing_rf_model.joblib"
SCALER_PATH = MODEL_DIR / "scaler.joblib"

# Model Hyperparameters
RANDOM_STATE = 42
TEST_SIZE = 0.2
RF_N_ESTIMATORS = 100

# Web Application Settings
# Keep local testing convenient, but prefer safe defaults for any public deployment.
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = False
MAX_REQUEST_SIZE = 1 * 1024 * 1024  # 1MB maximum request payload
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
