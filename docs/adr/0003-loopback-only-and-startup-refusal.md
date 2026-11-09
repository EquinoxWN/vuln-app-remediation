# ADR 0003: Loopback-only binding and a start-up refusal

- **Status:** Accepted

## Context

This repository ships code that is insecure on purpose. The main risk is not the code itself but
someone running it where it can be reached. The working rules for security content require that it
runs only against local, intentionally vulnerable targets and never faces a network.

## Decision

Make accidental exposure hard (poka-yoke):

- The app binds to `127.0.0.1` only; it never binds `0.0.0.0`.
- `main()` refuses to start unless `VULN_APP_I_UNDERSTAND=yes` is set, printing why.
- All fixtures are inert and marked `EXAMPLE-NOT-A-SECRET`; no real secret exists to leak.
- The SSRF target endpoint rejects any caller whose address is not loopback.
- The SSRF fetcher has a bounded timeout (3 s) and read cap (64 KB) so even the vulnerable path
  cannot hang or exhaust memory.

## Consequences

- Running the lab requires a deliberate step, so it cannot be started by a stray `python -m` in a
  deploy script without the operator opting in.
- The guarantees are enforced in code and covered by tests (`test_internal_metadata_blocks_non_loopback`,
  the serve-refusal exit code), not left to documentation alone.
- Trade-off: the acknowledgement env var is friction for a first-time local user; the README shows it
  on the run line, and the test suite needs no running server, so day-to-day use is unaffected.
