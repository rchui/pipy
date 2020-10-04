"""pipy module for CLI methods."""

import argparse


def add_category(category: str, subparsers: argparse._SubParsersAction, text: str) -> argparse._SubParsersAction:
    parser = subparsers.add_parser(category, help=text)
    parser.set_defaults(category=category)
    return parser.add_subparsers()


def add_action(action: str, subparser: argparse._SubParsersAction, text: str) -> argparse.ArgumentParser:
    parser = subparser.add_parser(action, help=text)
    parser.set_defaults(action=action)
    return parser
