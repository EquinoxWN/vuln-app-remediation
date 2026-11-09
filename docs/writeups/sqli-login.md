# SQL injection in the login form

| Field | Value |
|---|---|
| Catalogue id | `sqli-login` |
| OWASP Top 10 2021 | A03:2021 Injection |
| OWASP API Top 10 2023 | - |
| Endpoint | `POST /login` |
| Reference exploit | [`tests/test_exploits.py::test_exploit_sqli_login`](../../tests/test_exploits.py) |

## What goes wrong

The login handler builds its SQL by joining the submitted username and password into a string. A username containing a quote changes the structure of the query, so the password condition stops applying and the lab logs in as the named user.

## Proof of concept

The reference exploit runs against the lab's in-process app (Flask test client), never a real host.
It first checks the ordinary path, then shows the flaw firing. Run it with:

```bash
python -m pytest -q tests/test_exploits.py::test_exploit_sqli_login
```

Result on 2026-11-09 (Windows 11, Python 3.14): passed.

## Root cause

The query mixes code and data: user input is concatenated into SQL text instead of being bound as a parameter.

## Fix direction (M2)

Use a parameterised statement (`?` placeholders) and compare a salted password hash in code. The exploit test then inverts: the crafted username must get a 401.
