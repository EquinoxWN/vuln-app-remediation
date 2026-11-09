"""The catalogue of intentional flaws, mapped to OWASP Top 10 and API Top 10.

One source of truth: the README table, the write-ups and the exploit tests all read from here, so a
flaw cannot be documented without a stable id, category and root-cause note.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Flaw:
    """One intentional vulnerability in the lab."""

    id: str  # stable slug, used as the write-up filename
    title: str
    owasp: str  # OWASP Top 10 2021 category
    api_owasp: str  # OWASP API Security Top 10 2023 category, or "-" when not API-specific
    endpoint: str  # the route that carries the flaw
    summary: str  # one sentence: what the flaw is
    root_cause: str  # one sentence: the real cause, not the symptom (used in write-ups)


# The flaws, in catalogue order. Each has a reference exploit in tests/test_exploits.py and a
# write-up in docs/writeups/<id>.md.
FLAWS: tuple[Flaw, ...] = (
    Flaw(
        id="sqli-login",
        title="SQL injection in the login form",
        owasp="A03:2021 Injection",
        api_owasp="-",
        endpoint="POST /login",
        summary="The username is concatenated into a SQL string, so a crafted value bypasses the "
        "password check.",
        root_cause="The query is built by string formatting instead of a parameterised statement.",
    ),
    Flaw(
        id="idor-order",
        title="IDOR / BOLA on order details",
        owasp="A01:2021 Broken Access Control",
        api_owasp="API1:2023 Broken Object Level Authorization",
        endpoint="GET /api/orders/<order_id>",
        summary="Any logged-in user can read any order by changing the id in the URL.",
        root_cause="The handler looks the order up by id but never checks that it belongs to the "
        "caller.",
    ),
    Flaw(
        id="bfla-admin",
        title="Broken function-level authorization on the admin route",
        owasp="A01:2021 Broken Access Control",
        api_owasp="API5:2023 Broken Function Level Authorization",
        endpoint="GET /api/admin/users",
        summary="A non-admin session reaches an admin-only listing of all users.",
        root_cause="The route checks that the caller is logged in but never checks the admin role.",
    ),
    Flaw(
        id="mass-assignment",
        title="Mass assignment of a privileged field",
        owasp="A08:2021 Software and Data Integrity Failures",
        api_owasp="API6:2023 Unrestricted Access to Sensitive Business Flows",
        endpoint="POST /api/profile",
        summary="The profile update copies every posted key into the record, so a user can set "
        "their own role to admin.",
        root_cause="The update binds the whole request body instead of an allow-list of editable "
        "fields.",
    ),
    Flaw(
        id="reflected-xss",
        title="Reflected cross-site scripting in search",
        owasp="A03:2021 Injection",
        api_owasp="-",
        endpoint="GET /search",
        summary="The search term is written into the HTML response without escaping.",
        root_cause="The response is built by string concatenation instead of an auto-escaping "
        "template.",
    ),
    Flaw(
        id="path-traversal",
        title="Path traversal in the document download",
        owasp="A01:2021 Broken Access Control",
        api_owasp="-",
        endpoint="GET /api/docs?name=...",
        summary="A name containing .. escapes the documents directory and reads arbitrary files.",
        root_cause="The name is joined onto a base directory with no check that the result stays "
        "inside it.",
    ),
    Flaw(
        id="ssrf-fetch",
        title="Server-side request forgery in the link preview",
        owasp="A10:2021 Server-Side Request Forgery",
        api_owasp="API7:2023 Server Side Request Forgery",
        endpoint="GET /api/preview?url=...",
        summary="The server fetches any URL the user supplies, including loopback-only internal "
        "endpoints.",
        root_cause="The URL is fetched with no allow-list of hosts or schemes and no block on "
        "private and loopback addresses.",
    ),
)

FLAWS_BY_ID: dict[str, Flaw] = {f.id: f for f in FLAWS}


def flaw(flaw_id: str) -> Flaw:
    """Return a flaw by id, raising KeyError with a clear message when it is unknown."""
    try:
        return FLAWS_BY_ID[flaw_id]
    except KeyError:
        raise KeyError(f"unknown flaw id: {flaw_id!r}; known ids: {sorted(FLAWS_BY_ID)}") from None
