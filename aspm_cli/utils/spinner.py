import sys
import threading
import itertools
import time

class Spinner:
    def __init__(self, message="Processing..."):
        self.spinner = itertools.cycle(["|", "/", "-", "\\"])
        self.stop_running = False
        self.message = message
        self.thread = threading.Thread(target=self._spin)

    def _spin(self):
        while not self.stop_running:
            sys.stdout.write(f"\r{self.message} {next(self.spinner)}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")

    def start(self):
        self.stop_running = False
        self.thread.start()

    def stop(self):
        self.stop_running = True
        self.thread.join()
