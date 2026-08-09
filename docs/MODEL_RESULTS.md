# Model Evaluation Results

**System Architecture:** Random Forest Classifier  
**Evaluation Dataset Size:** Stratified Test Set  

## Performance Metrics

| Metric | Target | Model Result | Status |
|:---|:---|:---|:---|
| **Accuracy** | $\ge 90\%$ | **100.00%** | PASS |
| **Precision** | $\ge 90\%$ | **100.00%** | PASS |
| **Recall** | $\ge 90\%$ | **100.00%** | PASS |
| **F1 Score** | $\ge 0.90$ | **100.00%** | PASS |

## Confusion Matrix

```
                Predicted Legitimate (0)    Predicted Phishing (1)
Actual Legitimate (0)    173                       0
Actual Phishing (1)      0                         174
```

## Explainable Feature Importance (Gini Importance)

| Rank | Feature Name | Importance Weight |
|:---|:---|:---|
| 1 | `count_dots` | 0.2002 |
| 2 | `count_hyphens` | 0.1960 |
| 3 | `num_subdomains` | 0.1043 |
| 4 | `hostname_length` | 0.0960 |
| 5 | `has_suspicious_keyword` | 0.0905 |
| 6 | `count_digits` | 0.0872 |
| 7 | `count_letters` | 0.0639 |
| 8 | `url_length` | 0.0632 |
| 9 | `has_ip` | 0.0540 |
| 10 | `path_length` | 0.0220 |
| 11 | `is_https` | 0.0085 |
| 12 | `count_at` | 0.0056 |
| 13 | `count_slash` | 0.0051 |
| 14 | `count_equals` | 0.0022 |
| 15 | `count_question` | 0.0012 |
| 16 | `count_percent` | 0.0000 |
