# Path traversal in the document download

| Field | Value |
|---|---|
| Catalogue id | `path-traversal` |
| OWASP Top 10 2021 | A01:2021 Broken Access Control |
| OWASP API Top 10 2023 | - |
| Endpoint | `GET /api/docs?name=...` |
| Reference exploit | [`tests/test_exploits.py::test_exploit_path_traversal`](../../tests/test_exploits.py) |

## What goes wrong

The document name is joined onto the `docs_store` directory as given. `../server_notes.txt` resolves outside the store and its contents are returned.

## Proof of concept

The reference exploit runs against the lab's in-process app (Flask test client), never a real host.
It first checks the ordinary path, then shows the flaw firing. Run it with:

```bash
python -m pytest -q tests/test_exploits.py::test_exploit_path_traversal
```

Result on 2026-11-09 (Windows 11, Python 3.14): passed.

## Root cause

The resolved path is never checked against the base directory.

## Fix direction (M2)

Resolve the path and require it to stay under the resolved base (`Path.is_relative_to`), or serve from an id-to-file map so names are never paths.
