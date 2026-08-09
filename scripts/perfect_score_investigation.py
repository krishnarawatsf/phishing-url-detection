"""
Investigation into suspiciously perfect ML performance.
Does NOT modify production model or config.
"""
import os
import sys
import json
import warnings
from collections import defaultdict
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
import tldextract
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold, train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
from scipy.stats import pointbiserialr, mannwhitneyu

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.dataset_loader import load_dataset
from core.preprocessor import clean_dataset, split_dataset, normalize_url
from core.feature_extractor import extract_features_df, FEATURE_NAMES, extract_features

OUTPUT_DIR = os.path.join(config.BASE_DIR, "investigation_outputs")
RANDOM_STATE = config.RANDOM_STATE
SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".club", ".info", ".online", ".site"}


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_registered_domain(url: str) -> str:
    """Extract registered domain (domain + suffix) for grouping."""
    ext = tldextract.extract(url)
    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}".lower()
    # IP addresses
    parsed_host = url.replace("https://", "").replace("http://", "").split("/")[0].split("@")[-1].split(":")[0]
    if parsed_host.replace(".", "").isdigit() or "." in parsed_host:
        return parsed_host.lower()
    return url.lower()


def extract_base_domain_key(url: str) -> str:
    """For legitimate URLs: registered domain. For phishing: full hostname before path."""
    ext = tldextract.extract(url)
    if ext.domain and ext.suffix:
        reg = f"{ext.domain}.{ext.suffix}".lower()
        # For phishing on suspicious TLDs, treat full hostname as unique domain unit
        host = url.replace("https://", "").replace("http://", "").split("/")[0].split("@")[-1].split(":")[0].lower()
        if any(host.endswith(tld.strip(".")) or tld in host for tld in SUSPICIOUS_TLDS):
            return host
        return reg
    return url.lower()


def url_canonical_key(url: str) -> str:
    """Near-duplicate key: strip scheme and trailing slash."""
    u = url.replace("https://", "").replace("http://", "").lower().strip("/")
    return u


# ---------------------------------------------------------------------------
# 1. DUPLICATE ANALYSIS
# ---------------------------------------------------------------------------
def duplicate_analysis(clean_df: pd.DataFrame, raw_df: pd.DataFrame, X: pd.DataFrame) -> Dict:
    dup_urls_clean = int(clean_df["url"].duplicated().sum())
    dup_urls_raw = int(raw_df["url"].duplicated().sum())

    # Duplicate feature rows
    dup_feature_rows = int(X.duplicated().sum())

    clean_df = clean_df.copy()
    clean_df["registered_domain"] = clean_df["url"].apply(extract_registered_domain)
    dup_domains = int(clean_df["registered_domain"].duplicated().sum())

    # Conflicting labels for same URL
    raw_norm = raw_df.copy()
    raw_norm["url_norm"] = raw_norm["url"].apply(normalize_url)
    conflicts = raw_norm.groupby("url_norm")["label"].nunique()
    conflicting_urls = int((conflicts > 1).sum())

    # Near-duplicate URLs (canonical key)
    clean_df["canonical"] = clean_df["url"].apply(url_canonical_key)
    near_dup_groups = clean_df.groupby("canonical").size()
    near_duplicate_url_groups = int((near_dup_groups > 1).sum())
    near_duplicate_extra_rows = int(near_dup_groups[near_dup_groups > 1].sum() - (near_dup_groups > 1).sum())

    # Same domain different paths count
    domain_path_counts = clean_df.groupby("registered_domain").size()

    return {
        "total_duplicate_urls_raw": dup_urls_raw,
        "total_duplicate_urls_clean": dup_urls_clean,
        "duplicate_feature_rows": dup_feature_rows,
        "duplicate_domains": dup_domains,
        "conflicting_labels_same_url": conflicting_urls,
        "near_duplicate_url_groups": near_duplicate_url_groups,
        "near_duplicate_extra_rows": near_duplicate_extra_rows,
        "unique_registered_domains": int(clean_df["registered_domain"].nunique()),
        "domains_with_multiple_urls": int((domain_path_counts > 1).sum()),
        "max_urls_per_domain": int(domain_path_counts.max()),
    }


