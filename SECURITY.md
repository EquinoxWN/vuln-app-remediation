# Security policy

This repository contains an **intentionally vulnerable** application for teaching. Its flaws are
documented on purpose in `src/vuln_app_remediation/catalog.py` and `docs/writeups/`; reporting one
of those is not needed.

- Run it only on your own machine, bound to `127.0.0.1`, or inside the CI container with no network.
- Never deploy it, expose it, or point its exploits at hosts you do not own.
- All credentials in the fixtures are fake (`EXAMPLE-NOT-A-SECRET`).

Please report privately (GitHub security advisory on this repository) anything that would let the lab
reach beyond loopback, harm the machine running it, or a real secret committed by mistake.
