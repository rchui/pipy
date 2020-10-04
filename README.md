# Pipy: Service Dependency Management for Python
Pipy helps you manage the entire life cycle of your Python service. It operates across development, testing, and production to create consistent, reproducible environments not matter what stage you are at.

## Introduction

`pipy` is installed using `pip`.

```bash
pip install pipy
```

You can create an isolated Python environment:

```bash
pipy open
```

You can lock an service's dependencies:

```bash
pipy lock
```

You can install packages from a locked environment:

```bash
pipy install dev
```

Or create the locked environment into a container:

```bash
pipy create dev
```

You can clean up a created environment:

```bash
pipy close
```

## Configuration

`pipy` uses the standardized `pyproject.toml` to handle declaring, managing, and installing Python dependencies.

```toml
[tool.pipy]
name = "pipy"
versions = ["3.6", "3.7"]  # Supports multiple python version locking.

[[tool.pipy.environments]]
name = "dev"  # Supports arbitrary environment naming.
packages = ["flake8"]

[[tool.pipy.environments]]
name = "prd"
includes = ['dev']  # Also install 'dev' packages
packages = ["black"]
```

## Purpose

`pipy` uses industry standard tools under the hood to create the isolated environments. Instead of virtual environments, `pipy` launches, pauses, and unpauses containers to create environments. To perform Python package dependency reoslution, it uses `pip`'s experimental 2020 dependency resolver to generate locked environments.

`pipy` is meant to replace `pipenv`, `poetry`, `virtualenv`, and `pyenv` for developing and deploying containerized Python services.
