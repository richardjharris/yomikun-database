import sys
import time

class Timer():
    def __init__(self):
        """
        Creates and starts a timer.
        """
        self.start_time = time.monotonic()
    
    def report(self, prefix_message):
        """
        Prints elapsed time to stderr, as "{prefix_message} in {seconds}" 
        """
        elapsed = time.monotonic() - self.start_time
        print(f'{prefix_message} in {elapsed:.0f}s', file=sys.stderr)