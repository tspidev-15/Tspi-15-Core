"""Command-line interface for TSPI-15."""

import argparse
import sys
from pathlib import Path

from . import __version__
from .interpreter import TSPIError, run_source


def main() -> None:
    parser = argparse.ArgumentParser(prog="tspi15", description="Run a TSPI-15 v0.1 source file.")
    parser.add_argument("--version", action="version", version=f"TSPI-15 {__version__}")
    parser.add_argument("file", nargs="?", help="Path to a .tspi source file")
    args = parser.parse_args()
    if not args.file:
        parser.print_help()
        return
    path = Path(args.file)
    try:
        run_source(path.read_text(encoding="utf-8"))
    except OSError as error:
        print(f"tspi15: cannot read {path}: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    except TSPIError as error:
        print(f"tspi15: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
