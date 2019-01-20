"""Description.

Usage paragraph.
"""

import threading
import time


class Process:
    """Blank process class, implemented in three distinct subclasses.

    This Process class is the base for the input-, middleware- and
    output process classes implemented in these module. It is
    recommended to build any implementation you desire on these
    three classes.
    """
    def __init__(self, logger):
        """Provide a lock for concurrent access to queues.
        """
        self._lock = threading.Lock()
        self._logger = logger

    def execution_loop(self):
        """To be implemented by subclasses.
        """
        raise NotImplementedError('To be implemented by subclasses')


# TODO: input process, to be expanded further.
class InputProcess(Process):
    """
    """
    def __init__(self, queue, logger):
        """
        """
        super().__init__(logger)

        #:
        self._queue = queue
        #:
        self._topic = None

    def _put_message(self, message):
        """
        """
        with self._lock:
            self._queue.put(message)
            # TODO: Catch full exception.

    @property
    def topic(self):
        return self._topic

    @topic.setter
    def topic(self, topic):
        # TODO: test if it is valid.
        self._topic = topic

    def execution_loop(self):
        """The main execution loop for an input process, to be 
        implemented by a subclass.
        
        Each subclass of the InputProcess should implement their own
        execution loop, which receives a Topic object and adds Message
        objects to the queue until interrupted.
        """
        raise NotImplementedError('To be implemented by subclasses')

# TODO: twitter input process.


# TODO: reddit process.


# TODO: blank middle-process.
class MiddlewareProcess(Process):
    """

    We only support one middleware layer as we do not do multi-core
    concurrency, meaning that splitting up a process without blocking
    API calls will not result any significant speedup.
    """
    def __init__(self, input_queue, output_queue, logger):
        """
        """
        self._input_queue = input_queue
        self._output_queue = output_queue
        super().__init__(logger)

    def _get_message(self):
        """
        """
        with self._lock:
            try:
                return self._input_queue.get(False)
            except self._input_queue.Empty:
                raise  self._input_queue.Empty

    def _put_message(self, message):
        """
        """
        with self._lock:
            self._output_queue.put(message)
            # TODO: Catch full exception.

    def process_message(self, message):
        """
        """
        return message

    def execution_loop(self):
        """
        """
        while True:
            try:
                message = self._get_message()
                message = self.process_message(message)
                self._put_message(message)
            except self._input_queue.Empty:
                time.sleep(1)


# TODO: sentiment middle-process.


def output_message(handler):
    """Coroutine to emit messages using handlers without creating threads.
    """
    while True:
        message = (yield)
        handler.emit(message)


class OutputProcess(Process):
    """
    """
    def __init__(self, queue, logger):
        """
        """
        self._queue = queue
        self._output_handlers = set()
        super().__init__(logger)

    def _get_message(self):
        """
        """
        with self._lock:
            try:
                return self._queue.get(False)
            except self._queue.Empty:
                raise  self._queue.Empty

    @property
    def handlers(self):
        return list(self._output_handlers)

    def add_handler(self, handler):
        if handler in self._output_handlers:
            pass
        else:
            self._output_handlers.add(handler)

    def delete_handler(self, handler):
        self._output_handlers.remove(handler)

    def execution_loop(self):
        """
        """
        # Set up coroutines for all handlers.
        handler_coroutines = [output_message(x) for x in self._output_handlers]

        # Get messages from the queue.
        while True:
            try:
                message = self._get_message()
                for coroutine in handler_coroutines:
                    coroutine.send(message)
            except self._queue.Empty:
                time.sleep(1)
