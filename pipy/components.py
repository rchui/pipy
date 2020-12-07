from contextlib import AbstractContextManager
from typing import Any, Type

import typer

from pipy.exceptions import StepError, PipelineError
from pipy.utils import session, sh


class Step(AbstractContextManager):
    """A collection of tasks to execute as part of a pipeline."""

    def __init__(self, *, name: str, image: str, pipeline: "Pipeline", verbose: bool = False) -> None:
        self.name = name
        self.context = f"{pipeline.name}.{self.name}"
        self.verbose = verbose
        self.container = session.Container(image=image, context=self.context, verbose=self.verbose)

    def __enter__(self) -> "Step":
        sh.log(f"Step {self.name} started.", context=self.context, color=typer.colors.GREEN)
        self.container.start()
        return self

    def __exit__(self, exc_type: Type[BaseException], exc_val: Any, traceback: Any) -> None:
        self.container.stop()

        if exc_type is None:
            sh.log(f"Step {self.name} succeeded.", context=self.context, color=typer.colors.GREEN)
        else:
            sh.log(f"Step {self.name} failed.", context=self.context, color=typer.colors.RED)
            raise StepError(self.name)

    def task(self, command: str) -> "Step":
        """A task to execute as part of this step."""

        self.container.execute(command)
        return self


class Pipeline(AbstractContextManager):
    """A collection of steps to execute."""

    def __init__(self, *, name: str, verbose: bool = False) -> None:
        self.name = name
        self.context = self.name
        self.verbose = verbose

    def __enter__(self) -> "Pipeline":
        sh.log(f"Pipeline {self.name} started.", context=self.context, color=typer.colors.GREEN)
        return self

    def __exit__(self, exc_type: Type[BaseException], exc_val: Any, traceback: Any) -> None:
        if exc_type is None:
            sh.log(f"Pipeline {self.name} succeeded.", context=self.context, color=typer.colors.GREEN)
        else:
            sh.log(f"Pipeline {self.name} failed.", context=self.context, color=typer.colors.RED)
            raise PipelineError(self.name)

    def step(self, *, name: str, image: str, verbose: bool = False) -> Step:
        """A step to run as part of this pipeline.

        Args:
            name (str): Name of the step.
            image (str): Name of the image to execute the step inside of.
            verbose (bool, optional): Enable verbose logging. Defaults to False.
        """

        return Step(name=name, image=image, pipeline=self, verbose=verbose or self.verbose)
