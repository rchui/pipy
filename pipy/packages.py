"""pipy's module for locking packages"""

import sys
from itertools import chain
from typing import Any, Dict, List, Tuple

import hashin
import toml

from pipy import environment as docker
from pipy.utils import sh


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


def _get_includes(includes: List[str], environments: List[Dict[str, Any]]) -> List[str]:
    """Get all packages from all included environments.

    Args:
        includes (List[str]): Environments to also include.
        environments (List[Dict[str, Any]]): Other environments to check.

    Returns:
        List[str]: Packages to incldue from other environments.
    """

    packages: List[str] = []

    for include in includes:
        for other_environment in environments:
            if other_environment["name"] == include:
                packages = packages + other_environment["packages"]

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

            dependencies = sorted(
                set(environment["packages"] + _get_includes(environment.get("includes", []), environments))
            )

            requirements: List[Dict[str, Any]] = []
            for dependency in dependencies:
                if dependency in package_configurations:
                    print(f"    Locking: {dependency}")
                    requirements.append({"name": dependency, **package_configurations[dependency]})

            lock_configuration[environment["name"]][version] = {"packages": requirements}

    with open("pipy.lock.toml", "w+") as lock_file:
        lock_file.write(toml.dumps(lock_configuration))


def install(name: str, environment: str, version: str, verbose: bool) -> None:
    """Install a locked environment.

    Args:
        name (str): Name of the project being installed.
        environment (str): Name of the locked environment to install.
        version (str): Python version to lock environment with.
        verbose (bool): Verbose output.
    """

    print(f"Installing {name}'s Python {version} {environment} environment.")

    with open("pipy.lock.toml", "r") as lock_file:
        lock_configuration = toml.loads(lock_file.read())

    environment_configuration = lock_configuration.get(environment)
    if environment_configuration is None:
        print(
            f"{environment} is not a locked environment. Add to [[tool.pipy.environments]] and run: pipy lock",
            file=sys.stderr,
        )
        sys.exit(1)

    version_configuration = environment_configuration.get(version)
    if version_configuration is None:
        print(
            f"Python {version} is not a locked python version. Add version to [tool.pipy] and run: pipy lock",
            file=sys.stderr,
        )
        sys.exit(1)

    packages = (f"{package['name']}=={package['version']}" for package in version_configuration["packages"])

    sh.run(f"python -m pip install {' '.join(packages)}", log=verbose)
