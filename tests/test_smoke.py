from __future__ import annotations

import vuln_app_remediation


def test_version() -> None:
    """The package exposes its version."""
    assert vuln_app_remediation.__version__ == "0.1.0"
