# Perfect Score Investigation Report

**Project:** Machine Learning Based Phishing URL Detection and Risk Analysis System  
**Investigation Date:** 2026-08-08  
**Investigation Script:** `scripts/perfect_score_investigation.py`  
**Production Model Modified:** No  
**Supporting Data:** `investigation_outputs/`

---

## 1. Executive Summary

The Random Forest classifier achieved **100% on every metric** (accuracy, precision, recall, F1, ROC AUC, PR AUC) with zero false positives and zero false negatives on the held-out test set. Five-fold stratified cross-validation also reported mean F1 = 1.0000 with standard deviation 0.0000.

This investigation examined whether that result reflects genuine model strength or an artifact of the dataset and evaluation pipeline.

**Conclusion:** The perfect score is **not** caused by code-level data leakage or train/test URL contamination. It is caused by a **synthetic, rule-generated dataset** where phishing and legitimate URLs follow rigid, non-overlapping templates that align directly with the 16 engineered features. A simple rule-based heuristic achieves identical 100% test accuracy without machine learning.

**Root cause classification (Section 14):** **B. Dataset is too easy** (primary), with contributing factors **D. Excessive duplicate/similar samples** and **E. Optimistic evaluation methodology** (64.55% of test URLs share a registered domain with training, though stricter domain-held-out evaluation still yields 100%).

**Final status:** `DATASET LIMITED`

---

## 2. Duplicate Analysis

| Metric | Value |
|:---|:---:|
| **Total duplicate URLs (raw, before cleaning)** | 265 |
| **Total duplicate URLs (cleaned)** | 0 |
| **Duplicate feature rows** | 1,219 (70.3% of 1,735 cleaned samples) |
| **Duplicate registered domains** | 1,067 domain repetitions across 668 unique domains |
| **Conflicting labels (same URL, different label)** | 0 |
| **Near-duplicate URL groups** (http/https or trailing-slash variants) | 104 groups (106 extra rows) |
| **Unique registered domains** | 668 |
| **Domains with multiple URL paths** | 84 |
| **Maximum URLs per single domain** | 36 |

### Interpretation

- **265 raw duplicates (13.25%)** were removed during `clean_dataset()` — all had consistent labels.
- **Zero conflicting labels** — no URL appears with both label=0 and label=1.
- **1,219 duplicate feature rows (70.3%)** — the legitimate URL generator uses only 30 domains × 14 paths × 6 subdomain prefixes, producing many URLs that map to identical 16-dimensional feature vectors even when the URL strings differ slightly.
- **Near-duplicates** (104 groups) are primarily `http://` vs `https://` variants that differ only in the `is_https` feature.

This high feature duplication inflates the effective training signal: the model sees far fewer unique feature patterns than the row count suggests.

---

## 3. Train/Test Similarity

| Metric | Value |
|:---|:---:|
| Train unique registered domains | 548 |
| Test unique registered domains | 173 |
| **Shared domains (appear in both train and test)** | 53 |
| **Test samples sharing a domain with training** | 224 / 347 = **64.55%** |
| Exact URL overlap (train ∩ test) | 0 |
| Near-identical canonical overlap (scheme-stripped) | 34 |

### Examples of Shared-Domain Train/Test Pairs

| Domain | Training URLs | Test URLs |
|:---|:---|:---|
| `linkedin.com` | `https://support.linkedin.com/docs/guide` | `https://blog.linkedin.com/` |
| `paypal-security-update.top` | `https://paypal-security-update.top/signin` | `http://paypal-security-update.top/signin` |
| `account-security-alert-check.xyz` | Multiple brand subdomains | Different brand subdomains, same template |

### Are Test URLs Derived from Training URLs?

For **legitimate URLs**, yes — test and train URLs from the same domain (e.g., `google.com`, `linkedin.com`) are different paths/subdomains drawn from the **same generation template pool**. They are not independent draws from the real internet.

For **phishing URLs**, test samples on shared domains (e.g., `account-security-alert-check.xyz`) use the same structural template with different brand keywords — the model learns the template, not a generalizable phishing concept.

**64.55% of test samples share a registered domain with training.** This makes the random stratified split optimistic compared to a real deployment scenario where entirely new domains appear at test time.

---

## 4. Label Leakage Audit

### Feature Statistics by Class

