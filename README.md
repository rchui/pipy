# Pipy: Consistent Python Development Environments
`Pipy` helps you manage your python development environment and is meant to serve as a replacement to `virtualenv`. Instead of virtual environments, `pipy` launches, pauses, and unpauses containers to create isolated and reproducible development environments.

## Introduction

`pipy` is installed using `pip`.

```bash
pip install pipy
```

## Usage

To create an isolated Python environment:

```bash
pipy open
```

To clean up a created environment:

```bash
pipy close
```

## Configuration

`pipy` uses the standardized `pyproject.toml` to handle declaring, managing, and installing Python dependencies.

```toml
[tool.pipy]
name = "pipy"

[[tool.pipy.aliases]]
name = "setup"
commands = []  # Shell commands to execute to setup environment.
```

`pipy` expects a default alias `setup` to be pre-defined in order to setup the environments as they are created.
