# Broken function-level authorization on the admin route

| Field | Value |
|---|---|
| Catalogue id | `bfla-admin` |
| OWASP Top 10 2021 | A01:2021 Broken Access Control |
| OWASP API Top 10 2023 | API5:2023 Broken Function Level Authorization |
| Endpoint | `GET /api/admin/users` |
| Reference exploit | [`tests/test_exploits.py::test_exploit_bfla_admin`](../../tests/test_exploits.py) |

## What goes wrong

The admin listing only checks for a session. Any logged-in user, not just the admin, receives every account with its role and email.

## Proof of concept

The reference exploit runs against the lab's in-process app (Flask test client), never a real host.
It first checks the ordinary path, then shows the flaw firing. Run it with:

```bash
python -m pytest -q tests/test_exploits.py::test_exploit_bfla_admin
```

Result on 2026-11-09 (Windows 11, Python 3.14): passed.

## Root cause

The role check is missing; the route relies on the path name and the absence of a UI link to keep normal users out.

## Fix direction (M2)

Enforce the role in one decorator (deny by default) applied to every admin route, and test that a user session gets 403.