| Feature | Type | Min | Max | Mean | Std | Legit Mean | Phish Mean | Legit Range | Phish Range | Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| `url_length` | int | 16 | 104 | 48.76 | 23.59 | 35.81 | 61.57 | [16, 57] | [23, 104] | Partial separation |
| `hostname_length` | int | 7 | 70 | 22.09 | 14.52 | 15.13 | 28.99 | [7, 25] | [10, 70] | Partial separation |
| `path_length` | int | 0 | 79 | 17.15 | 19.70 | 11.46 | 22.78 | [0, 21] | [5, 79] | Partial separation |
| `count_dots` | int | 1 | 5 | 2.36 | 1.21 | 1.84 | 2.89 | [1, 2] | [1, 5] | **Legit max < Phish min for value ≥3** |
| `count_hyphens` | int | 0 | 4 | 0.96 | 1.35 | 0.13 | 1.79 | [0, 2] | [0, 4] | Strong separation |
| `count_at` | int | 0 | 1 | 0.12 | 0.32 | 0.00 | 0.23 | **[0, 0]** | [0, 1] | **Legit always 0** |
| `count_question` | int | 0 | 1 | 0.16 | 0.36 | 0.08 | 0.23 | [0, 1] | [0, 1] | Overlapping |
| `count_equals` | int | 0 | 1 | 0.16 | 0.36 | 0.08 | 0.23 | [0, 1] | [0, 1] | Overlapping |
| `count_slash` | int | 2 | 6 | 3.50 | 0.80 | 3.75 | 3.25 | [2, 6] | [3, 4] | Partial separation |
| `count_percent` | int | 0 | 0 | 0.00 | 0.00 | 0.00 | 0.00 | [0, 0] | [0, 0] | Dead feature |
| `count_digits` | int | 0 | 12 | 2.87 | 3.89 | 0.87 | 4.85 | [0, 6] | [0, 12] | Overlapping |
| `count_letters` | int | 8 | 83 | 36.76 | 19.81 | 27.99 | 45.43 | [12, 48] | [8, 83] | Overlapping |
| `has_ip` | int | 0 | 1 | 0.11 | 0.31 | 0.00 | 0.22 | **[0, 0]** | [0, 1] | **Legit always 0** |
| `is_https` | int | 0 | 1 | 0.69 | 0.46 | 0.89 | 0.49 | [0, 1] | [0, 1] | Overlapping |
| `num_subdomains` | int | 0 | 3 | 0.77 | 0.94 | 0.84 | 0.69 | [0, 1] | [0, 3] | Partial separation |
| `has_suspicious_keyword` | int | 0 | 1 | 0.64 | 0.48 | 0.32 | 0.96 | [0, 1] | [0, 1] | Strong bias |

### Features That Almost Perfectly Encode the Label

No single feature achieves 100% accuracy alone, but combinations of generation rules map cleanly to features:

| Feature | Single-Feature Best Accuracy | Point-Biserial r | Notes |
|:---|:---:|:---:|:---|
| `has_suspicious_keyword` | 81.79% | 0.6615 | 95.8% of phishing URLs have keyword=1 |
| `count_hyphens` | 85.71% | 0.6165 | Phishing mean 1.79 vs legit 0.13 |
| `count_dots` | 84.15% | 0.4336 | Legit URLs have ≤2 dots; phishing templates use 3–5 |
| `count_at` | 61.44% | 0.3621 | `@` appears **only** in phishing (23% of phishing) |
| `has_ip` | 60.81% | 0.3509 | IP appears **only** in phishing (22% of phishing) |

**Critical finding:** `count_at` and `has_ip` are **always 0 for legitimate URLs** in this dataset because the generator never creates legitimate URLs with `@` or IP hostnames. This is not leakage in code, but the **label generation rules directly determine feature values**.

---

## 5. Feature Leakage Audit (Target Correlation)

Full correlation table: `investigation_outputs/feature_target_correlation.csv`

### Top 5 Features by Target Correlation

| Rank | Feature | Correlation | Single-Feature Accuracy |
|:---:|:---|:---:|:---:|
| 1 | `has_suspicious_keyword` | 0.6615 | 81.79% |
| 2 | `count_hyphens` | 0.6165 | 85.71% |
| 3 | `url_length` | 0.5459 | 73.95% |
| 4 | `count_digits` | 0.5106 | 74.93% |
| 5 | `hostname_length` | 0.4771 | 77.81% |

