"""
https://stackoverflow.com/questions/5849800/what-is-the-python-equivalent-of-matlabs-tic-and-toc-functions
"""
import time


class Timer:
    """Timer wrapper for evaluating"""
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    # noinspection PyShadowingBuiltins
    def __exit__(self, type, value, traceback):  # pylint: disable=redefined-builtin
        if self.name:
            print('[%s]' % self.name,)
        print('Elapsed: %s' % (time.time() - self.tstart))
