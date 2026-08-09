import os
import sqlite3
import json
from typing import List, Dict, Any
import logging

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_db_connection(db_path: str = None) -> sqlite3.Connection:
    """
    Returns an open SQLite database connection.
    """
    if db_path is None:
        db_path = str(config.DATABASE_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = None) -> None:
    """
    Initializes the SQLite database schema if the scans table does not exist.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            prediction TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            phishing_probability REAL NOT NULL,
            explanations TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    logging.info("SQLite database initialized successfully.")


def save_scan_result(result: Dict[str, Any], db_path: str = None) -> int:
    """
    Saves a URL scan result to the SQLite database.
    
    Args:
        result: Prediction result dictionary from PhishingPredictor.
        db_path: SQLite DB path.
        
    Returns:
        int: Inserted row ID.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    explanations_json = json.dumps(result.get("explanations", []))
    
    cursor.execute("""
        INSERT INTO scans (url, prediction, risk_score, risk_level, phishing_probability, explanations)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        result["url"],
        result["prediction"],
        result["risk_score"],
        result["risk_level"],
        result["phishing_probability"],
        explanations_json
    ))
    
    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return scan_id


def get_scan_history(limit: int = 20, db_path: str = None) -> List[Dict[str, Any]]:
    """
    Retrieves recent scan history from SQLite database.
    
    Args:
        limit: Number of recent scans to fetch.
        db_path: SQLite DB path.
        
    Returns:
        List[Dict[str, Any]]: Scan log records.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, url, prediction, risk_score, risk_level, phishing_probability, explanations, created_at
        FROM scans
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    history = []
    for r in rows:
        history.append({
            "id": r["id"],
            "url": r["url"],
            "prediction": r["prediction"],
            "risk_score": r["risk_score"],
            "risk_level": r["risk_level"],
            "phishing_probability": r["phishing_probability"],
            "explanations": json.loads(r["explanations"]),
            "created_at": r["created_at"]
        })
        
    conn.close()
    return history


def get_scan_stats(db_path: str = None) -> Dict[str, Any]:
    """
    Computes overall scan statistics (total scans, legitimate count, phishing count, avg risk).
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM scans")
    total = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as phishing FROM scans WHERE prediction = 'Phishing'")
    phishing = cursor.fetchone()["phishing"]
    
    cursor.execute("SELECT AVG(risk_score) as avg_risk FROM scans")
    avg_risk = cursor.fetchone()["avg_risk"] or 0.0
    
    conn.close()
    return {
        "total_scans": total,
        "phishing_count": phishing,
        "legitimate_count": total - phishing,
        "average_risk_score": round(avg_risk, 1)
    }
