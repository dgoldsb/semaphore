"""Description.

Usage paragraph.
"""

import queue
import sys


class Message:
    def __init__(self):
        pass


class Semaphore:
    def __init__(self):
        #: Input processes
        self._input_processes = set()
        #: Output handlers, to be used in output proces
        self._output_handlers = set()
        #: Message queue
        self._input_queue = queue.Queue()
        self._output_queue = queue.Queue()

    def add_output_handler(self, handler):
        self._output_handlers.add(handler)

    def run(self):
        try:
            # Kick off concurrent processes.
            # TODO: Run all sources in different threads to let Python handle CPU time.
            pass
        except KeyboardInterrupt:
            sys.exit(0)
