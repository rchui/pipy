"""pipy's module for running shell subprocesses."""

import os
import shlex
import subprocess
import sys
from typing import Optional


def which(program: str) -> Optional[str]:
    def is_exe(fpath: str) -> bool:
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def run(command: str, log: bool = True) -> None:
    """Run a command in a shell.

    Args:
        command (str): Command to execute.
        log (bool, optional): Log command. Defaults to True.
    """

    if log:
        print(" ".join(command.split()))
    response = subprocess.run(shlex.split(command))
    if response.returncode != 0:
        print()  # Stop colors from bleeding in CI
        sys.exit(response.returncode)


def collect(command: str, log: bool = True, fail: bool = True) -> str:
    """Run a command in a shell and collect the stdout.

    Args:
        command (str): Comamnd to execute.
        log (bool, optional): Log command. Defaults to True.

    Returns:
        str: Stdout from command.
    """

    if log:
        print(" ".join(command.split()))
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        if log:
            print(err.decode(), file=sys.stderr)
        if fail:
            sys.exit(1)
    return out.decode().strip()


def attempt(command: str, log: bool = True) -> None:
    try:
        collect(command, log=log)
    except:  # noqa
        pass
