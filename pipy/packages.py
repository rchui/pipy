"""pipy's module for locking packages"""

import sys
from itertools import chain
from typing import Any, Dict, List, Tuple

import hashin
import toml

from pipy import environment as docker


def _get_hashes(version: str, packages: List[Tuple[str, str]]) -> Dict[str, Any]:
    """Get the package hashes given a python version, the package name, and package version.

    Args:
        version (str): Python version to get hash for.
        packages (List[Tuple[str, str]]): Package name and package version.

    Returns:
        Dict[str, Any]: Package name mapped to package version and hashes.
    """

    package_configurations: Dict[str, Any] = {}

    for requirement_name, requirement_version in packages:
        print(f"  Locking: {requirement_name}=={requirement_version}")
        requirement_hashes = [
            hashes["hash"]
            for hashes in hashin.get_package_hashes(
                requirement_name, version=requirement_version, algorithm="sha512", python_versions=(version,)
            )["hashes"]
        ]
        package_configurations[requirement_name] = {"version": requirement_version, "hashes": requirement_hashes}

    return package_configurations


def _get_packages(name: str, version: str, dependencies: List[str], verbose: bool) -> List[Tuple[str, str]]:
    """Use pip to determine which package versions to lock to.

    Args:
        name (str): Name of the project being locked.
        version (str): Python version of the project being locked.
        dependencies (List[str]): List of packages to lock for the given Python version.

    Returns:
        List[Tuple[str, str]]:
            str: Package name
            str: Locked package version
    """

    with docker.Manager(name, version, close=True):
        docker._collect(name, version, "python -m pip install --upgrade pip", verbose)
        docker._collect(
            name,
            version,
            f"python -m pip install --upgrade --use-feature=2020-resolver {' '.join(dependencies)}",
            verbose,
        )
        requirements = docker._collect(name, version, "pip freeze --exclude-editable", verbose)

    packages: List[Tuple[str, str]] = []
    for requirement in requirements.splitlines():
        package_name, package_version = requirement.split("==")
        packages.append((package_name, package_version))
    return packages


def lock(name: str, verbose: bool = False) -> None:
    """Lock all environments and versions for the given project.

    Args:
        name (str): Name of the python project being locked.
    """

    with open("pyproject.toml", "r") as pyproject:
        project_configs = toml.loads(pyproject.read())

    if "environments" not in project_configs["tool"]["pipy"]:
        print("No environments found to lock. Add to [[tool.pipy.environments]] in pyproject.toml.", file=sys.stderr)
        sys.exit(1)
    elif "versions" not in project_configs["tool"]["pipy"]:
        print("No versions found to lock. Add to [tool.pipy] in pyproject.toml.", file=sys.stderr)
        sys.exit(1)

    environments = project_configs["tool"]["pipy"]["environments"]
    versions = project_configs["tool"]["pipy"]["versions"]

    name = f"{name}-lock"
    lock_configuration: Dict[str, Any] = {environment["name"]: {} for environment in environments}

    for version in versions:
        print(f"\nLocking packages for Python {version}:")

        dependencies = sorted(set(chain.from_iterable(environment["packages"] for environment in environments)))
        packages = _get_packages(name, version, dependencies, verbose)
        package_configurations = _get_hashes(version, packages)

        for environment in environments:
            print(f"\n  Locking {environment['name']} environment:")

            dependencies = environment["packages"]

            requirements: List[Dict[str, Any]] = []
            for dependency in dependencies:
                if dependency in package_configurations:
                    print(f"    Locking: {dependency}")
                    requirements.append({"name": dependency, **package_configurations[dependency]})

            lock_configuration[environment["name"]][version] = {"packages": requirements}

    with open("pipy.lock.toml", "w+") as lock_file:
        lock_file.write(toml.dumps(lock_configuration))
