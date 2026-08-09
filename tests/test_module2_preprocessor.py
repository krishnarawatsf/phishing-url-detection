import os
import sys
import pytest
import pandas as pd

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.dataset_loader import load_dataset
from core.preprocessor import normalize_url, clean_dataset, save_processed_dataset, split_dataset


def test_normalize_url_variations():
    """TC2.1: Verify URL normalization handles protocol, spaces, missing prefix"""
    assert normalize_url("  google.com  ") == "http://google.com"
    assert normalize_url("https://example.com/login") == "https://example.com/login"
    assert normalize_url("http://192.168.1.1") == "http://192.168.1.1"
    assert normalize_url("") == ""
    assert normalize_url(None) == ""


def test_clean_dataset_removes_duplicates_and_nans():
    """TC2.2: Verify clean_dataset removes duplicate URLs and NA values"""
    raw_data = {
        "url": ["google.com", "google.com", "  https://paypal.com  ", None, ""],
        "label": [0, 0, 1, 1, 0]
    }
    raw_df = pd.DataFrame(raw_data)
    cleaned = clean_dataset(raw_df)
    
    # Only 2 unique valid URLs should remain
    assert len(cleaned) == 2
    assert "http://google.com" in cleaned["url"].values
    assert "https://paypal.com" in cleaned["url"].values
    assert cleaned["label"].tolist() == [0, 1]


def test_save_processed_dataset_persists_file():
    """TC2.3: Verify save_processed_dataset creates valid CSV file"""
    df = pd.DataFrame({"url": ["http://test.com"], "label": [0]})
    output_path = save_processed_dataset(df, config.CLEAN_DATASET_PATH)
    
    assert os.path.exists(output_path), "Processed dataset file was not created"
    loaded = pd.read_csv(output_path)
    assert len(loaded) == 1
    assert loaded.iloc[0]["url"] == "http://test.com"


def test_stratified_train_test_split():
    """TC2.4: Verify train/test split maintains 80/20 ratio and class stratification"""
    df_raw = load_dataset(config.RAW_DATASET_PATH)
    df_clean = clean_dataset(df_raw)
    
    train_df, test_df = split_dataset(df_clean, test_size=0.2, random_state=42)
    
    total_len = len(df_clean)
    assert len(train_df) + len(test_df) == total_len
    # 20% test size tolerance check
    assert abs(len(test_df) / total_len - 0.2) < 0.02
    
    # Class balance stratification check
    train_phish_ratio = (train_df["label"] == 1).mean()
    test_phish_ratio = (test_df["label"] == 1).mean()
    assert abs(train_phish_ratio - test_phish_ratio) < 0.01


def test_integration_full_preprocessing_flow():
    """TC2.5: Integration test loading raw data, cleaning, saving, and splitting"""
    raw_df = load_dataset(config.RAW_DATASET_PATH)
    clean_df = clean_dataset(raw_df)
    saved_path = save_processed_dataset(clean_df)
    
    assert os.path.exists(saved_path)
    loaded_clean = pd.read_csv(saved_path)
    assert len(loaded_clean) == len(clean_df)
    
    train_df, test_df = split_dataset(loaded_clean)
    assert len(train_df) > 0
    assert len(test_df) > 0
