#!/usr/bin/env python3

import argparse
import sys

from pipy import configuration, session
from pipy.utils import cli

ACTIONS = {"open": session, "close": session}


def main() -> None:

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--verbose", action="store_true", help="Enable verbbose output.")

    subparsers = parser.add_subparsers()

    open_parser = cli.add_action("open", subparsers, "Open an isolated python environment.")
    cli.version(open_parser)

    close_parser = cli.add_action("close", subparsers, "Close and delete python environment.")
    cli.version(close_parser)

    configs = configuration.parse()

    args = vars(parser.parse_args())

    action = args.pop("action", None)
    if action is None:
        parser.print_help()
        sys.exit(1)

    if action not in ACTIONS:
        parser.print_help()
        sys.exit(1)

    getattr(ACTIONS[action], action)(**args, **configs)


if __name__ == "__main__":
    main()
