import os
import pandas as pd
from typing import Tuple
from sklearn.model_selection import train_test_split
import logging

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def normalize_url(url: str) -> str:
    """
    Normalizes raw URL strings:
    - Strips leading/trailing whitespace
    - Ensures a standard HTTP/HTTPS scheme prefix if missing
    
    Args:
        url: Raw URL string.
        
    Returns:
        str: Cleaned and normalized URL string.
    """
    if not isinstance(url, str):
        return ""
    
    url = url.strip()
    if not url:
        return ""
    
    # Add http:// default if no protocol scheme present
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "http://" + url
        
    return url


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw dataset by removing missing values, invalid URLs, and duplicate entries.
    
    Args:
        df: Input raw DataFrame.
        
    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    initial_count = len(df)
    
    # Drop NA rows
    df_clean = df.dropna(subset=["url", "label"]).copy()
    
    # Convert labels to integer type
    df_clean["label"] = df_clean["label"].astype(int)
    
    # Normalize URLs
    df_clean["url"] = df_clean["url"].apply(normalize_url)
    
    # Remove empty URLs after normalization
    df_clean = df_clean[df_clean["url"] != ""]
    
    # Remove duplicate URLs
    df_clean = df_clean.drop_duplicates(subset=["url"])
    
    final_count = len(df_clean)
    logging.info(f"Dataset cleaning complete: {initial_count} original rows -> {final_count} cleaned rows.")
    
    return df_clean.reset_index(drop=True)


def save_processed_dataset(df: pd.DataFrame, output_path: str = None) -> str:
    """
    Saves cleaned dataset to data/processed directory.
    
    Args:
        df: Cleaned DataFrame.
        output_path: Target CSV file path (defaults to config.CLEAN_DATASET_PATH).
        
    Returns:
        str: Absolute path to saved file.
    """
    if output_path is None:
        output_path = config.CLEAN_DATASET_PATH
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logging.info(f"Processed dataset saved to: {output_path}")
    return str(output_path)


def split_dataset(df: pd.DataFrame, test_size: float = None, random_state: int = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits cleaned dataset into training and testing sets with stratified class sampling.
    
    Args:
        df: Cleaned DataFrame.
        test_size: Ratio of test dataset (defaults to config.TEST_SIZE).
        random_state: Seed for reproducibility (defaults to config.RANDOM_STATE).
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (train_df, test_df)
    """
    if test_size is None:
        test_size = config.TEST_SIZE
    if random_state is None:
        random_state = config.RANDOM_STATE
        
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df["label"]
    )
    
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)
