"""Non-exploit behaviour: the banner, the catalogue endpoint, and input-validation failure paths.

These cover the empty, invalid and unauthenticated paths so the lab's guards (bounded input, numeric
ids, login checks) are proven, not just the happy and exploit paths.
"""

from __future__ import annotations

from conftest import login
from flask import Flask
from flask.testing import FlaskClient


def test_index_warns_it_is_a_lab(client: FlaskClient) -> None:
    """The root route carries an unmistakable lab warning."""
    body = client.get("/").get_json()
    assert "Intentionally vulnerable" in body["warning"]


def test_flaws_endpoint_lists_the_catalogue(client: FlaskClient) -> None:
    """/api/flaws returns one entry per catalogued flaw."""
    from vuln_app_remediation.catalog import FLAWS

    data = client.get("/api/flaws").get_json()
    assert {e["id"] for e in data} == {f.id for f in FLAWS}


def test_login_requires_a_username(client: FlaskClient) -> None:
    """An empty username is a 400, not a 500 or an accidental match."""
    assert client.post("/login", data={"username": "", "password": "x"}).status_code == 400


def test_order_requires_login_and_numeric_id(client: FlaskClient) -> None:
    """The order route rejects anonymous callers and non-numeric ids before touching the DB."""
    assert client.get("/api/orders/1001").status_code == 401
    login(client, "alice", "alice-EXAMPLE-NOT-A-SECRET")
    assert client.get("/api/orders/not-a-number").status_code == 400
    assert client.get("/api/orders/9999").status_code == 404


def test_profile_rejects_non_object_and_anonymous(client: FlaskClient) -> None:
    """Profile update needs a login and a JSON object body."""
    assert client.post("/api/profile", json={"role": "admin"}).status_code == 401
    login(client, "alice", "alice-EXAMPLE-NOT-A-SECRET")
    assert client.post("/api/profile", json=[]).status_code == 400
    assert client.post("/api/profile", json={}).status_code == 400


def test_docs_requires_a_name_and_404s_missing_files(client: FlaskClient) -> None:
    """The docs route needs a name and reports unreadable files as 404, not 500."""
    assert client.get("/api/docs").status_code == 400
    assert client.get("/api/docs", query_string={"name": "no_such_file.txt"}).status_code == 404


def test_preview_requires_url_and_rejects_bad_scheme(client: FlaskClient) -> None:
    """The preview route needs a url and surfaces fetch failures as 502, not 500."""
    assert client.get("/api/preview").status_code == 400
    bad = client.get("/api/preview", query_string={"url": "file:///etc/passwd"})
    assert bad.status_code == 502  # the test fetcher rejects non-http schemes


def test_internal_metadata_blocks_non_loopback(app: Flask) -> None:
    """The internal endpoint refuses a caller whose address is not loopback."""
    client = app.test_client()
    resp = client.get("/internal/metadata", environ_overrides={"REMOTE_ADDR": "203.0.113.9"})
    assert resp.status_code == 403