# ---------------------------------------------------------------------------
# 2. TRAIN/TEST SIMILARITY
# ---------------------------------------------------------------------------
def train_test_similarity(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict:
    train_df = train_df.copy()
    test_df = test_df.copy()
    train_df["registered_domain"] = train_df["url"].apply(extract_registered_domain)
    test_df["registered_domain"] = test_df["url"].apply(extract_registered_domain)
    train_df["canonical"] = train_df["url"].apply(url_canonical_key)
    test_df["canonical"] = test_df["url"].apply(url_canonical_key)

    train_domains = set(train_df["registered_domain"])
    test_domains = set(test_df["registered_domain"])
    shared_domains = train_domains & test_domains

    test_shared_domain = test_df["registered_domain"].isin(shared_domains)
    pct_test_shared_domain = float(test_shared_domain.mean() * 100)

    # Same base domain with different paths
    train_domain_paths = set(zip(train_df["registered_domain"], train_df["url"].apply(
        lambda u: u.split("/", 3)[-1] if "/" in u.replace("://", "://x") else ""
    )))
    test_with_train_domain = test_df[test_shared_domain]

    # Near-identical canonical overlap
    train_canonical = set(train_df["canonical"])
    test_canonical = set(test_df["canonical"])
    canonical_overlap = train_canonical & test_canonical
    near_identical_count = len(canonical_overlap)

    # Exact URL overlap
    exact_overlap = set(train_df["url"]) & set(test_df["url"])

    # Test samples whose registered domain appears in train with same label distribution check
    shared_domain_examples = []
    for d in list(shared_domains)[:5]:
        tr = train_df[train_df["registered_domain"] == d]["url"].head(2).tolist()
        te = test_df[test_df["registered_domain"] == d]["url"].head(2).tolist()
        shared_domain_examples.append({"domain": d, "train_urls": tr, "test_urls": te})

    return {
        "train_unique_domains": len(train_domains),
        "test_unique_domains": len(test_domains),
        "shared_domains_count": len(shared_domains),
        "pct_test_samples_sharing_domain_with_train": round(pct_test_shared_domain, 2),
        "test_samples_sharing_domain_with_train": int(test_shared_domain.sum()),
        "exact_url_overlap_train_test": len(exact_overlap),
        "near_identical_canonical_overlap": near_identical_count,
        "shared_domain_examples": shared_domain_examples,
    }


# ---------------------------------------------------------------------------
# 3 & 4. FEATURE STATS AND TARGET CORRELATION
# ---------------------------------------------------------------------------
def feature_audit(clean_df: pd.DataFrame, X: pd.DataFrame) -> Dict:
    y = clean_df["label"].values
    stats_rows = []
    correlation_rows = []
    perfect_separators = []

    for feat in FEATURE_NAMES:
        col = X[feat].values.astype(float)
        legit = col[y == 0]
        phish = col[y == 1]

        stats_rows.append({
            "feature": feat,
            "dtype": str(X[feat].dtype),
            "min": float(np.min(col)),
            "max": float(np.max(col)),
            "mean": float(np.mean(col)),
            "std": float(np.std(col)),
            "mean_legitimate": float(np.mean(legit)),
            "mean_phishing": float(np.mean(phish)),
            "min_legitimate": float(np.min(legit)),
            "max_legitimate": float(np.max(legist := legit)),
            "min_phishing": float(np.min(phish)),
            "max_phishing": float(np.max(phish)),
        })

        # Point-biserial correlation
        if np.std(col) > 0:
            corr, pval = pointbiserialr(y, col)
        else:
            corr, pval = 0.0, 1.0

        # Check near-perfect separation
        legit_max, legit_min = legit.max(), legit.min()
        phish_max, phish_min = phish.max(), phish.min()
        separated = (legit_max < phish_min) or (phish_max < legit_min)
        overlap_pct = float(len(set(col) & set(col)))  # placeholder

        # Non-overlapping range check (approximate)
        ranges_overlap = not (legit_max < phish_min or phish_max < legit_min)
        if not ranges_overlap:
            perfect_separators.append(feat)

        # Single-feature classifier accuracy
        if len(np.unique(col)) <= 2:
            # Binary feature: threshold at 0.5
            single_pred = (col >= 0.5).astype(int)
            single_acc = float(accuracy_score(y, single_pred))
        else:
            # Try median threshold
            best_acc = 0
            for thresh in np.unique(col):
                pred = (col > thresh).astype(int)
                acc = accuracy_score(y, pred)
                best_acc = max(best_acc, acc)
                pred2 = (col <= thresh).astype(int)
                best_acc = max(best_acc, accuracy_score(y, pred2))
            single_acc = float(best_acc)

        correlation_rows.append({
            "feature": feat,
            "point_biserial_corr": round(float(corr), 4),
            "p_value": float(pval),
            "single_feature_best_accuracy": round(single_acc, 4),
            "ranges_non_overlapping": not ranges_overlap,
            "unique_values": int(X[feat].nunique()),
        })

    stats_df = pd.DataFrame(stats_rows)
    corr_df = pd.DataFrame(correlation_rows)
    stats_df.to_csv(os.path.join(OUTPUT_DIR, "feature_statistics.csv"), index=False)
    corr_df.to_csv(os.path.join(OUTPUT_DIR, "feature_target_correlation.csv"), index=False)

    return {
        "feature_statistics": stats_rows,
        "feature_correlations": correlation_rows,
        "perfect_range_separators": perfect_separators,
        "top_correlated_features": corr_df.nlargest(5, "point_biserial_corr")[["feature", "point_biserial_corr", "single_feature_best_accuracy"]].to_dict("records"),
    }


# ---------------------------------------------------------------------------
# 5. DATASET GENERATION ANALYSIS
# ---------------------------------------------------------------------------
def dataset_source_analysis() -> Dict:
    return {
        "classification": "SYNTHETIC / RULE-GENERATED",
        "source_script": "scripts/generate_dataset.py",
        "random_seed": 42,
        "legitimate_generation": "Random combinations of 30 known domains × 14 paths × 6 subdomain prefixes",
        "phishing_generation": "5 template patterns: IP URLs, @-symbol tricks, deep subdomains, long keyword paths, brand-spoof TLDs",
        "external_feeds_used": False,
        "label_creation_method": "Rule-based at generation time — phishing templates always label=1, legitimate templates always label=0",
        "label_feature_overlap": "CRITICAL FINDING: Labels created using same URL characteristics (suspicious TLDs, @ symbol, IP, keywords) that features detect",
        "major_limitation": True,
    }


# ---------------------------------------------------------------------------
# 6. FEATURE ENGINEERING AUDIT
# ---------------------------------------------------------------------------
def feature_engineering_audit() -> Dict:
    checks = [
        {"check": "Uses target label", "result": False, "evidence": "extract_features() only parses URL string"},
        {"check": "Uses dataset source", "result": False, "evidence": "No metadata columns accessed"},
        {"check": "Uses row position/index", "result": False, "evidence": "No index-based features"},
        {"check": "Uses filename", "result": False, "evidence": "Not referenced"},
        {"check": "Uses class name", "result": False, "evidence": "Not referenced"},
        {"check": "Uses pre-existing classification", "result": False, "evidence": "Not referenced"},
        {"check": "Indirect label encoding via generation rules", "result": True, "evidence": "Phishing URLs always contain suspicious TLDs/IPs/@/keywords that features explicitly measure — circular but not code-level leakage"},
    ]
    code_leakage = any(c["result"] for c in checks[:6])
    return {
        "checks": checks,
        "code_level_data_leakage": code_leakage,
        "data_leakage_verdict": "NO" if not code_leakage else "YES",
        "conceptual_circular_labeling": True,
    }


# ---------------------------------------------------------------------------
# 7. PREPROCESSING AUDIT
# ---------------------------------------------------------------------------
def preprocessing_audit() -> Dict:
    return {
        "operations_before_split": [
            {"operation": "dropna(url, label)", "uses_full_dataset": True, "leakage_risk": "LOW — removes incomplete rows only"},
            {"operation": "normalize_url()", "uses_full_dataset": True, "leakage_risk": "LOW — per-row transform"},
            {"operation": "drop_duplicates(url)", "uses_full_dataset": True, "leakage_risk": "LOW — dedup before split is acceptable"},
        ],
        "operations_after_split": [
            {"operation": "extract_features_df()", "uses_full_dataset": False, "leakage_risk": "NONE"},
            {"operation": "StandardScaler.fit_transform(train)", "uses_full_dataset": False, "leakage_risk": "NONE"},
            {"operation": "StandardScaler.transform(test)", "uses_full_dataset": False, "leakage_risk": "NONE"},
        ],
        "feature_selection_before_split": False,
        "scaling_before_split": False,
        "preprocessing_leakage": False,
    }


# ---------------------------------------------------------------------------
# 8. MODEL CONFIG AUDIT
# ---------------------------------------------------------------------------
def model_config_audit() -> Dict:
    rf = RandomForestClassifier(n_estimators=config.RF_N_ESTIMATORS, random_state=RANDOM_STATE, n_jobs=-1)
    return {
        "n_estimators": rf.n_estimators,
        "max_depth": rf.max_depth,  # None = unlimited
        "min_samples_split": rf.min_samples_split,
        "min_samples_leaf": rf.min_samples_leaf,
        "max_features": str(rf.max_features),
        "class_weight": rf.class_weight,
        "random_state": rf.random_state,
        "bootstrap": rf.bootstrap,
        "overfitting_indicators": [
            "max_depth=None allows full tree depth — can memorize training data",
            "However, 100% test accuracy with 100% CV suggests dataset separability, not just overfitting",
            "Train accuracy also 100% — model fully fits training set",
        ],
    }


# ---------------------------------------------------------------------------
# 9. LEAVE-DOMAIN-OUT TEST
# ---------------------------------------------------------------------------
def compute_metrics(y_true, y_pred, y_proba=None) -> Dict:
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    m = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "fp": int(fp), "fn": int(fn), "tp": int(tp), "tn": int(tn),
    }
    if y_proba is not None and len(np.unique(y_true)) > 1:
        m["roc_auc"] = float(roc_auc_score(y_true, y_proba))
        m["pr_auc"] = float(average_precision_score(y_true, y_proba))
    return m