### Categorical Feature Class Distributions

| Feature | P(feature=1 \| Legit) | P(feature=1 \| Phishing) |
|:---|:---:|:---:|
| `has_suspicious_keyword` | 32.3% | 95.8% |
| `has_ip` | 0.0% | 22.0% |
| `count_at` | 0.0% | 23.3% |
| `is_https` | 89.2% | 48.5% |

No feature uses the target label, row index, filename, or pre-existing classification directly. **Code-level DATA LEAKAGE = NO.**

However, **conceptual circular labeling exists**: phishing labels are assigned at generation time using URL patterns (suspicious TLDs, `@`, IP, keywords, hyphens) that are exactly what the features measure.

---

## 6. Preprocessing Audit

### Operations Before Train/Test Split

| Operation | Uses Full Dataset? | Leakage Risk |
|:---|:---:|:---|
| `dropna(url, label)` | Yes | LOW |
| `normalize_url()` (per-row) | Yes | LOW |
| `drop_duplicates(url)` | Yes | LOW — standard practice |

### Operations After Split

| Operation | Uses Train Only? | Leakage Risk |
|:---|:---:|:---|
| `extract_features_df()` | Per-split | NONE |
| `StandardScaler.fit()` | Train only | NONE |
| `StandardScaler.transform(test)` | Applies train stats | NONE |

| Check | Result |
|:---|:---|
| Scaling before split | **No** |
| Feature selection before split | **No** |
| Imputation using global stats | **No** |
| Feature generation using labels | **No** |
| **Preprocessing leakage** | **NO** |

---

## 7. Dataset Source

| Property | Finding |
|:---|:---|
| **Dataset type** | **Synthetic / rule-generated** |
| **Source script** | `scripts/generate_dataset.py` |
| **Random seed** | 42 |
| **External phishing feeds** | **Not used** (no PhishTank, OpenPhish, etc.) |
| **Legitimate source** | Random combinations from 30 hardcoded domains |
| **Phishing source** | 5 hardcoded template patterns |
| **Label assignment** | Rule-based at generation: template type → label |

### Generation Rules vs Features (Circular Labeling)

| Phishing Template (from generator) | Feature Signal |
|:---|:---|
| Pattern 1: Raw IP URLs | `has_ip=1` |
| Pattern 2: `@` symbol trick | `count_at=1` |
| Pattern 3: Deep subdomains + hyphens | `count_dots≥3`, `count_hyphens≥2`, `num_subdomains≥2` |
| Pattern 4: `login-XXXX.tld` + long path | `count_digits`, `count_hyphens`, suspicious TLD |
| Pattern 5: `brand-security-update.tld` | `count_hyphens`, suspicious TLD, `has_suspicious_keyword=1` |
| Legitimate: known `.com/.org` domains | Low dots, low hyphens, no `@`, no IP |

**Major limitation confirmed:** Labels were created using the same URL characteristics the model learns to detect. This is the primary explanation for perfect performance.

---

## 8. Random Forest Configuration

| Parameter | Value | Notes |
|:---|:---|:---|
| `n_estimators` | 100 | Default project config |
| `max_depth` | **None (unlimited)** | Trees can grow until pure leaves — overfitting-capable |
| `min_samples_split` | 2 | Minimum — allows deep splits |
| `min_samples_leaf` | 1 | Minimum — allows single-sample leaves |
| `max_features` | `"sqrt"` | Standard default |
| `class_weight` | None | Not needed — balanced classes |
| `random_state` | 42 | Reproducible |
| `bootstrap` | True | Standard bagging |

### Overfitting Assessment

- Train accuracy = 100%, Test accuracy = 100%, Grouped CV = 100% → performance is **not** train-only overfitting.
- Unlimited depth *could* memorize, but the dataset is **linearly separable in feature space** by design, so even a Decision Tree with default settings achieves 100%.
- Model complexity is **not** the cause of perfect scores; dataset separability is.

---

## 9. Domain-Based Evaluation (Leave-Domain-Out)

Strict evaluation: **no registered domain may appear in both training and testing.**

