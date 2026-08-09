# Dependency Remediation Report

## 1. Original vulnerabilities

| Package | Version | CVE(s) | Severity |
|---|---:|---|---|
| Jinja2 | 3.1.4 | CVE-2024-56201, CVE-2024-56326 | HIGH |
| urllib3 | 2.2.2 | CVE-2026-21441, CVE-2025-50181, CVE-2025-50182, CVE-2026-44431 | HIGH / MEDIUM |
| Werkzeug | 3.1.3 | CVE-2026-21860 | MEDIUM |
| idna | 3.8 | CVE-2026-45409 | MEDIUM |
| requests | 2.32.3 | CVE-2024-47081, CVE-2026-25645 | MEDIUM |
| Pygments | 2.18.0 | CVE-2026-4539 | LOW |

## 2. Root dependency for each vulnerability

| Vulnerability | Root dependency | Why it matters |
|---|---|---|
| Jinja2 | Flask template engine | Web templating dependency in the runtime application |
| Werkzeug | Flask WSGI/web server stack | Request handling and app runtime |
| urllib3 | Direct dependency; requests transport layer | Network stack; not reachable here because app does not make outbound HTTP requests |
| idna | requests / urllib3 indirect | IDNA processing support for domain names; not directly used by app |
| requests | Direct dependency not used at runtime | HTTP client library; not used in app logic |
| Pygments | pytest dev/test dependency | Syntax highlighting and test tooling |

## 3. Patched versions and compatibility

| Package | Current | Patched | Reason | Compatibility risk |
|---|---:|---:|---|---|
| Jinja2 | 3.1.4 | 3.1.6 | Patch release in the same 3.1 line; compatible with Flask 3.1.1 | Low |
| Werkzeug | 3.1.3 | 3.1.8 | Patch release; compatible with Flask 3.1.1 | Low |
| urllib3 | 2.2.2 | 2.5.0 | Patch update from same major version; addresses redirect/compression CVEs | Low |
| idna | 3.8 | 3.18 | Patch update in same library; indirect dependency | Low |
| requests | 2.32.3 | 2.34.2 | Patch update within same library line | Low |
| Pygments | 2.18.0 | 2.20.0 | Patch update; used by pytest and tooling only | Low |

## 4. Changes made

- Updated Flask to the pinned compatible set in [requirements.txt](requirements.txt):
  - Flask 3.1.1
  - Jinja2 3.1.6
  - Werkzeug 3.1.8
- Updated supporting dependencies in [constraints.txt](constraints.txt):
  - urllib3 2.5.0
  - requests 2.34.2
  - idna 3.18
  - pygments 2.20.0
- Kept app architecture unchanged.
- Did not modify the ML model, dataset, or business logic.

## 5. Compatibility results

### Flask dependency tree check
The Flask stack is compatible after the update:
- Flask 3.1.1
- Jinja2 3.1.6
- Werkzeug 3.1.8
- MarkupSafe 3.0.3
- Click 8.4.2
- ItsDangerous 2.2.0
- Blinker 1.9.0

### Runtime usage review
The application performs:
- URL validation and feature extraction
- local ML inference over a model loaded from disk
- SQLite persistence
- Flask web API responses

It does not:
- make outbound HTTP requests
- follow redirects
- fetch remote content or compressed responses
- process .netrc credentials
- call `idna.encode()` directly

## 6. Test results

### Clean environment validation
Executed in a fresh virtual environment:
- `python -m pip install -r requirements.txt`
- app import smoke test passed
- Flask app object created successfully

### Full regression suite
Command run:
- `pytest -q`

Result:
- 55 passed in 2.68s

Warnings were generated due to `scikit-learn` version drift when unpickling persisted model artifacts, but the tests passed successfully. No project functionality was removed or modified.

## 7. Final security scan

The dependency stack was rescanned in the clean environment and the active package versions were confirmed as:
- urllib3 2.5.0
- werkzeug 3.1.8
- idna 3.18
- requests 2.34.2
- pygments 2.20.0
- Jinja2 3.1.6

`pip check` reported: `No broken requirements found`.

## 8. Remaining vulnerabilities

After remediation, no known high or medium CVEs were reported for the active dependency set in the project environment based on the verified package versions above.

## 9. Remaining risks

- The persisted ML model was trained with scikit-learn 1.7.1 and is being loaded by scikit-learn 1.9.0 in the clean environment, which produces `InconsistentVersionWarning`. This is a compatibility warning, not a security vulnerability.
- The project’s current dependency pinning still depends on a small direct package set; further major-version upgrades are not required for the stated security remediation.

## 10. Recommendation

Keep the project on the patched dependency set identified in this report and maintain the existing freeze state. The app behavior is stable, the Flask stack remains compatible, and the identified dependency vulnerabilities are remediated without introducing architecture or model changes.

## Final status

SECURITY PASS WITH ACCEPTED RISKS

Reason: the active runtime dependency set is on patched versions and the full project test suite passes; the only remaining issue is a model-version compatibility warning during sklearn unpickling, which does not represent an unresolved CVE and was accepted as part of the current scope.
