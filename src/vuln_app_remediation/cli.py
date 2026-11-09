"""Command line for the lab: list the catalogued flaws or serve the app on loopback."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from . import __version__
from .catalog import FLAWS


def _list_flaws(as_json: bool) -> int:
    """Print the catalogue."""
    if as_json:
        print(
            json.dumps(
                [
                    {
                        "id": f.id,
                        "title": f.title,
                        "owasp": f.owasp,
                        "api_owasp": f.api_owasp,
                        "endpoint": f.endpoint,
                        "root_cause": f.root_cause,
                    }
                    for f in FLAWS
                ],
                indent=2,
            )
        )
    else:
        for f in FLAWS:
            print(f"{f.id:16}  {f.owasp:34}  {f.endpoint}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(prog="vuln-lab", description="Local OWASP teaching lab.")
    parser.add_argument("--version", action="version", version=f"vuln-lab {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("flaws", help="list the catalogued flaws")
    p_list.add_argument("--json", action="store_true", help="emit JSON")

    sub.add_parser(
        "serve", help="run the vulnerable app on loopback (needs VULN_APP_I_UNDERSTAND=yes)"
    )

    args = parser.parse_args(argv)
    if args.command == "flaws":
        return _list_flaws(args.json)
    if args.command == "serve":
        from .app import main as serve_main

        return serve_main()
    return 2  # unreachable: subparsers are required


if __name__ == "__main__":
    sys.exit(main())