| Metric | Random Split (Original) | Leave-Domain-Out |
|:---|:---:|:---:|
| Accuracy | 1.0000 | **1.0000** |
| Precision | 1.0000 | **1.0000** |
| Recall | 1.0000 | **1.0000** |
| F1 | 1.0000 | **1.0000** |
| ROC AUC | 1.0000 | **1.0000** |
| PR AUC | 1.0000 | **1.0000** |
| False Positives | 0 | **0** |
| False Negatives | 0 | **0** |
| Train size | 1,388 | 1,378 |
| Test size | 347 | 357 |
| Train domains | — | 535 |
| Test domains | — | 133 |

**Key finding:** Perfect performance **persists** even when entire domains are held out. This rules out train/test domain overlap as the primary cause. The separability is at the **template/rule level**, not the domain level — unseen domains from the same generation templates are still perfectly classified.

---

## 10. Grouped Cross-Validation

**Method:** 5-fold `GroupKFold` grouped by registered domain (no domain in both train and validation within a fold).

| Metric | Mean | Std Dev |
|:---|:---:|:---:|
| Accuracy | 1.0000 | 0.0000 |
| Precision | 1.0000 | 0.0000 |
| Recall | 1.0000 | 0.0000 |
| **F1** | **1.0000** | **0.0000** |

All 5 folds: FP=0, FN=0.

Grouped CV confirms perfect performance is **stable across domain partitions** — not a lucky random split.

---

## 11. Feature Ablation

Top 5 features by Gini importance: `count_dots`, `count_hyphens`, `num_subdomains`, `hostname_length`, `has_suspicious_keyword`

| Features Removed | Remaining | Accuracy | F1 | FP | FN |
|:---|:---:|:---:|:---:|:---:|:---:|
| None (baseline) | 16 | 1.0000 | 1.0000 | 0 | 0 |
| Top 1 (`count_dots`) | 15 | 1.0000 | 1.0000 | 0 | 0 |
| Top 2 (+ `count_hyphens`) | 14 | 1.0000 | 1.0000 | 0 | 0 |
| Top 3 (+ `num_subdomains`) | 13 | 1.0000 | 1.0000 | 0 | 0 |
| Top 5 (+ `hostname_length`, `has_suspicious_keyword`) | 11 | 1.0000 | 1.0000 | 0 | 0 |

**Removing the top 5 features still yields perfect performance.** The remaining 11 features (including `count_at`, `has_ip`, `count_digits`, `url_length`) carry sufficient signal because the dataset templates are so distinct.

---

## 12. Baseline Comparison

| Baseline | Accuracy | Precision | Recall | F1 | FP | FN |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Majority class** (always predict phishing) | 50.14% | 50.14% | 100% | 66.79% | 173 | 0 |
| **Rule-based heuristic** (TLD + `@` + IP + template patterns) | **100%** | **100%** | **100%** | **100%** | **0** | **0** |
| Rule-based on **full dataset** | **100%** | — | — | — | — | — |
| Random Forest (test set) | 100% | 100% | 100% | 100% | 0 | 0 |

The rule-based heuristic mirrors the dataset generation rules:

```
IF url contains '@' → phishing
IF hostname uses suspicious TLD (.tk, .ml, .ga, .xyz, etc.) → phishing
IF hostname is IP address → phishing
IF url matches template patterns (account-security-alert-check, login-NNNN.tld, brand-security-update.tld) → phishing
ELSE → legitimate
```

**The ML model is not learning anything beyond these generation rules.**

---

## 13. Unseen Dataset Test (Out-of-Distribution)

21 manually curated URLs **not present** in the original dataset. No URLs were executed — string analysis only.

| Metric | Value |
|:---|:---:|
| Accuracy | 95.24% (20/21) |
| Precision | 100% |
| Recall | 83.33% |
| F1 | 90.91% |
| False Positives | 0 |
| False Negatives | 1 |

### Misclassified Sample

| URL | True Label | Predicted | P(phishing) | Issue |
|:---|:---:|:---:|:---:|:---|
| `http://legitimate.com@phishing.tk/steal` | Phishing | **Legitimate** | 0.14 | `@`-symbol credential phishing missed |

### Correctly Handled OOD Cases

- Modern legitimate sites (Google, GitHub, Chase, OpenAI) → Legitimate ✓
- Suspicious-looking legitimate logins (Google accounts, Microsoft OAuth) → Legitimate ✓
- Homoglyph phishing (`paypa1-secure-login.com`) → Phishing ✓
- IP-based phishing (`192.0.2.45`) → Phishing ✓
- Subdomain deception (`google.com.evil-site.ru`) → Phishing ✓
- Simple phishing template (`.tk` TLD) → Phishing ✓

