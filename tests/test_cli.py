"""The CLI lists the catalogue and refuses to serve without the acknowledgement variable."""

from __future__ import annotations

import json

import pytest

from vuln_app_remediation.catalog import FLAWS
from vuln_app_remediation.cli import main


def test_flaws_json_lists_every_flaw(capsys: pytest.CaptureFixture[str]) -> None:
    """`flaws --json` prints one object per catalogued flaw."""
    assert main(["flaws", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert [d["id"] for d in data] == [f.id for f in FLAWS]


def test_serve_refuses_without_acknowledgement(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`serve` exits 2 and starts nothing unless VULN_APP_I_UNDERSTAND=yes."""
    monkeypatch.delenv("VULN_APP_I_UNDERSTAND", raising=False)
    assert main(["serve"]) == 2
    assert "Refusing to start" in capsys.readouterr().out


def test_unknown_command_is_an_argparse_error() -> None:
    """An unknown subcommand exits 2 through argparse."""
    with pytest.raises(SystemExit) as exc:
        main(["nope"])
    assert exc.value.code == 2


@pytest.mark.parametrize("port", ["", "abc", "80", "70000", "-1"])
def test_serve_rejects_an_invalid_port(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], port: str
) -> None:
    """An invalid VULN_APP_PORT exits 2 before any socket is opened."""
    monkeypatch.setenv("VULN_APP_I_UNDERSTAND", "yes")
    monkeypatch.setenv("VULN_APP_PORT", port)
    assert main(["serve"]) == 2
    assert "VULN_APP_PORT" in capsys.readouterr().out
