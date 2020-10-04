#!/usr/bin/env python3

import argparse
import sys

import toml

from pipy import environment, packages
from pipy.utils import cli

ACTIONS = {"open": environment, "close": environment, "lock": packages, "install": packages}
DEFAULT_VERSION = f"{sys.version_info[0]}.{sys.version_info[1]}"


def main() -> None:

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--verbose", action="store_true", help="Enable verbbose output.")

    subparsers = parser.add_subparsers()

    open_parser = cli.add_action("open", subparsers, "Open an isolated python environment.")
    open_parser.add_argument("version", type=str, help="Python version use in environment.")

    close_parser = cli.add_action("close", subparsers, "Close and delete python environment.")
    close_parser.add_argument("version", type=str, help="Python version of environment to close.")

    cli.add_action("lock", subparsers, "Lock environment packages.")

    install_parser = cli.add_action("install", subparsers, "Install a locked python environment.")
    install_parser.add_argument("environment", type=str, help="Locked pipy environment to install.")
    install_parser.add_argument(
        "--version",
        type=str,
        default=DEFAULT_VERSION,
        help=f"Python version to install with. Defaults to '{DEFAULT_VERSION}'.",
    )

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
