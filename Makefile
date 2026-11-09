.PHONY: setup lint test flaws audit bench ci

PY ?= python

setup:
	$(PY) -m pip install --upgrade pip && $(PY) -m pip install -e ".[dev]"

# ruff lint, ruff format check and mypy --strict.
lint:
	$(PY) -m ruff check . && $(PY) -m ruff format --check . && $(PY) -m mypy

# Catalogue, seed, input-validation and the reference exploit per flaw.
test:
	$(PY) -m pytest -q -rs

# List the catalogued flaws (OWASP mapping and endpoint).
flaws:
	$(PY) -m vuln_app_remediation.cli flaws

# Known vulnerabilities in the Python dependencies.
audit:
	$(PY) -m pip_audit --skip-editable --cache-dir .tmp/pip-audit

bench:
	@echo "M3: OWASP ZAP before/after counts across branches; not part of M1"

ci: setup lint test