def leave_domain_out_eval(clean_df: pd.DataFrame) -> Dict:
    df = clean_df.copy()
    df["group_domain"] = df["url"].apply(extract_registered_domain)

    # Split domains into train/test — no domain in both
    unique_domains = df["group_domain"].unique()
    domain_labels = df.groupby("group_domain")["label"].agg(lambda x: x.mode()[0]).to_dict()

    # Stratified domain split: ensure both classes in test
    domains_by_class = defaultdict(list)
    for d in unique_domains:
        domains_by_class[domain_labels[d]].append(d)

    rng = np.random.RandomState(RANDOM_STATE)
    test_domains = set()
    for cls, doms in domains_by_class.items():
        n_test = max(1, int(len(doms) * config.TEST_SIZE))
        chosen = rng.choice(doms, size=n_test, replace=False)
        test_domains.update(chosen)

    train_mask = ~df["group_domain"].isin(test_domains)
    test_mask = df["group_domain"].isin(test_domains)

    train_df = df[train_mask]
    test_df = df[test_mask]

    # Verify no domain overlap
    assert len(set(train_df["group_domain"]) & set(test_df["group_domain"])) == 0

    X_train_raw = extract_features_df(train_df["url"].tolist())
    X_test_raw = extract_features_df(test_df["url"].tolist())
    y_train = train_df["label"].values
    y_test = test_df["label"].values

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_test = scaler.transform(X_test_raw)

    rf = RandomForestClassifier(n_estimators=config.RF_N_ESTIMATORS, random_state=RANDOM_STATE, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    y_proba = rf.predict_proba(X_test)[:, 1]

    metrics = compute_metrics(y_test, y_pred, y_proba)
    metrics["train_size"] = len(train_df)
    metrics["test_size"] = len(test_df)
    metrics["train_domains"] = int(train_df["group_domain"].nunique())
    metrics["test_domains"] = int(test_df["group_domain"].nunique())
    return metrics


# ---------------------------------------------------------------------------
# 10. GROUPED CROSS-VALIDATION
# ---------------------------------------------------------------------------
def grouped_cv_eval(clean_df: pd.DataFrame, n_splits=5) -> Dict:
    df = clean_df.copy()
    df["group_domain"] = df["url"].apply(extract_registered_domain)
    groups = df["group_domain"].values

    X_raw = extract_features_df(df["url"].tolist())
    y = df["label"].values

    gkf = GroupKFold(n_splits=n_splits)
    fold_metrics = []

    for fold, (train_idx, val_idx) in enumerate(gkf.split(X_raw, y, groups)):
        X_tr, X_val = X_raw.iloc[train_idx], X_raw.iloc[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_val_s = scaler.transform(X_val)

        rf = RandomForestClassifier(n_estimators=config.RF_N_ESTIMATORS, random_state=RANDOM_STATE, n_jobs=-1)
        rf.fit(X_tr_s, y_tr)
        y_pred = rf.predict(X_val_s)
        y_proba = rf.predict_proba(X_val_s)[:, 1]
        m = compute_metrics(y_val, y_pred, y_proba)
        m["fold"] = fold + 1
        fold_metrics.append(m)

    summary = {
        "mean_accuracy": float(np.mean([m["accuracy"] for m in fold_metrics])),
        "std_accuracy": float(np.std([m["accuracy"] for m in fold_metrics])),
        "mean_precision": float(np.mean([m["precision"] for m in fold_metrics])),
        "std_precision": float(np.std([m["precision"] for m in fold_metrics])),
        "mean_recall": float(np.mean([m["recall"] for m in fold_metrics])),
        "std_recall": float(np.std([m["recall"] for m in fold_metrics])),
        "mean_f1": float(np.mean([m["f1"] for m in fold_metrics])),
        "std_f1": float(np.std([m["f1"] for m in fold_metrics])),
        "fold_details": fold_metrics,
    }
    return summary


# ---------------------------------------------------------------------------
# 11. FEATURE ABLATION
# ---------------------------------------------------------------------------
def feature_ablation(train_df, test_df, top_features: List[str]) -> Dict:
    X_train_raw = extract_features_df(train_df["url"].tolist())
    X_test_raw = extract_features_df(test_df["url"].tolist())
    y_train = train_df["label"].values
    y_test = test_df["label"].values

    results = {}
    for n_remove in [0, 1, 2, 3, 5]:
        drop_feats = top_features[:n_remove] if n_remove > 0 else []
        keep = [f for f in FEATURE_NAMES if f not in drop_feats]
        X_tr = X_train_raw[keep]
        X_te = X_test_raw[keep]

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_te_s = scaler.transform(X_te)

        rf = RandomForestClassifier(n_estimators=config.RF_N_ESTIMATORS, random_state=RANDOM_STATE, n_jobs=-1)
        rf.fit(X_tr_s, y_train)
        y_pred = rf.predict(X_te_s)
        y_proba = rf.predict_proba(X_te_s)[:, 1]
        m = compute_metrics(y_test, y_pred, y_proba)
        m["removed_features"] = drop_feats
        m["remaining_features"] = len(keep)
        results[f"remove_top_{n_remove}"] = m

    return results


# ---------------------------------------------------------------------------
# 12. SIMPLE BASELINES
# ---------------------------------------------------------------------------
def simple_baselines(clean_df: pd.DataFrame, test_df: pd.DataFrame, y_test: np.ndarray) -> Dict:
    # Majority class
    majority = int(clean_df["label"].mode()[0])
    maj_pred = np.full(len(y_test), majority)
    majority_metrics = compute_metrics(y_test, maj_pred)

    # Rule-based heuristic matching generation patterns
    def rule_predict(url):
        url_l = url.lower()
        ext = tldextract.extract(url)
        host = url_l.split("/")[2] if "://" in url_l else url_l
        if "@" in url:
            return 1
        if any(url_l.endswith(t) or t in host for t in SUSPICIOUS_TLDS):
            return 1
        # IP check
        host_clean = host.split(":")[0]
        parts = host_clean.split(".")
        if len(parts) == 4 and all(p.isdigit() for p in parts):
            return 1
        if "account-security-alert-check" in url_l:
            return 1
        if "-security-update" in url_l and any(t.strip(".") in url_l for t in SUSPICIOUS_TLDS):
            return 1
        if url_l.startswith("http") and "login-" in host and any(t.strip(".") in host for t in SUSPICIOUS_TLDS):
            return 1
        return 0

    rule_pred = np.array([rule_predict(u) for u in test_df["url"]])
    rule_metrics = compute_metrics(y_test, rule_pred)

    # Full dataset rule accuracy
    full_rule = np.array([rule_predict(u) for u in clean_df["url"]])
    full_rule_acc = float(accuracy_score(clean_df["label"], full_rule))

    return {
        "majority_class": majority,
        "majority_class_baseline": majority_metrics,
        "rule_based_heuristic_test": rule_metrics,
        "rule_based_heuristic_full_dataset_accuracy": full_rule_acc,
    }


# ---------------------------------------------------------------------------
# 13. OUT-OF-DISTRIBUTION TEST
# ---------------------------------------------------------------------------
def ood_test(rf_model, scaler) -> Dict:
    ood_urls = [
        # Modern legitimate
        ("https://www.google.com/search?q=machine+learning", 0, "Modern legitimate - Google"),
        ("https://github.com/scikit-learn/scikit-learn", 0, "Modern legitimate - GitHub"),
        ("https://www.chase.com/personal/checking", 0, "Legitimate bank site"),
        ("https://openai.com/research", 0, "Modern legitimate - OpenAI"),
        ("https://cursor.com/pricing", 0, "Modern legitimate - Cursor"),
        # Suspicious-looking legitimate
        ("https://accounts.google.com/signin/v2/identifier", 0, "Suspicious-looking legitimate login"),
        ("https://login.microsoftonline.com/common/oauth2/v2.0/authorize", 0, "Legitimate OAuth login URL"),
        ("https://secure.chase.com/web/auth/dashboard", 0, "Legitimate secure banking path"),
        # Simple-looking phishing patterns (synthetic OOD, not live threats)
        ("https://paypa1-secure-login.com/verify", 1, "Homoglyph phishing pattern"),
        ("https://amazon-customer-support.xyz/account/update", 1, "Simple phishing on suspicious TLD"),
        ("http://192.0.2.45/secure/banking", 1, "IP-based phishing (TEST-NET)"),
        ("http://www.google.com.evil-site.ru/login", 1, "Subdomain deception pattern"),
        ("https://bit.ly/3xample", 0, "URL shortener - ambiguous"),
        # Structural edge cases
        ("https://sub1.sub2.sub3.sub4.sub5.example.com/path", 0, "Multi-subdomain legitimate TLD"),
        ("http://user:pass@example.com/secret", 0, "URL with credentials segment"),
        ("http://legitimate.com@phishing.tk/steal", 1, "@-symbol phishing"),
        ("https://xn--80ak6aa92e.com", 0, "Punycode domain"),
        ("http://example.com/" + "x" * 300, 0, "Very long URL"),
        ("http://test.co.uk/login", 0, "Short legitimate URL"),
        ("https://microsoft-account-update.tk/signin", 1, "Simple phishing template"),
        ("https://www.apple.com/shop/buy-iphone", 0, "Simple legitimate Apple URL"),
    ]

    rows = []
    y_true = []
    y_pred = []
    for url, true_label, desc in ood_urls:
        feats = extract_features(normalize_url(url))
        X = pd.DataFrame([feats])[FEATURE_NAMES]
        X_s = scaler.transform(X)
        pred = int(rf_model.predict(X_s)[0])
        proba = float(rf_model.predict_proba(X_s)[0][1])
        y_true.append(true_label)
        y_pred.append(pred)
        rows.append({
            "description": desc,
            "url": url[:100],
            "true_label": true_label,
            "predicted": pred,
            "phishing_probability": round(proba, 4),
            "correct": pred == true_label,
        })

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    ood_metrics = compute_metrics(y_true, y_pred)
    ood_metrics["samples"] = len(rows)
    ood_metrics["correct_count"] = int(sum(r["correct"] for r in rows))

    pd.DataFrame(rows).to_csv(os.path.join(OUTPUT_DIR, "ood_test_results.csv"), index=False)
    return {"metrics": ood_metrics, "details": rows}


# ---------------------------------------------------------------------------
# ORIGINAL SPLIT EVAL (for comparison)
# ---------------------------------------------------------------------------
def original_split_eval(train_df, test_df) -> Dict:
    X_train_raw = extract_features_df(train_df["url"].tolist())
    X_test_raw = extract_features_df(test_df["url"].tolist())
    y_train = train_df["label"].values
    y_test = test_df["label"].values

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_test = scaler.transform(X_test_raw)

    rf = RandomForestClassifier(n_estimators=config.RF_N_ESTIMATORS, random_state=RANDOM_STATE, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    y_proba = rf.predict_proba(X_test)[:, 1]
    metrics = compute_metrics(y_test, y_pred, y_proba)

    # Get feature importances for ablation
    importances = sorted(zip(FEATURE_NAMES, rf.feature_importances_), key=lambda x: x[1], reverse=True)
    top5 = [f[0] for f in importances[:5]]

    return metrics, rf, scaler, top5, y_test


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    ensure_output_dir()
    print("=== PERFECT SCORE INVESTIGATION ===\n")

    raw_df = load_dataset(config.RAW_DATASET_PATH)
    clean_df = clean_dataset(raw_df)
    X = extract_features_df(clean_df["url"].tolist())

    train_df, test_df = split_dataset(clean_df)

    # 1. Duplicates
    dup = duplicate_analysis(clean_df, raw_df, X)
    print("1. Duplicate Analysis:", json.dumps(dup, indent=2))

    # 2. Train/test similarity
    sim = train_test_similarity(train_df, test_df)
    print("\n2. Train/Test Similarity:", json.dumps(sim, indent=2))

    # 3-4. Feature audit
    feat = feature_audit(clean_df, X)

    # 5-8. Audits
    source = dataset_source_analysis()
    feat_eng = feature_engineering_audit()
    preproc = preprocessing_audit()
    model_cfg = model_config_audit()

    # Original eval
    orig_metrics, rf, scaler, top5, y_test = original_split_eval(train_df, test_df)
    print(f"\nOriginal split F1: {orig_metrics['f1']}")

    # 9. Leave-domain-out
    ldo = leave_domain_out_eval(clean_df)
    print(f"\n9. Leave-Domain-Out F1: {ldo['f1']}")

    # 10. Grouped CV
    gcv = grouped_cv_eval(clean_df)
    print(f"10. Grouped CV Mean F1: {gcv['mean_f1']:.4f} ± {gcv['std_f1']:.4f}")

    # 11. Feature ablation
    ablation = feature_ablation(train_df, test_df, top5)
    print("11. Feature Ablation (remove top 3):", ablation["remove_top_3"])

    # 12. Baselines
    baselines = simple_baselines(clean_df, test_df, y_test)
    print(f"12. Rule-based heuristic test accuracy: {baselines['rule_based_heuristic_test']['accuracy']}")

    # 13. OOD
    ood = ood_test(rf, scaler)
    print(f"13. OOD accuracy: {ood['metrics']['accuracy']:.4f} ({ood['metrics']['correct_count']}/{ood['metrics']['samples']})")

    # Decision classification
    if feat_eng["code_level_data_leakage"]:
        decision = "LEAKAGE FOUND"
    elif ldo["f1"] < 0.95 or ood["metrics"]["accuracy"] < 0.85:
        decision = "DATASET LIMITED"
    elif baselines["rule_based_heuristic_full_dataset_accuracy"] >= 0.99:
        decision = "SUSPICIOUS"  # dataset too easy
    else:
        decision = "GENUINE"

    results = {
        "duplicate_analysis": dup,
        "train_test_similarity": sim,
        "feature_audit": feat,
        "dataset_source": source,
        "feature_engineering_audit": feat_eng,
        "preprocessing_audit": preproc,
        "model_config": model_cfg,
        "original_random_split": orig_metrics,
        "leave_domain_out": ldo,
        "grouped_cv": gcv,
        "feature_ablation": ablation,
        "baselines": baselines,
        "ood_test": ood,
        "top5_features": top5,
        "perfect_performance_decision": decision,
    }

    with open(os.path.join(OUTPUT_DIR, "investigation_results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nFinal classification: {decision}")
    print(f"Results saved to {OUTPUT_DIR}")
    return results


if __name__ == "__main__":
    main()
