import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

REQUIRED_COLUMNS = ["url", "label"]
VALID_LABELS = {0, 1}


def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Loads and validates the dataset from a CSV file.
    
    Args:
        filepath: Path to the CSV dataset file.
        
    Returns:
        pd.DataFrame: Validated DataFrame.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty, missing required columns, or contains invalid labels.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file not found at: {filepath}")
    
    if os.path.getsize(filepath) == 0:
        raise ValueError(f"Dataset file at {filepath} is empty (0 bytes).")
    
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Failed to parse CSV file at {filepath}: {str(e)}")
        
    if df.empty:
        raise ValueError("Dataset DataFrame is empty after reading CSV.")
        
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset missing required column(s): {missing_cols}")
        
    # Check label integrity
    unique_labels = set(df["label"].dropna().unique())
    invalid_labels = unique_labels - VALID_LABELS
    if invalid_labels:
        raise ValueError(f"Dataset contains invalid label values: {invalid_labels}. Expected only 0 and 1.")
        
    return df


def validate_dataset_summary(df: pd.DataFrame) -> dict:
    """
    Computes statistical and structural summary of the loaded dataset.
    
    Args:
        df: Pandas DataFrame containing dataset.
        
    Returns:
        dict: Summary statistics including total rows, missing values, class distribution.
    """
    total_rows = len(df)
    missing_urls = int(df["url"].isnull().sum())
    missing_labels = int(df["label"].isnull().sum())
    label_counts = df["label"].value_counts().to_dict()
    
    summary = {
        "total_rows": total_rows,
        "missing_urls": missing_urls,
        "missing_labels": missing_labels,
        "legitimate_count": label_counts.get(0, 0),
        "phishing_count": label_counts.get(1, 0),
        "class_balance_ratio": round(label_counts.get(1, 0) / max(total_rows, 1), 4)
    }
    
    logging.info(f"Dataset validation summary: {summary}")
    return summary
