#!/usr/bin/env python
"""CLI: render RabbitMQ definitions JSON from `gwbase.topology`.

Thin wrapper over ``gwbase.rabbit_definitions``. The build logic lives in the
package (linted / typed / unit-tested); this is the entry point the
broker-image build and the CI drift-guard call.

Modes
-----
Render one vhost to stdout / a file (ad-hoc):

    python for_docker/gen_definitions.py --vhost d1__1 \\
        --user smqPublic --password smqPublic \\
        --out rabbit/rabbitconfig/dev_definitions.json

Render the canonical committed artifacts (dev + prod) into a directory:

    python for_docker/gen_definitions.py --write-all --dir rabbit/rabbitconfig

Check the committed artifacts for drift (exit 1 if stale):

    python for_docker/gen_definitions.py --check --dir rabbit/rabbitconfig
"""

import argparse
import sys
from pathlib import Path

from gwbase.rabbit_definitions import (
    build_definitions,
    dumps,
    rendered_artifacts,
)

DEFAULT_DIR = "rabbit/rabbitconfig"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vhost", default="d1__1", help="vhost name")
    parser.add_argument("--user", default=None, help="dev user (omit for prod)")
    parser.add_argument("--password", default=None, help="dev password")
    parser.add_argument("--out", default=None, help="write here (default: stdout)")
    parser.add_argument("--dir", default=DEFAULT_DIR, help="artifact directory")
    parser.add_argument(
        "--write-all", action="store_true", help="render the committed artifacts"
    )
    parser.add_argument(
        "--check", action="store_true", help="fail if committed artifacts are stale"
    )
    args = parser.parse_args(argv)

    if args.check:
        return _check(Path(args.dir))
    if args.write_all:
        _write_all(Path(args.dir))
        return 0

    text = dumps(build_definitions(vhost=args.vhost, user=args.user, password=args.password))
    if args.out:
        Path(args.out).write_text(text)
    else:
        sys.stdout.write(text)
    return 0


def _write_all(directory: Path) -> None:
    for name, text in rendered_artifacts().items():
        (directory / name).write_text(text)
        print(f"wrote {directory / name}")


def _check(directory: Path) -> int:
    stale: list[str] = []
    for name, expected in rendered_artifacts().items():
        path = directory / name
        if not path.exists() or path.read_text() != expected:
            stale.append(name)
    if stale:
        print(
            "Stale/missing definitions: "
            + ", ".join(stale)
            + f"\nRegenerate: python for_docker/gen_definitions.py --write-all --dir {directory}",
            file=sys.stderr,
        )
        return 1
    print("definitions up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
