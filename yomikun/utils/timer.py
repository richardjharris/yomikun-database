import sys
import time

class Timer():
    def __init__(self):
        """
        Creates and starts a timer.
        """
        self.start_time = time.monotonic()

    @property
    def elapsed(self) -> str:
        """
        Returns elapsed time in seconds, to one decimal point.
        """
        elapsed_secs = time.monotonic() - self.start_time
        return f'{elapsed_secs:.0f}'

    def report(self, prefix_message: str):
        """
        Prints elapsed time to stderr, as "{prefix_message} in {seconds}" 
        """
        print(f'{prefix_message} in {self.elapsed}s', file=sys.stderr)