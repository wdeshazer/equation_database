import inspect
import binascii

jpeg_signatures = [
    binascii.unhexlify(b'FFD8FFD8'),
    binascii.unhexlify(b'FFD8FFE0'),
    binascii.unhexlify(b'FFD8FFE1')
]

# JPEG Testing Example (https://www.geeksforgeeks.org/working-with-binary-data-in-python/)
# with open('food.jpeg', 'rb') as file:
#     first_four_bytes = file.read(4)
#
#     if first_four_bytes in jpeg_signatures:
#         print("JPEG detected.")
#     else:
#         print("File does not look like a JPEG.")

def called_func():
    return inspect.stack()[1][3]


def calling_func():
    return inspect.stack()[2][3]


import time


class TimerError(Exception):

    """A custom exception used to report errors in use of Timer class"""


class Timer:

    def __init__(self):

        self._start_time = None

    def start(self):

        """Start a new timer"""

        if self._start_time is not None:

            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self):

        """Stop the timer, and report the elapsed time"""

        if self._start_time is None:

            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time

        self._start_time = None

        print(f"Elapsed time: {elapsed_time:0.4f} seconds")
