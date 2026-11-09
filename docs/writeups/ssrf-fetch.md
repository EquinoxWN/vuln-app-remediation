# Server-side request forgery in the link preview

| Field | Value |
|---|---|
| Catalogue id | `ssrf-fetch` |
| OWASP Top 10 2021 | A10:2021 Server-Side Request Forgery |
| OWASP API Top 10 2023 | API7:2023 Server Side Request Forgery |
| Endpoint | `GET /api/preview?url=...` |
| Reference exploit | [`tests/test_exploits.py::test_exploit_ssrf_fetch`](../../tests/test_exploits.py) |

## What goes wrong

The preview fetches whatever URL the caller supplies. Pointed at `http://127.0.0.1/internal/metadata`, the server makes the request from loopback and returns the internal-only response. In the test the fetcher is routed back into the same app, so no network traffic happens.

## Proof of concept

The reference exploit runs against the lab's in-process app (Flask test client), never a real host.
It first checks the ordinary path, then shows the flaw firing. Run it with:

```bash
python -m pytest -q tests/test_exploits.py::test_exploit_ssrf_fetch
```

Result on 2026-11-09 (Windows 11, Python 3.14): passed.

## Root cause

The server acts as a proxy for user-chosen destinations with no scheme or host allow-list and no block on loopback and private ranges.

## Fix direction (M2)

Allow-list schemes and hosts, resolve the name once and reject loopback, link-local and private addresses before connecting, and disable redirects.
