#!/usr/bin/env python3

import argparse
import sys

import toml

from pipy import packages, session
from pipy.utils import cli

ACTIONS = {"open": session, "close": session, "lock": packages, "install": packages, "sync": packages}


def main() -> None:

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--verbose", action="store_true", help="Enable verbbose output.")

    subparsers = parser.add_subparsers()

    open_parser = cli.add_action("open", subparsers, "Open an isolated python environment.")
    cli.version(open_parser)

    close_parser = cli.add_action("close", subparsers, "Close and delete python environment.")
    cli.version(close_parser)

    cli.add_action("lock", subparsers, "Lock environment packages.")

    install_parser = cli.add_action("install", subparsers, "Install a locked python environment.")
    cli.environment(install_parser)
    cli.version(install_parser)

    sync_parser = cli.add_action("sync", subparsers, "Sync a locked environment.")
    cli.environment(sync_parser)
    cli.version(sync_parser)

    with open("pyproject.toml", "r") as pyproject:
        project_configs = toml.loads(pyproject.read())

    if "tool" in project_configs and "pipy" in project_configs["tool"]:
        configs = {"name": project_configs["tool"]["pipy"]["name"]}
    else:
        print("No pyproject.toml found. Could not identify as a python project.", file=sys.stderr)
        sys.exit(1)

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
