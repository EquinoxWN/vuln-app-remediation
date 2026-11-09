"""The intentionally vulnerable Flask app. LOCAL TEACHING LAB ONLY.

Every route below carries a deliberate flaw from catalog.FLAWS. The code is written the insecure way
on purpose so the exploit tests and write-ups have a concrete target. Do not copy these patterns into
real code, and never expose this app to a network: it binds to loopback and refuses to run with
debug off unless VULN_APP_I_UNDERSTAND=yes is set (a poka-yoke against accidental deployment).
"""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from flask import Flask, Response, g, jsonify, request, session

# Obviously fake, hard-coded on purpose (part of the broken-auth lesson). Not a real secret.
_FAKE_SECRET_KEY = "EXAMPLE-NOT-A-SECRET-flask-session-key"  # noqa: S105 (inert lab fixture)

# Cap on anything the SSRF preview may read back, so a fetch cannot exhaust memory.
_PREVIEW_MAX_BYTES = 64 * 1024
_PREVIEW_TIMEOUT_S = 3.0

# The "internal" documents the path-traversal lab is meant to confine access to.
_DOCS_DIR = Path(__file__).resolve().parent / "docs_store"

Fetcher = Callable[[str], bytes]


def _default_fetcher(url: str) -> bytes:
    """Fetch a URL with a timeout and a size cap (still SSRF-vulnerable: no host allow-list)."""
    # INTENTIONAL FLAW (ssrf-fetch): any scheme/host the user gives is fetched server-side.
    with urlopen(url, timeout=_PREVIEW_TIMEOUT_S) as resp:
        data: bytes = resp.read(_PREVIEW_MAX_BYTES)
    return data


