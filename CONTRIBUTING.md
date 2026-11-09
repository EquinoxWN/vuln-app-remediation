# Contributing

1. `python -m venv .venv` and `pip install -e ".[dev]"` (Python 3.11+).
2. A new flaw needs all three: an entry in `catalog.FLAWS`, a `test_exploit_<id>` reference exploit in
   `tests/test_exploits.py`, and `docs/writeups/<id>.md`. The guard tests fail if one is missing.
3. Exploits target only the in-process app. No third-party hosts, no real secrets, no payloads that
   do anything beyond proving the flaw.
4. Before a pull request: `ruff check .`, `ruff format --check .`, `mypy`, `pytest -q`, `pip_audit`.
