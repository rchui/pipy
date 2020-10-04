import re
import subprocess
from typing import Any

from setuptools import find_packages, setup


def _get_version_from_pkg_info() -> str:
    return re.search(r"^Version:\s+(\S+)", open("PKG-INFO", "r").read(), re.MULTILINE).group(1)


def _get_version_from_git_tag() -> Any:
    """Return a PEP440-compliant version derived from the git status.
    If that fails for any reason, return the first 7 chars of the changeset hash.
    """

    def _is_dirty() -> bool:
        try:
            subprocess.check_call(["git", "diff", "--quiet"])
            subprocess.check_call(["git", "diff", "--cached", "--quiet"])
            return False
        except subprocess.CalledProcessError:
            return True

    def _get_most_recent_tag() -> Any:
        return subprocess.check_output(["git", "describe", "--tags"]).strip().decode("utf-8")

    def _get_hash() -> Any:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")[:7]

    tag = _get_most_recent_tag()
    m = re.match(r"(?P<xyz>\d+\.\d+\.\d+)(?:-(?P<dev>\d+)+(?P<hash>.+))?", tag)

    version = m.group("xyz")
    if m.group("dev") or _is_dirty():
        version += ".dev{dev}+{hash}".format(dev=m.group("dev") or 0, hash=m.group("hash") or _get_hash())

    return version


def get_version() -> Any:
    try:
        return _get_version_from_pkg_info()
    except IOError:
        return _get_version_from_git_tag()


name = "pipy"
description = "Python library for consistent environments."
long_description = description
with open("requirements.txt", "r") as requirements_file:
    requirements = [line for line in requirements_file]

setup(
    author="Ryan Chui",
    author_email="ryan.w.chui@gmail.com",
    description=description,
    entry_points={"console_scripts": ["pipy=pipy:main"]},
    license="Apache 2.0",
    long_description=long_description,
    name=name,
    package_data={name: ["_/*/*"]},
    packages=find_packages(),
    py_modules=[],  # Add scripts as modules
    include_package_data=True,
    url="https://github.com/rchui/" + name,
    version=get_version(),
    install_requires=requirements,
    setup_requires=[],
)
