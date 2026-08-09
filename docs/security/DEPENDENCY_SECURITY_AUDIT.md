# Dependency Security Audit

## Scope
This project is a phishing URL detection web app built with Flask. The application validates user-provided URLs, extracts lexical features, and loads a pre-trained ML model for prediction. It does not perform outbound network requests to arbitrary sites, does not follow redirects from user-provided URLs, and does not download external content.

## Directly affected packages

| Package | Current state | Directly listed in requirements.txt? | Transitive? | Requires | Used by project? | Reachability | Patched compatible version |
|---|---|---:|---:|---|---|---|---|
| Jinja2 | 3.1.4 | Yes | No | Flask | Yes, template rendering in Flask | Yes, but only as web template engine; not direct input sink | 3.1.6 |
| Werkzeug | 3.1.3 | Yes | No | Flask | Yes, WSGI server and request handling | Yes, app server and request lifecycle | 3.1.8 |
| urllib3 | 2.2.2 | Yes | No | Direct dependency; also used by requests | Minimal; not directly used in application code | Low, since no outbound HTTP fetches are performed by this app | 2.5.0 |
| idna | 3.8 | Yes | Indirect via requests and urllib3 | requests / urllib3 | Indirect only | Low; project does not call idna directly | 3.18 |
| requests | 2.32.3 | Yes | No | Direct dependency | Not used in application logic | Low; no external HTTP client usage in app | 2.34.2 |
| tldextract | 5.3.1 | Yes | No | Directly imported in feature extraction | Yes, URL parsing for feature extraction | Yes, but only parsing user-supplied URL strings for local feature extraction | 5.3.1 (already current; no fix required on the current branch) |
| Pygments | 2.18.0 | Yes | No (via pytest) | pytest | Only dev/test tooling | Not part of runtime app | 2.20.0 |

## Dependency tree notes

### Flask dependency tree
The Flask application depends on a compatible set of packages:
- Flask 3.1.1
- Jinja2 3.1.6
- Werkzeug 3.1.8
- click 8.4.2
- itsdangerous 2.2.0
- blinker 1.9.0
- MarkupSafe 3.0.3

These must stay mutually compatible. Flask 3.1.1 is compatible with Jinja2 3.1.6 and Werkzeug 3.1.8.

### requests / urllib3 usage assessment
The project does not use requests or urllib3 for outbound HTTP requests. The application receives a URL string from the user, validates length and format, and then extracts lexical features locally. It does not fetch, follow redirects, download content, or handle compressed network responses from remote servers.

This means the urllib3 redirect and decompression-bomb issues are not reachable through the application flow.

### idna usage assessment
The project uses `urllib.parse.urlparse` and `tldextract` for URL parsing. It does not directly call `idna.encode()`, handle Unicode IDN conversions, or process punycode manually. The only idna usage is indirect dependency support inside `requests`/`urllib3` libraries, which are not used by the app at runtime.

### Vulnerability reachability summary
- Jinja2: reachable through Flask template rendering, but no remote untrusted template execution path in this app. Still updated to a patched version for safe compatibility.
- Werkzeug: reachable through the Flask web server request lifecycle, so updated with a compatible Flask version.
- urllib3: not reachable in the actual app path because no outbound HTTP requests are made.
- requests: not reachable in the actual app path because the app does not make HTTP calls.
- idna: indirect and not reachable because the app does not use IDNA encoding directly.
- tldextract: directly used for parsing user-supplied URLs, but the relevant vulnerability was not reported for this library in the current scan; the current version is kept as 5.3.1.

## Recommended minimum fix set
- Jinja2: 3.1.4 -> 3.1.6
- Werkzeug: 3.1.3 -> 3.1.8
- urllib3: 2.2.2 -> 2.5.0
- idna: 3.8 -> 3.18
- requests: 2.32.3 -> 2.34.2
- Pygments: 2.18.0 -> 2.20.0 (pytest transitive tooling)

## Compatibility risk
Low to moderate for the runtime app because these are patch-level updates in the Flask stack and supporting libraries. The project also passes the full pytest suite in the clean environment after installation.
