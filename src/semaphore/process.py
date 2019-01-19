"""
"""

import threading
import time


class Process:
    """
    """
    def __init__(self):
        """
        """
        self._lock = threading.Lock()

    def execution_loop(self):
        """
        """
        raise NotImplementedError('To be implemented by subclasses.')


# TODO: blank middle-process.
class MiddlewareProcess(Process):
    """
    """
    def __init__(self, input_queue, output_queue):
        """
        """
        self._input_queue = input_queue
        self._output_queue = output_queue
        super().__init__()

    def get_message(self):
        """
        """
        with self._lock:
            try:
                return self._input_queue.get(False)
            except self._input_queue.Empty:
                raise  self._input_queue.Empty

    def put_message(self, message):
        """
        """
        with self._lock:
            self._output_queue.put(message)
            # TODO: Catch full exception.

    def process_message(self, message):
        """
        """
        raise NotImplementedError('To be implemented by subclasses.')

    def execution_loop(self):
        """
        """
        while True:
            try:
                message = self.get_message()
                message = self.process_message(message)
                self.put_message(message)
            except self._input_queue.Empty:
                time.sleep(1)


# TODO: sentiment middle-process.


# TODO: input process, to be expanded further.
class InputProcess(Process):
    """
    """
    def __init__(self, queue):
        """
        """
        self._queue = queue
        super().__init__()

    def put_message(self, message):
        """
        """
        with self._lock:
            self._queue.put(message)
            # TODO: Catch full exception.

    def execution_loop(self):
        """
        """
        raise NotImplementedError('To be implemented by subclasses.')

# TODO: twitter input process.


# TODO: reddit process.


def output_message(handler):
    """
    """
    while True:
        message = (yield)
        handler.emit(message)


class OutputProcess(Process):
    """
    """
    def __init__(self, queue, output_handlers):
        """
        """
        self._queue = queue
        self._output_handlers = output_handlers
        super().__init__()

    def get_message(self):
        """
        """
        with self._lock:
            try:
                return self._queue.get(False)
            except self._queue.Empty:
                raise  self._queue.Empty

    def execution_loop(self):
        """
        """
        # Set up coroutines for all handlers.
        handler_coroutines = [output_message(x) for x in self._output_handlers]

        # Get messages from the queue.
        while True:
            try:
                message = self.get_message()
                for coroutine in handler_coroutines:
                    coroutine.send(message)
            except self._queue.Empty:
                time.sleep(1)
