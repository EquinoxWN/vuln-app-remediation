# RFC 0001: vuln-app-remediation design

- **Status:** Accepted
- **Author:** EquinoxWN
- **Created:** 2026-11-09

## Problem

Developers are told to "find and fix the vulnerability" but rarely get a safe, concrete target where
a flaw can be exploited, explained and then patched, with a test proving the exploit worked and later
proving the fix holds. Reading an OWASP list is not the same as watching an IDOR return someone
else's order. The critical-to-quality measure (Define, in Lean Six Sigma terms) is: for every
catalogued flaw, an automated reference exploit demonstrates the flaw, and the flaw is mapped to a
named OWASP Top 10 / API Top 10 category with a one-sentence root cause.

## Users

- Engineers preparing for secure-code-review interviews ("find the bug in this handler").
- People learning the OWASP Top 10 who want a running target rather than slides.
- Reviewers who want a minimal, readable example of each bug class to point to.

## Goals (M1)

- Ship an intentionally vulnerable Flask app that runs **only** on loopback, with a catalogue that
  maps each flaw to OWASP Top 10 2021 and (where it applies) the OWASP API Security Top 10 2023.
- Cover the bug classes named in the backlog: injection (SQLi), IDOR / BOLA, SSRF and broken auth,
  plus broken function-level authorization, mass assignment, reflected XSS and path traversal.
- Give each flaw a write-up with a proof-of-concept, captured here as an automated reference exploit
  (a pytest test) so the proof is reproducible without a proxy tool and runs in CI.

## Non-goals

- Running as a hosted or internet-facing service. The app refuses to start without an explicit
  acknowledgement env var and binds to `127.0.0.1`.
- Any attack against third-party hosts. Every exploit targets the lab's own in-process app and data.
- The fixes themselves and the ZAP/Semgrep automation: those are M2 and M3 (see Milestones).

## Proposed design

A Flask application factory (`create_app`) wires a set of routes, each carrying one deliberate flaw.
A frozen `catalog.FLAWS` tuple is the single source of truth: id, title, OWASP category, endpoint,
summary and root cause. The README table, the per-flaw write-ups and the exploit tests all read from
it, so a flaw cannot be half-documented.

- **Data:** an in-memory SQLite seed (`db.py`) with three accounts and four orders. Every password,
  token and email is an obviously fake fixture carrying the marker `EXAMPLE-NOT-A-SECRET`.
- **Flaws:** SQL injection in login (string-built query), IDOR on `/api/orders/<id>` (no owner
  check), broken function-level auth on `/api/admin/users` (no role check), mass assignment on
  `/api/profile` (role is writable), reflected XSS in `/search` (unescaped), path traversal in
  `/api/docs` (no containment check), and SSRF in `/api/preview` (fetches any user URL).
- **Reference exploits:** `tests/test_exploits.py`, one test per flaw, using Flask's test client. A
  guard test asserts every catalogued flaw has a matching exploit. The SSRF exploit routes the
  fetcher back into the same app (injected in `conftest.py`) so it reaches a loopback-only internal
  endpoint with no real network traffic.
- **Safety rails (poka-yoke):** loopback-only bind; a start-up refusal unless `VULN_APP_I_UNDERSTAND
  =yes`; the SSRF fetcher has a 3 s timeout and a 64 KB read cap; the internal endpoint rejects any
  non-loopback caller; non-vulnerable guards (numeric ids, required fields, JSON-object bodies) are
  real and tested so failures surface as 4xx, not 500s.

## Alternatives considered

| Option | Why not (yet) |
|---|---|
| Fork OWASP Juice Shop / DVWA | Large, Node/PHP, and hard to reason about as a minimal teaching unit; this repo is a small, auditable Python target where each flaw is a handful of lines mapped one-to-one to a test. Juice Shop remains the upstream to contribute to. |
| Capture PoCs in Burp Suite screenshots | Not reproducible in CI and not a regression test. Expressing each PoC as an automated test makes the exploit runnable, reviewable and, in M2, a guard that the fix holds. |
| Ship the fixed code behind a flag now | M1's deliverable is the vulnerable target and the proofs; mixing the fix in dilutes both. M2 patches the same routes so the exploit tests invert into regression tests. |

## Measurement plan

- **Measure/Analyze:** `make test` runs the catalogue, seed, input-validation and exploit tests; the
  count and pass/fail are recorded in `docs/results/m1.md`. Each exploit asserts both a baseline
  (the non-malicious path behaves) and the exploit (the flaw fires), so a test that always passes
  would be caught by mutation testing (`docs/quality/2026-11-01.md`).
- **Control:** CI runs lint (`ruff`), types (`mypy --strict`), the tests and `pip-audit` on every
  push; the catalogue guard test blocks adding a flaw without an exploit.

## Milestones

- **M1 (this RFC):** vulnerable app mapped to OWASP Top 10 / API Top 10, each flaw with a reference
  exploit and a write-up. Local only.
- **M2:** patch each route (root cause, not symptom); each exploit test inverts into a regression
  test proving the exploit no longer works.
- **M3:** OWASP ZAP in CI showing before/after findings, and a Semgrep rule per bug class.

## Risks and open questions

- **Misuse risk:** the app is a deliberate target. Mitigated by loopback-only binding, the start-up
  refusal, fake-only fixtures, and documentation that states it must never be exposed.
- **Branch model:** the backlog mentions `vulnerable`/`fixed` branches; the portfolio keeps a single
  `main` branch, so M2 patches land on `main` with the exploit tests turning into regression tests
  rather than a second branch.
