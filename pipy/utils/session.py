import uuid
from contextlib import ContextDecorator
from pathlib import Path
from typing import Any

import docker
import typer

from pipy import config
from pipy.utils import sh


class Docker(ContextDecorator):
    def __init__(self, context: str = "pipy.session.docker") -> None:
        self.name = uuid.uuid4()
        self.client = docker.from_env()
        self.container: Any = None
        self.context = context

    def __enter__(self) -> "Docker":
        self.stop()
        self.start()
        return self

    def __exit__(self, *_: Any) -> None:
        self.stop()

    def start(self) -> "Docker":
        """Create and start a Docker container."""
        self.container = self.client.containers.create(
            "python:3.6",
            name=self.name,
            tty=True,
            detach=True,
            volumes={str(Path.cwd()): {"bind": config.defaults.workdir, "mode": "rw"}},
        )
        self.container.start()
        return self

    def stop(self) -> None:
        """Stop and remove a Docker container."""
        if self.container is not None:
            self.container.remove(v=True, force=True)

    def execute(self, command: str) -> "Docker":
        """Execute a command in a running Docker container."""
        sh.log(command, context=self.context)
        for stream in self.container.exec_run(command, stream=True, demux=False, workdir=config.defaults.workdir):
            if stream is not None:
                for line in stream:
                    sh.log(line.decode().strip(), context=self.context, color=typer.colors.YELLOW)
        return self