def create_app(
    conn: sqlite3.Connection | None = None,
    fetcher: Fetcher | None = None,
) -> Flask:
    """Build the vulnerable app. A caller may inject a DB connection and a URL fetcher for tests."""
    app = Flask(__name__)
    app.secret_key = _FAKE_SECRET_KEY
    app.config["LAB"] = True
    shared_conn = conn
    fetch: Fetcher = fetcher or _default_fetcher

    def db() -> sqlite3.Connection:
        """One seeded connection per request (or the injected shared one)."""
        if shared_conn is not None:
            return shared_conn
        if "db" not in g:
            from .db import connect

            g.db = connect()
        return g.db  # type: ignore[no-any-return]

    @app.teardown_appcontext
    def _close_db(_exc: BaseException | None) -> None:
        """Close the per-request connection if we opened one."""
        conn_ = g.pop("db", None)
        if conn_ is not None and shared_conn is None:
            conn_.close()

    def current_user() -> sqlite3.Row | None:
        """The logged-in user row, or None."""
        uid = session.get("user_id")
        if uid is None:
            return None
        cur = db().execute("SELECT * FROM users WHERE id = ?", (uid,))
        row: sqlite3.Row | None = cur.fetchone()
        return row

    @app.get("/")
    def index() -> Response:
        """Lab banner so the app can never be mistaken for a real service."""
        return jsonify(
            lab="vuln-app-remediation",
            warning="Intentionally vulnerable. Local teaching lab only. Do not expose.",
            flaws="GET /api/flaws",
        )

    @app.get("/api/flaws")
    def flaws() -> Response:
        """List the catalogued flaws (documentation endpoint, not itself a flaw)."""
        from .catalog import FLAWS

        return jsonify(
            [
                {"id": f.id, "title": f.title, "owasp": f.owasp, "endpoint": f.endpoint}
                for f in FLAWS
            ]
        )

    @app.post("/login")
    def login() -> Any:
        """INTENTIONAL FLAW (sqli-login): username is concatenated into the SQL string."""
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username:
            return jsonify(error="username required"), 400
        query = (
            "SELECT * FROM users WHERE username = '"
            + username
            + "' AND password = '"
            + password
            + "'"
        )
        try:
            row = db().execute(query).fetchone()
        except sqlite3.Error:
            # The injection may produce invalid SQL; surface it as an auth failure.
            return jsonify(error="invalid credentials"), 401
        if row is None:
            return jsonify(error="invalid credentials"), 401
        session["user_id"] = row["id"]
        return jsonify(ok=True, user=row["username"], role=row["role"])

    @app.post("/logout")
    def logout() -> Response:
        """End the session."""
        session.clear()
        return jsonify(ok=True)

    @app.get("/api/orders/<order_id>")
    def get_order(order_id: str) -> Any:
        """INTENTIONAL FLAW (idor-order): looked up by id, never checked against the caller."""
        if current_user() is None:
            return jsonify(error="login required"), 401
        if not order_id.isdigit():
            return jsonify(error="order id must be numeric"), 400
        row = db().execute("SELECT * FROM orders WHERE id = ?", (int(order_id),)).fetchone()
        if row is None:
            return jsonify(error="not found"), 404
        return jsonify(
            id=row["id"], user_id=row["user_id"], item=row["item"], amount_cents=row["amount_cents"]
        )

    @app.get("/api/admin/users")
    def admin_users() -> Any:
        """INTENTIONAL FLAW (bfla-admin): checks login but not the admin role."""
        if current_user() is None:
            return jsonify(error="login required"), 401
        rows = db().execute("SELECT id, username, role, email FROM users").fetchall()
        return jsonify([dict(r) for r in rows])

    @app.post("/api/profile")
    def update_profile() -> Any:
        """INTENTIONAL FLAW (mass-assignment): binds every posted key, including role."""
        user = current_user()
        if user is None:
            return jsonify(error="login required"), 401
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="JSON object required"), 400
        allowed_columns = {"username", "email", "role", "password"}
        updates = {k: v for k, v in payload.items() if k in allowed_columns}
        if not updates:
            return jsonify(error="nothing to update"), 400
        assignments = ", ".join(f"{col} = ?" for col in updates)
        db().execute(
            f"UPDATE users SET {assignments} WHERE id = ?",
            [*updates.values(), user["id"]],
        )
        db().commit()
        fresh = (
            db()
            .execute("SELECT id, username, role, email FROM users WHERE id = ?", (user["id"],))
            .fetchone()
        )
        return jsonify(dict(fresh))

    @app.get("/search")
    def search() -> Response:
        """INTENTIONAL FLAW (reflected-xss): the term is written into HTML without escaping."""
        term = request.args.get("q", "")
        body = "<html><body><h1>Results for " + term + "</h1><p>No items.</p></body></html>"
        return Response(body, mimetype="text/html")

    @app.get("/api/docs")
    def read_doc() -> Any:
        """INTENTIONAL FLAW (path-traversal): name is joined with no containment check."""
        name = request.args.get("name", "")
        if not name:
            return jsonify(error="name required"), 400
        target = _DOCS_DIR / name
        try:
            text = target.read_text(encoding="utf-8", errors="replace")
        except (FileNotFoundError, IsADirectoryError, PermissionError, OSError):
            return jsonify(error="cannot read"), 404
        return Response(text, mimetype="text/plain")

    @app.get("/internal/metadata")
    def internal_metadata() -> Any:
        """Loopback-only internal resource, the SSRF lab's target (blocks non-local callers)."""
        if request.remote_addr not in {"127.0.0.1", "::1", None}:
            return jsonify(error="forbidden"), 403
        return jsonify(
            internal=True,
            note="internal-only metadata",
            token="EXAMPLE-NOT-A-SECRET",  # noqa: S106 (inert lab fixture)
        )

    @app.get("/api/preview")
    def preview() -> Any:
        """INTENTIONAL FLAW (ssrf-fetch): fetches any user URL (bounded size and timeout only)."""
        url = request.args.get("url", "")
        if not url:
            return jsonify(error="url required"), 400
        try:
            data = fetch(url)
        except (URLError, ValueError, OSError) as exc:
            return jsonify(error=f"fetch failed: {exc}"), 502
        return Response(data, mimetype="application/octet-stream")

    return app


def main() -> int:
    """Run the lab on loopback. Refuses to run unless the operator acknowledges the risk."""
    if os.environ.get("VULN_APP_I_UNDERSTAND") != "yes":
        print(
            "Refusing to start: this app is intentionally vulnerable.\n"
            "Set VULN_APP_I_UNDERSTAND=yes to run it, and only on a local, isolated machine.",
        )
        return 2
    raw_port = os.environ.get("VULN_APP_PORT", "5000")
    if not raw_port.isdigit() or not 1024 <= int(raw_port) <= 65535:
        print(f"VULN_APP_PORT must be an integer in 1024..65535, got {raw_port!r}")
        return 2
    port = int(raw_port)
    # Bind to loopback only; never 0.0.0.0.
    create_app().run(host="127.0.0.1", port=port, debug=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
