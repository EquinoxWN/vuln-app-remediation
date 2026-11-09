# IDOR / BOLA on order details

| Field | Value |
|---|---|
| Catalogue id | `idor-order` |
| OWASP Top 10 2021 | A01:2021 Broken Access Control |
| OWASP API Top 10 2023 | API1:2023 Broken Object Level Authorization |
| Endpoint | `GET /api/orders/<order_id>` |
| Reference exploit | [`tests/test_exploits.py::test_exploit_idor_order`](../../tests/test_exploits.py) |

## What goes wrong

The route checks that a session exists, then returns whichever order id is in the URL. Alice can read Bob's order 1003 by changing the number.

## Proof of concept

The reference exploit runs against the lab's in-process app (Flask test client), never a real host.
It first checks the ordinary path, then shows the flaw firing. Run it with:

```bash
python -m pytest -q tests/test_exploits.py::test_exploit_idor_order
```

Result on 2026-11-09 (Windows 11, Python 3.14): passed.

## Root cause

Authorization is done at the route level (logged in or not) but never at the object level: the query has no `user_id = caller` condition.

## Fix direction (M2)

Scope the lookup to the caller (`WHERE id = ? AND user_id = ?`) and return 404 for objects the caller does not own, so existence is not leaked.
