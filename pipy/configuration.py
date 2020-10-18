"""pipy's module for locking packages"""

import sys
from typing import Any, Dict, MutableMapping

import toml


def _validate(configs: MutableMapping[str, Any]) -> Dict[str, Any]:
    if "tool" not in configs or "pipy" not in configs["tool"]:
        print("No pyproject.toml found. Could not identify as a python project.", file=sys.stderr)
        sys.exit(1)

    return configs["tool"]["pipy"]


def _name(configs: Dict[str, Any]) -> str:
    return configs["name"]


def _aliases(configs: Dict[str, Any]) -> Dict[str, Any]:
    alias_configs = {alias["name"]: alias for alias in configs["aliases"]}
    if "setup" not in alias_configs:
        print(
            'Expected required alias "setup".'
            + ' Add to pyproject.toml:\n[[tool.pipy.aliases]]\nname = "setup"\ncommands = [...]'
        )
    return alias_configs


def parse() -> Dict[str, Any]:
    with open("pyproject.toml", "r") as file:
        file_configs = toml.loads(file.read())

    pyproject = _validate(file_configs)
    configs = {"name": _name(pyproject), "aliases": _aliases(pyproject)}

    return configs
