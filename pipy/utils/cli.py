"""pipy module for CLI methods."""

import argparse
import sys

DEFAULT_VERSION = f"{sys.version_info[0]}.{sys.version_info[1]}"


def add_category(category: str, subparsers: argparse._SubParsersAction, text: str) -> argparse._SubParsersAction:
    parser = subparsers.add_parser(category, help=text)
    parser.set_defaults(category=category)
    return parser.add_subparsers()


def add_action(action: str, subparser: argparse._SubParsersAction, text: str) -> argparse.ArgumentParser:
    parser = subparser.add_parser(action, help=text)
    parser.set_defaults(action=action)
    return parser


def environment(argparser: argparse.ArgumentParser) -> None:
    argparser.add_argument("environment", type=str, help="Locked pipy environment to use.")


def version(argparser: argparse.ArgumentParser) -> None:
    argparser.add_argument(
        "--version",
        type=str,
        default=DEFAULT_VERSION,
        help=f"Python version to use. Defaults to '{DEFAULT_VERSION}'.",
    )
