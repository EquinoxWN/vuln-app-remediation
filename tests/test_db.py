"""The seed is inert teaching data; these tests pin its shape and its fake-secret marker."""

from __future__ import annotations

from vuln_app_remediation.db import SEED_ORDERS, SEED_USERS, connect


def test_seed_users_are_obviously_fake() -> None:
    """Every seeded password carries the not-a-secret marker, so no real credential can slip in."""
    for u in SEED_USERS:
        assert "EXAMPLE-NOT-A-SECRET" in u.password
        assert u.email.endswith(".invalid")


def test_exactly_one_admin_is_seeded() -> None:
    """The lab has a single admin account, used by the privilege-escalation lessons."""
    admins = [u for u in SEED_USERS if u.role == "admin"]
    assert len(admins) == 1
    assert admins[0].username == "admin"


def test_connect_seeds_users_and_orders() -> None:
    """A fresh connection has the seeded rows and closes cleanly."""
    conn = connect()
    try:
        users = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
        orders = conn.execute("SELECT COUNT(*) AS n FROM orders").fetchone()["n"]
        assert users == len(SEED_USERS)
        assert orders == len(SEED_ORDERS)
    finally:
        conn.close()


def test_orders_reference_seeded_users() -> None:
    """Every seeded order belongs to a seeded user (referential sanity of the fixture)."""
    user_ids = {u.id for u in SEED_USERS}
    for _oid, owner, _item, amount in SEED_ORDERS:
        assert owner in user_ids
        assert amount > 0
