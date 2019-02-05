"""process.py

This package provides utilities for running synchronous external processes.
"""

import os

from time import monotonic as _time
from subprocess import Popen, PIPE, TimeoutExpired, CalledProcessError


__all__ = ['run', 'run_process']


class CompletedProcessWrapper:

    def __init__(self, proc, start_time, end_time):
        self._proc = proc
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return repr(self._proc)

    @property
    def args(self):
        return self._proc.args

    @property
    def returncode(self):
        return self._proc.returncode

    @property
    def stdout_data(self):
        return self._proc.stdout

    @property
    def stderr_data(self):
        return self._proc.stderr


def run_process(*args, input=None):
    shell = os.name == 'nt'
    start_time = _time()
    cp = subprocess.run(
        args, input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=shell, bufsize=1, universal_newlines=True
    )
    end_time = _time()
    return CompletedProcessWrapper(cp, start_time, end_time)


def run(*args, input=None):
    proc = run_process(*args, input=input)
    return proc.stdout_data.decode('utf-8')

