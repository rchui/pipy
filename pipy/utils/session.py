import uuid
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any

import docker

from pipy import config
from pipy.utils import sh


class Container(AbstractContextManager):
    def __init__(self, *, image: str, context: str = "pipy.session.container", verbose: bool = False) -> None:
        self.client = docker.from_env()
        self.container: Any = None
        self.context = context
        self.image = image
        self.name = uuid.uuid4()
        self.verbose = verbose

    def __enter__(self) -> "Container":
        self.start()
        return self

    def __exit__(self, *_: Any) -> None:
        self.stop()

    def start(self) -> "Container":
        """Create and start a Docker container."""
        sh.collect(
            f"docker run -idt --name {self.name} --rm -v {Path.cwd()}:{config.defaults.workdir}:rw {self.image}",
            context=self.context,
            verbose=self.verbose,
        )
        return self

    def stop(self) -> None:
        """Stop and remove a Docker container."""
        sh.collect(f"docker stop {self.name}", context=self.context, check=False, verbose=self.verbose)

    def execute(self, command: str) -> "Container":
        """Execute a command in a running Docker container."""
        if not self.verbose:
            sh.log(command, context=self.context)
        sh.run(
            f"docker exec -it -w {config.defaults.workdir} {self.name} {command}",
            context=self.context,
            verbose=self.verbose,
        )
        return self
