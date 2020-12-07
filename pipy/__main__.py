#!/usr/bin/env python3

import typer

from pipy.components import Pipeline

cli = typer.Typer()


@cli.command()
def test() -> None:
    with Pipeline(name="pipeline-1") as one:
        with one.step(name="start", image="python:3.6") as start:
            start.task("echo 'hello python'")
            start.task("sleep 1")
        with one.step(name="end", image="python:3.7") as end:
            end.task("git fetch --all")


@cli.command()
def start() -> None:
    pass


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
