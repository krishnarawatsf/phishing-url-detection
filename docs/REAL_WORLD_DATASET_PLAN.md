# Real-World Dataset Upgrade Plan

Status: planning only. No code changes yet.

## Goal

Upgrade the project from a synthetic baseline to a real-world phishing URL evaluation pipeline while preserving the current synthetic dataset as the **Synthetic Baseline Dataset**.

The current synthetic data stays intact for reference, regression testing, and classroom/viva demonstration. The new work adds a separate real-world evaluation path rather than replacing the existing baseline.

## Proposed Real-World Data Sources

### Phishing / malicious URL sources

1. **PhishTank**
   - Source: https://phishtank.org/
   - API/data access: verified phishing URLs with downloadable database files and API access.
   - Why it fits: community-verified phishing URLs with hourly updates and explicit per-URL metadata.
   - Documentation:
     - API information: https://phishtank.org/api_info.php
     - Developer info: https://phishtank.org/developer_info.php
     - Terms of use: https://phishtank.org/terms.php

2. **URLhaus**
   - Source: https://urlhaus.abuse.ch/
   - API/data access: malware URL database dumps, API, plain-text URL lists, and feeds.
   - Why it fits: public, security-focused, operationally maintained malicious URL source.
   - Documentation:
     - Community API: https://urlhaus.abuse.ch/api/
     - Feeds: https://urlhaus.abuse.ch/feeds/
     - About: https://urlhaus.abuse.ch/about/

3. **OpenPhish Academic Use Program**
   - Source: https://openphish.com/
   - Access model: application-based academic access.
   - Why it fits: real-time phishing feed plus archive, useful if academic approval is available.
   - Documentation:
     - Feed overview: https://openphish.com/phishing_feeds.html
     - Academic use: https://openphish.com/academic_use.html
     - Terms: https://www.openphish.com/terms.html

### Legitimate URL sources

1. **Tranco**
   - Source: https://tranco-list.eu/
   - Why it fits: research-oriented top-sites ranking with reproducible daily lists.
   - Use in this project: select legitimate domains from Tranco, then sample URLs from those domains.
   - Documentation: https://tranco-list.eu/

2. **Common Crawl URL Index**
   - Source: https://commoncrawl.org/url-index
   - Why it fits: free, large-scale URL index useful for harvesting legitimate URLs from popular domains.
   - Use in this project: pull clean, non-malicious URLs for the legitimate class after domain filtering.
   - Documentation:
     - URL Index: https://commoncrawl.org/url-index
     - Get Started: https://commoncrawl.org/get-started

## Licensing / Usage Considerations

### PhishTank

- Data is available for commercial use without charge, but the service is subject to terms of use and API usage limits.
- Use a descriptive user agent string.
- Do not assume the feed is a formal warranty of correctness; validate and deduplicate locally.

### URLhaus

- Community API is available under fair-use principles.
- Commercial or for-profit use may require a paid subscription.
- Respect fetch-rate guidance and submission policy.

### OpenPhish

- Community feed is free but limited and bound by terms of use.
- Academic use requires an application, attribution, and non-commercial use.
- Data sharing restrictions must be respected.

### Tranco

- Tranco is a research-oriented ranking.
- The site indicates that its default list integrates multiple providers, including data under different upstream licenses.
- Use Tranco for domain selection, not as a direct replacement for URL-level crawl data.

### Common Crawl

- Common Crawl data is free to access and download.
- The URL Index is suitable for bulk queries and reproducible sampling.
- For this project, use it only for legitimate URL harvesting and keep the crawl subset small enough for a Mac M3.

## Expected Dataset Size

Target scale for a Mac M3:

- Phishing URLs: 5,000 to 20,000
- Legitimate URLs: 5,000 to 20,000
- Total initial raw pool: 10,000 to 40,000 URLs

Recommended first milestone:

- 5,000 phishing
- 5,000 legitimate
- Keep the first real-world evaluation small enough to iterate quickly before scaling up.

## Cleaning Process

Planned pipeline:

1. **Raw ingestion**
   - Store source-specific raw exports separately.
   - Preserve source metadata such as feed name, access date, and retrieval method.

2. **Normalization**
   - Strip whitespace.
   - Standardize schemes where needed.
   - Normalize obvious URL formatting differences.

3. **Validation**
   - Remove empty or malformed entries.
   - Keep only HTTP/HTTPS URLs.
   - Filter obviously broken or blacklisted non-URL rows.

4. **Deduplication**
   - Remove exact duplicate URLs.
   - Remove duplicate normalized URLs.
   - Preserve one canonical row per unique normalized URL.

5. **Label harmonization**
   - `phishing = 1`
   - `legitimate = 0`
   - Keep source metadata so class origin remains traceable.

6. **Persist cleaned data**
   - Save a cleaned intermediate dataset before feature extraction.

## Deduplication Process

- Remove exact URL duplicates first.
- Remove canonical duplicates after normalization.
- Track duplicates by source and by registered domain.
- Keep one record per unique URL in the cleaned dataset.
- Prevent duplicate domains from leaking across train/test whenever the same domain is represented multiple times.

