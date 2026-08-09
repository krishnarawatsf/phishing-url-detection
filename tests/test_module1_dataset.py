import os
import sys
import pytest
import pandas as pd

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.dataset_loader import load_dataset, validate_dataset_summary


def test_dataset_file_exists():
    """TC1.1: Verify dataset file exists in data/raw/"""
    assert os.path.exists(config.RAW_DATASET_PATH), f"Dataset file does not exist at {config.RAW_DATASET_PATH}"


def test_load_dataset_success():
    """TC1.2: Verify dataset loads successfully without error"""
    df = load_dataset(config.RAW_DATASET_PATH)
    assert isinstance(df, pd.DataFrame), "Returned object is not a pandas DataFrame"
    assert len(df) > 0, "Loaded dataset is empty"


def test_required_columns_exist():
    """TC1.3: Verify required columns ('url', 'label') exist"""
    df = load_dataset(config.RAW_DATASET_PATH)
    assert "url" in df.columns, "Missing 'url' column"
    assert "label" in df.columns, "Missing 'label' column"


def test_dataset_non_empty_and_rows():
    """TC1.4: Verify dataset has expected row count (> 100)"""
    df = load_dataset(config.RAW_DATASET_PATH)
    assert len(df) >= 1000, f"Expected at least 1000 rows, found {len(df)}"


def test_missing_values_handled():
    """TC1.5: Verify no missing/null values in url or label columns"""
    df = load_dataset(config.RAW_DATASET_PATH)
    summary = validate_dataset_summary(df)
    assert summary["missing_urls"] == 0, "Dataset contains missing URL entries"
    assert summary["missing_labels"] == 0, "Dataset contains missing label entries"


def test_binary_labels_validity():
    """TC1.6: Verify labels contain only binary classes (0 and 1)"""
    df = load_dataset(config.RAW_DATASET_PATH)
    unique_labels = set(df["label"].unique())
    assert unique_labels == {0, 1}, f"Unexpected label classes found: {unique_labels}"


def test_dataset_invalid_filepath_raises():
    """TC1.7: Error handling test for non-existent file path"""
    with pytest.raises(FileNotFoundError):
        load_dataset("non_existent_file.csv")


def test_dataset_summary_structure():
    """TC1.8: Check dataset validation summary output dictionary format"""
    df = load_dataset(config.RAW_DATASET_PATH)
    summary = validate_dataset_summary(df)
    assert "total_rows" in summary
    assert "legitimate_count" in summary
    assert "phishing_count" in summary
    assert summary["legitimate_count"] > 0
    assert summary["phishing_count"] > 0
