# Mass assignment of a privileged field

| Field | Value |
|---|---|
| Catalogue id | `mass-assignment` |
| OWASP Top 10 2021 | A08:2021 Software and Data Integrity Failures |
| OWASP API Top 10 2023 | API6:2023 Unrestricted Access to Sensitive Business Flows |
| Endpoint | `POST /api/profile` |
| Reference exploit | [`tests/test_exploits.py::test_exploit_mass_assignment`](../../tests/test_exploits.py) |

## What goes wrong

The profile update writes every recognised key from the JSON body, and `role` is one of them, so a user can set their own role to `admin`.

## Proof of concept

The reference exploit runs against the lab's in-process app (Flask test client), never a real host.
It first checks the ordinary path, then shows the flaw firing. Run it with:

```bash
python -m pytest -q tests/test_exploits.py::test_exploit_mass_assignment
```

Result on 2026-11-09 (Windows 11, Python 3.14): passed.

## Root cause

The writable field set is defined by the database columns rather than by what a user may change about themselves.

## Fix direction (M2)

Bind an explicit allow-list of user-editable fields (`email` only) and reject unknown or privileged keys with 400.