**OOD performance drops from 100% to 95.24%**, revealing a generalization gap on `@`-symbol attacks that the synthetic training data partially covers but the model fails to generalize on variant formats.

Full results: `investigation_outputs/ood_test_results.csv`

---

## 14. Root Cause of Perfect Score

### Classification (exactly one primary cause)

| Option | Applies? | Evidence |
|:---|:---:|:---|
| **A. Genuine strong performance** | **No** | OOD test fails; rule baseline matches ML exactly |
| **B. Dataset is too easy** | **Yes (PRIMARY)** | Synthetic templates map 1:1 to features; rule heuristic = 100% |
| **C. Hidden leakage** | **No** | No label in features, no train/test URL overlap, scaler isolated |
| **D. Excessive duplicate/similar samples** | **Yes (SECONDARY)** | 70.3% duplicate feature rows; 13.25% raw URL duplicates |
| **E. Optimistic evaluation methodology** | **Partial** | 64.55% test domain overlap, but domain-held-out still 100% |
| **F. Insufficient evidence** | **No** | Multiple independent tests confirm root cause |

### Root Cause Chain

```
scripts/generate_dataset.py
  → Phishing URLs built from 5 rigid templates (IP, @, subdomains, long paths, spoof TLD)
  → Legitimate URLs built from 30 known domains + standard paths
  → Labels assigned by template type (not real-world verification)
  → Feature extractor measures exactly these template characteristics
  → Dataset is linearly separable in 16-D feature space
  → ANY reasonable classifier achieves 100%
  → Random Forest perfect score is a dataset artifact, not ML achievement
```

---

## 15. Recommended Evaluation Method

For credible academic and security evaluation, replace or supplement the current approach with:

1. **Real-world dataset:** Combine PhishTank/OpenPhish (phishing) with Tranco top-1M or similar (legitimate).
2. **Domain-grouped splitting:** Use `GroupKFold` by registered domain for all reported metrics.
3. **Temporal split:** If timestamps available, train on older URLs, test on newer.
4. **Report rule baseline:** Always compare ML against simple heuristics — if they tie, ML adds no value on that dataset.
5. **OOD test set:** Maintain a held-out manual set of real-world URL patterns updated independently.
6. **Fix dataset generator:** Expand template diversity; add legitimate URLs with `@`, IP, and keywords; add phishing on `.com` TLDs.
7. **Do not report 100% as "excellent"** without domain-held-out and OOD validation.

---

## 16. Final Conclusion

The Random Forest model's perfect evaluation scores are **mathematically correct but scientifically meaningless** for assessing real-world phishing detection capability.

| Question | Answer |
|:---|:---|
| Is there code-level data leakage? | **No** |
| Is there train/test URL contamination? | **No** (0 exact overlaps) |
| Is the evaluation pipeline broken? | **No** — methodology is mostly correct |
| Why 100% accuracy? | **Synthetic dataset with rule-based labels that mirror feature definitions** |
| Does ML beat simple rules? | **No** — rule heuristic also achieves 100% |
| Does perfect score survive domain-held-out testing? | **Yes** — templates, not domains, drive separability |
| Does perfect score survive OOD testing? | **No** — drops to 95.24% (1 missed `@`-phishing) |
| Should the model be modified now? | **Not yet** — fix the dataset and evaluation first |

**Do not present 100% metrics to an external reviewer as evidence of a production-ready phishing detector.** Present them as proof that the pipeline runs correctly on a synthetic benchmark, with explicit limitations documented.

---

## Reproducibility

```bash
cd "/Users/krishnarawat/Desktop/Major Project"
python3 scripts/perfect_score_investigation.py
```

Outputs:
- `investigation_outputs/investigation_results.json`
- `investigation_outputs/feature_statistics.csv`
- `investigation_outputs/feature_target_correlation.csv`
- `investigation_outputs/ood_test_results.csv`

---

## FINAL STATUS

```
DATASET LIMITED
```

**Justification:** The perfect score is caused by a synthetic, rule-generated dataset with circular label-feature alignment. No code-level leakage was found, but the dataset does not represent real-world phishing complexity. The ML model learns generation templates, not generalizable phishing detection.
