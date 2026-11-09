# Reflected cross-site scripting in search

| Field | Value |
|---|---|
| Catalogue id | `reflected-xss` |
| OWASP Top 10 2021 | A03:2021 Injection |
| OWASP API Top 10 2023 | - |
| Endpoint | `GET /search` |
| Reference exploit | [`tests/test_exploits.py::test_exploit_reflected_xss`](../../tests/test_exploits.py) |

## What goes wrong

The search term is concatenated into the HTML page. A term containing markup comes back as markup, so a browser would run a script supplied in a link.

## Proof of concept

The reference exploit runs against the lab's in-process app (Flask test client), never a real host.
It first checks the ordinary path, then shows the flaw firing. Run it with:

```bash
python -m pytest -q tests/test_exploits.py::test_exploit_reflected_xss
```

Result on 2026-11-09 (Windows 11, Python 3.14): passed.

## Root cause

Output is built by string concatenation with no context-aware encoding.

## Fix direction (M2)

Render through Jinja2's auto-escaping templates (or `markupsafe.escape`) and add a restrictive Content-Security-Policy header as defence in depth.
