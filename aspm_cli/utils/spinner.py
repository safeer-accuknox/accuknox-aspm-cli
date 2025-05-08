import sys
import threading
import itertools
import time
from colorama import Fore, init
import os

init(autoreset=True)

class Spinner:
    def __init__(self, message="Processing...", color=Fore.CYAN):
        self.spinner = itertools.cycle(["|", "/", "-", "\\"])
        self.stop_running = False
        self.message = message
        self.color = color
        self.thread = threading.Thread(target=self._spin)

    def _spin(self):
        last_update = time.time()  # Track last update time
        while not self.stop_running:
            # Print spinner updates every 10 seconds if in GitHub Actions, else every 0.1s
            if os.getenv("GITHUB_ACTIONS") == "true":
                if time.time() - last_update >= 10:
                    sys.stdout.write(f"\r{self.color}{self.message} {next(self.spinner)}")
                    sys.stdout.flush()
                    last_update = time.time()
            else:
                sys.stdout.write(f"\r{self.color}{self.message} {next(self.spinner)}")
                sys.stdout.flush()
                time.sleep(0.1)  # Faster updates in other environments
        sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")

    def start(self):
        self.stop_running = False
        self.thread.start()

    def stop(self):
        self.stop_running = True
        self.thread.join()
