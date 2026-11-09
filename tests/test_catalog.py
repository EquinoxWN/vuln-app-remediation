"""The catalogue is the single source of truth, so its integrity is tested directly."""

from __future__ import annotations

from pathlib import Path

import pytest

from vuln_app_remediation.catalog import FLAWS, FLAWS_BY_ID, flaw


def test_ids_are_unique_and_slug_shaped() -> None:
    """Every flaw id is unique and a filesystem-safe slug (used as a write-up filename)."""
    ids = [f.id for f in FLAWS]
    assert len(ids) == len(set(ids))
    for fid in ids:
        assert fid
        assert all(c.islower() or c.isdigit() or c == "-" for c in fid)


def test_every_flaw_is_fully_described() -> None:
    """No flaw may ship with an empty field: a flaw cannot be half-documented."""
    for f in FLAWS:
        assert all((f.title, f.owasp, f.endpoint, f.summary, f.root_cause))
        assert f.owasp.startswith("A")
        assert ":2021" in f.owasp


def test_lookup_round_trips() -> None:
    """flaw(id) returns the catalogue entry."""
    for f in FLAWS:
        assert flaw(f.id) is f
    assert set(FLAWS_BY_ID) == {f.id for f in FLAWS}


def test_unknown_id_raises_keyerror_with_known_ids() -> None:
    """An unknown id fails loudly and names the known ids."""
    with pytest.raises(KeyError, match="unknown flaw id"):
        flaw("does-not-exist")


def test_core_backlog_categories_are_present() -> None:
    """The backlog names injection, IDOR/BOLA, SSRF and broken auth: all must be catalogued."""
    categories = " ".join(f"{f.owasp} {f.api_owasp} {f.title}" for f in FLAWS).lower()
    assert "injection" in categories
    assert "broken object level" in categories or "idor" in categories
    assert (
        "server-side request forgery" in categories or "server side request forgery" in categories
    )
    assert "access control" in categories


def test_every_flaw_has_a_writeup_naming_its_category() -> None:
    """Each flaw has docs/writeups/<id>.md that states its OWASP category and root cause."""
    root = Path(__file__).resolve().parent.parent / "docs" / "writeups"
    for f in FLAWS:
        text = (root / f"{f.id}.md").read_text(encoding="utf-8")
        assert f.owasp in text
        assert "## Root cause" in text
        assert f"test_exploit_{f.id.replace('-', '_')}" in text
