import shlex
import subprocess
from typing import Any

import typer

from pipy import config


def log(output: str, context: str = config.defaults.project, err: bool = False, color: Any = typer.colors.BLUE) -> None:
    """Log output to the console."""
    typer.secho(f" >> [{context}] {output}", err=err, fg=color)


def run(command: str, context: str = config.defaults.project, check: bool = True, verbose: bool = True) -> None:
    """Run a shell command."""
    parts = shlex.split(command)
    if verbose:
        log(" ".join(parts), context=context)
    subprocess.run(command, shell=True, check=check)


def collect(command: str, context: str = config.defaults.project, check: bool = True, verbose: bool = True) -> str:
    """Collect the output of stdout from a shell comamnd."""
    parts = shlex.split(command)
    if verbose:
        log(" ".join(parts), context=context)

    response = subprocess.run(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=check)

    if response.stderr:
        log(response.stderr.decode(), context=context, err=True, color=typer.colors.RED)
        if check:
            raise typer.Exit(code=1)
    return response.stdout.decode().strip()
