#!/usr/bin/env python
"""CLI: render a RabbitMQ definitions JSON from `gwbase.topology`.

Thin wrapper over ``gwbase.rabbit_definitions.build_definitions``. The build
logic lives in the package (linted / typed / unit-tested); this is just the
entry point the broker-image build and the CI drift-guard call.

Examples
--------
Dev (commits the non-secret smqPublic credential):

    python for_docker/gen_definitions.py --vhost d1__1 \\
        --user smqPublic --password smqPublic \\
        --out rabbit/rabbitconfig/dev_definitions.json

Prod (no baked credential — user/permissions injected at deploy):

    python for_docker/gen_definitions.py --vhost hw1__1 \\
        --out rabbit/rabbitconfig/prod_definitions.json
"""

import argparse
import json
import sys
from pathlib import Path

from gwbase.rabbit_definitions import build_definitions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vhost", default="d1__1", help="vhost name")
    parser.add_argument(
        "--user", default=None, help="dev user to include (omit for prod)"
    )
    parser.add_argument(
        "--password", default=None, help="dev password (defaults to --user)"
    )
    parser.add_argument(
        "--out", default=None, help="write here (default: stdout)"
    )
    args = parser.parse_args(argv)

    definitions = build_definitions(
        vhost=args.vhost, user=args.user, password=args.password
    )
    # Deterministic: sorted keys + trailing newline, so CI can diff.
    text = json.dumps(definitions, indent=2, sort_keys=True) + "\n"

    if args.out:
        Path(args.out).write_text(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
