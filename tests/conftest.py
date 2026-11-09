"""Shared fixtures: a seeded lab app wired so the SSRF fetcher routes back into the same app.

Routing the fetcher to the app's own test client lets the SSRF exploit reach a loopback-only
internal endpoint deterministically, with no real network traffic.
"""

from __future__ import annotations

from collections.abc import Iterator
from urllib.parse import urlparse

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from vuln_app_remediation.app import create_app
from vuln_app_remediation.db import connect


@pytest.fixture
def app() -> Iterator[Flask]:
    """A seeded lab app with a shared in-memory DB and an in-process fetcher."""
    conn = connect()
    holder: dict[str, Flask] = {}

    def fetcher(url: str) -> bytes:
        """Resolve loopback URLs against the app itself; reject anything else (keeps tests offline)."""
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError(f"unsupported scheme: {parsed.scheme!r}")
        if parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise OSError(f"test fetcher only serves loopback, got {parsed.hostname!r}")
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"
        resp = holder["app"].test_client().get(path)
        return resp.get_data()

    application = create_app(conn=conn, fetcher=fetcher)
    holder["app"] = application
    try:
        yield application
    finally:
        conn.close()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A test client for the lab app."""
    return app.test_client()


def login(client: FlaskClient, username: str, password: str) -> TestResponse:
    """Log in through the real login route and return the response."""
    return client.post("/login", data={"username": username, "password": password})
