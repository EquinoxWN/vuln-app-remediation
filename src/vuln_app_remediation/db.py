"""An in-memory SQLite seed for the lab. Every value is obviously fake and local-only.

The passwords, tokens and emails here are inert teaching fixtures, never real secrets. They exist so
the lab has data to attack; nothing in this file reaches a real service.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

# Inert fixtures. The marker string makes it unmistakable that these are not real credentials.
_FAKE = "EXAMPLE-NOT-A-SECRET"


@dataclass(frozen=True)
class SeedUser:
    """A seeded account (teaching fixture, not a real identity)."""

    id: int
    username: str
    password: str  # plain text on purpose: part of the broken-auth lesson, obviously fake
    role: str
    email: str


SEED_USERS: tuple[SeedUser, ...] = (
    SeedUser(1, "alice", f"alice-{_FAKE}", "user", "alice@lab.invalid"),
    SeedUser(2, "bob", f"bob-{_FAKE}", "user", "bob@lab.invalid"),
    SeedUser(3, "admin", f"admin-{_FAKE}", "admin", "admin@lab.invalid"),
)

# order id -> (owner user id, item, amount in cents)
SEED_ORDERS: tuple[tuple[int, int, str, int], ...] = (
    (1001, 1, "USB cable", 799),
    (1002, 1, "Mechanical keyboard", 8999),
    (1003, 2, "Webcam", 4500),
    (1004, 3, "Server rack screws", 1200),
)


def connect() -> sqlite3.Connection:
    """Open a fresh in-memory database, seeded. Caller owns it and must close it."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, "
        "password TEXT NOT NULL, role TEXT NOT NULL, email TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, item TEXT NOT NULL, "
        "amount_cents INTEGER NOT NULL)"
    )
    conn.executemany(
        "INSERT INTO users (id, username, password, role, email) VALUES (?, ?, ?, ?, ?)",
        [(u.id, u.username, u.password, u.role, u.email) for u in SEED_USERS],
    )
    conn.executemany(
        "INSERT INTO orders (id, user_id, item, amount_cents) VALUES (?, ?, ?, ?)",
        SEED_ORDERS,
    )
    conn.commit()
    return conn