### Domain deduplication rule

- For legitimate URLs, treat the registered domain as the grouping unit.
- For phishing URLs, group by registered domain or full host when the domain itself is a malicious hosting domain that appears with multiple paths.
- If a group appears in the training set, do not split another sample from the same group into test unless the evaluation stage explicitly allows it.

## Feature Extraction

Preserve the existing feature extraction system initially.

- Reuse the current 16 lexical and structural URL features.
- Do not introduce new feature families in phase 1.
- Keep the extraction contract stable so model comparisons remain fair.

This preserves comparability with the current synthetic baseline and makes it easier to isolate the effect of real-world data quality.

## Dataset Pipeline

Planned flow:

`raw -> cleaned -> deduplicated -> feature extraction -> grouped split`

Operational notes:

- `raw`: source-specific exports from PhishTank, URLhaus, OpenPhish, Tranco, and Common Crawl
- `cleaned`: normalized, validated, and source-tagged rows
- `deduplicated`: canonical URL set with duplicate domains tracked
- `feature extraction`: existing 16-feature pipeline
- `grouped split`: domain-aware splitting to reduce leakage

## Train/Test Methodology

### Primary split

- Use a grouped train/test split.
- Split by registered domain where possible.
- Keep all URLs from the same domain group in the same split.
- Use stratification by label at the group level if the implementation supports it.

### Secondary validation

- Keep a small validation split from the training groups only.
- Use it for threshold tuning, not for final reporting.

### Why grouped splitting matters

Without domain grouping, the model can see nearly identical URLs from the same domain in both train and test, which inflates performance.

## Domain Grouping

Use a domain-aware grouping policy:

- Group on registered domain for standard web hosts.
- Group on full host for special cases such as IP-based URLs or malicious hostnames that repeat across many paths.
- Keep all members of one group in a single split.

This should prevent duplicate domains from appearing across train and test where appropriate.

## Model Comparison Methodology

Compare the following models on the same cleaned, grouped dataset:

1. Rule-based heuristic baseline
2. Logistic Regression
3. Decision Tree
4. Random Forest
5. XGBoost

### Fairness rules

- Use the same feature matrix for all ML models.
- Use the same train/test split for all models.
- Tune only on the training side.
- Do not let the test set influence model selection.

### Compute budget for Mac M3

- Prefer small-to-moderate parameter grids.
- Keep tree depth and estimator counts modest initially.
- Use parallelism only where it is stable and helpful.
- Avoid heavy cross-validation loops on very large data until the pipeline is proven.

## Evaluation Metrics

Report all of the following:

- Accuracy
- Precision
- Recall
- F1
- ROC AUC
- PR AUC
- False Positives
- False Negatives
- Confusion Matrix

### Reporting guidance

- For phishing detection, emphasize recall and false negatives alongside overall accuracy.
- Include per-class interpretation so the project does not rely on accuracy alone.

## OOD Testing

Add an unseen / out-of-distribution test set that is never used in training or model selection.

### OOD examples

- New phishing domains from a later time window
- New legitimate domains from a separate domain list
- URLs with structures not overrepresented in training
- Phishing URLs with different hosting patterns than the main training set

### OOD goal

- Measure how the current feature system behaves outside the distribution it was trained on.
- Confirm whether the model generalizes or only memorizes source-specific patterns.

## Expected Project Timeline

### Phase 1: Source review and acquisition
- 1 to 2 days
- Confirm access, terms, and retrieval method for each source

### Phase 2: Dataset assembly
- 1 to 2 days
- Pull raw feeds and build the raw dataset catalog

### Phase 3: Cleaning and deduplication
- 1 day
- Normalize URLs, remove duplicates, and validate label integrity

### Phase 4: Grouped split and feature extraction
- 1 day
- Build the domain-aware split and reuse the existing feature extractor

### Phase 5: Baseline evaluation
- 1 to 2 days
- Compare rule-based, Logistic Regression, Decision Tree, Random Forest, and XGBoost

### Phase 6: OOD evaluation and reporting
- 1 day
- Build the unseen test set and document limitations

## Risks and Limitations

1. **Data licensing constraints**
   - Some feeds are free for academic use only or require attribution and rate limits.

2. **Label noise**
   - Public phishing feeds can contain stale or partially verified URLs.

3. **Class imbalance**
   - Real-world phishing data may be far less balanced than the synthetic baseline.

4. **Domain leakage**
   - If grouped splitting is not strict, test metrics may still be inflated.

5. **OOD shift**
   - A model that scores well on in-distribution data may still fail on new hosting patterns.

6. **Compute constraints**
   - Large Common Crawl samples can exceed a Mac M3-friendly workflow if not downsampled carefully.

7. **Feature ceiling**
   - The current lexical feature set may be sufficient for baseline comparisons but may not capture richer real-world signals.

8. **Comparison fairness**
   - Model comparisons are only meaningful if every model sees the same split, same features, and same preprocessing.

## Approval Gate

This plan is intentionally non-implementational.

Do not modify the ML model, feature extractor, or training pipeline until this plan is approved.
