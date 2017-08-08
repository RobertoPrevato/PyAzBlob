"""
Timer class, edited from: Python Cookbook, 3rd Edition by Brian K. Jones, David Beazley
"""
import time


class StopWatch:
    def __init__(self, func=time.perf_counter):
        self._elapsed_s = 0.0
        self._func = func
        self._start = None

    def start(self):
        if self._start is not None:
            raise RuntimeError("Already started")

        self._start = self._func()

    def stop(self):
        if self._start is None:
            raise RuntimeError("Not started")

        end = self._func()
        self._elapsed_s += end - self._start
        self._start = None

    def reset(self):
        self._elapsed_s = 0.0

    @property
    def elapsed_s(self):
        end = self._func()
        return end - self._start

    @property
    def elapsed_ms(self):
        if self.elapsed_s > 0.0:
            return self.elapsed_s * 1000
        return 0.0

    @property
    def running(self):
        return self._start is not None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()