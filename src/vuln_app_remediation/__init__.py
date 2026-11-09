"""vuln-app-remediation: a local-only OWASP teaching lab of intentional flaws.

The package ships an intentionally vulnerable Flask app, a catalogue that maps each flaw to the
OWASP Top 10 / API Top 10, and a reference exploit per flaw expressed as an automated test. It is a
learning target: it binds to loopback, seeds obviously fake data, and must never face a network.
See README.md and docs/writeups/ for the problem this solves.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
