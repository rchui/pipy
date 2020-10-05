"""pipy module for creating python environments"""

import os
import sys
from contextlib import ContextDecorator
from typing import Any

from typing_extensions import Literal

from pipy.utils import sh


def _docker() -> None:
    if sh.which("docker") is None:
        print("Could not find a usable 'docker' executable.", file=sys.stderr)
        sys.exit(1)


def close(name: str, version: str, verbose: bool = False) -> None:
    """Close and delete python environment.

    Args:
        name (str): Name of the project environment being closed.
        version (str): Version of the python environment being closed.
    """

    _docker()

    sh.attempt(f"docker stop pipy-{version}-{name}", log=verbose)


class Manager(ContextDecorator):
    def __init__(self, name: str, version: str, close: bool = False, verbose: bool = False) -> None:
        self.name = name
        self.version = version
        self.environment = f"pipy-{version}-{name}"

        self.close = close
        self.verbose = verbose

    def __enter__(self) -> "Manager":
        try:
            sh.collect(f"docker inspect {self.environment}", fail=True, log=self.verbose)
            sh.attempt(f"docker unpause {self.environment}", log=self.verbose)
        except:  # noqa
            cache_dir = sh.collect("pip cache dir", log=False)
            sh.collect(
                f"""docker run
                        --name {self.environment}
                        --interactive
                        --tty
                        --detach
                        --rm
                        --workdir /src
                        --volume {os.environ['PWD']}:/src
                        --volume /var/run/docker.sock:/var/run/docker.sock
                        --volume {cache_dir}:/root/.cache/pip
                        python:{self.version}
                """,
                log=self.verbose,
            )
        return self

    def __exit__(self, *_: Any) -> Literal[False]:
        if self.close:
            close(self.name, self.version, verbose=self.verbose)
        else:
            sh.collect(f"docker pause {self.environment}", log=self.verbose)
        return False


def _collect(name: str, version: str, command: str, verbose: bool) -> str:
    return sh.collect(f"docker exec --interactive --tty pipy-{version}-{name} {command}", log=verbose)


def _execute(name: str, version: str, command: str, verbose: bool) -> None:
    sh.run(f"docker exec --interactive --tty pipy-{version}-{name} {command}", log=verbose)


def open(name: str, version: str, verbose: bool = False) -> None:
    """Open an isolated python environment.

    Args:
        name (str): Name of the project environment is being started for.
        version (str): Python version of the environment to start.
    """

    _docker()

    with Manager(name, version, verbose=verbose):
        _execute(name, version, "bash", verbose)
